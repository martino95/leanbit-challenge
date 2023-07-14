from datetime import datetime, timedelta
from collections import OrderedDict
from holidays import country_holidays
from copy import deepcopy
from .JsonEncoder import *
from .utils import *
import sys

'''
   ### CLASSE PER LA GESTIONE DI PROGETTI PERIODI E SVILUPPATORI ###

   Consente di: caricare periodi, progetti e sviluppatori dai file json, 
   aggiungere vacanze per nazionalità, calcolare i giorni di ferie e di
   lavoro, stampare report di disponibilità su periodi e progetti, calcolare
   la fattibilità dei progetti (singolarmente e nell'insieme), distribuire
   i giorni di effort tra gli sviluppatori
'''


class Manager():



  def __init__(self):
    self.periods = []
    self.projects = []
    self.developers = []
    self.holidays = []
    self.tasks = []
    self.avail = False
    self.calendar = None
    
    
    
  def load_data_file(self,fn):
    try:
      with open(fn) as df: 
        self.data = json.load(df)
      if self.data.get('periods') != None:
        self.add_periods()
      if self.data.get('projects') != None:
        self.add_projects()
      if self.data.get('developers') != None:
        self.add_developers()
      if self.data.get('local_holidays') != None:
        self.add_local_holidays()
    except FileNotFoundError:
       print('file {} not found\n'.format(fn))
       sys.exit()
       
       
       
  def add_periods(self):
    if self.data.get('periods') == None:
      raise ValueError('Data file does not contain periods. Expected a periods list identified by the key "periods"')
    self.periods += [getperiod(pdict) for pdict in self.data['periods']]



  def add_projects(self):
    if self.data.get('projects') == None:
      raise ValueError('Data file does not contain projects. Expected a project list identified by the key "projects"')
    self.projects += [getproject(pdict) for pdict in self.data['projects']]



  def add_developers(self):
    if self.data.get('developers') == None:
      raise ValueError('Data file does not contain developers. Expected a developers list identified by the key "developers"')
    self.developers += [getdeveloper(ddict) for ddict in self.data['developers']]



  def add_country_holidays(self, country):
    sy = min([pe['since'].year for pe in self.periods]+[pe['since'].year for pe in self.projects])
    ey = max([pe['until'].year for pe in self.periods]+[pe['until'].year for pe in self.projects])
    yl = [y for y in range(sy,ey+1)]
    choli = [h for h in country_holidays(country, years=yl).keys()]
    self.holidays += choli
    for developer in self.developers:
      developer['holidays'] += choli
  
  
  
  def add_local_holidays(self):
    if self.data.get('local_holidays') == None:
      raise ValueError('Data file does not contain local holidays. Expected a local holidays list identified by the key "local_holidays"')
    else:
      localholidays = [datetime.strptime(lh['day'], '%Y-%m-%d').date()  for lh in self.data['local_holidays']]
      names = [lh['name'] for lh in self.data['local_holidays']]
      print('Local holidays: {} added\n'.format(names))
      self.holidays += localholidays
    for developer in self.developers:
      developer['holidays'] += localholidays
    
    
    
  def compute_availabilities(self):
    self.avail = True
    if self.periods != None:
      for pe in self.periods:
        pe['total_availability'] = 0
        pe['total_days'], pe['workdays'], pe['weekend_days'], pe['holidays'] = check_dates(pe['since'], pe['until'], self.holidays)
        pe['devel_avail']={}
        for dv in self.developers: 
          total, work, wend, holi = check_developer_availability(dv, pe)
          pe['devel_avail'][dv['id']] = {'total_days': total, 'workdays':work, 'weekend_days':wend, 'holidays':holi}
          pe['total_availability']+=work
    if self.projects != None:
      for pr in self.projects:
        pr['total_availability']=0
        pr['total_days'], pr['workdays'], pr['weekend_days'], pr['holidays'] = check_dates(pr['since'], pr['until'], self.holidays)
        pr['devel_avail']={}
        for dv in self.developers: 
          total, work, wend, holi = check_developer_availability(dv, pr)
          pr['devel_avail'][dv['id']] = {'total_days': total, 'workdays':work, 'weekend_days':wend, 'holidays':holi}
          pr['total_availability']+=work
        pr['feasibility'] = pr['total_availability'] >= pr['effort_days']
        pr['buffer_days'] = pr['total_availability'] - pr['effort_days']



  def get_period_report(self, outf):
    if not self.avail: 
      raise RequirementError('Availabilities not computed.')
    report_list=[]
    for pe in self.periods:
      report_list.append(NoIndent(OrderedDict([('period_id', pe['id']), 
  					('total_days', pe['total_days']), 
  					('workdays', pe['workdays']), 
  					('weekend_days', pe['weekend_days']), 
  					('holidays', pe['holidays'])
  					])))
    json_str = json.dumps({'availabilities': report_list}, indent=2, cls=MyEncoder)
    with open(outf, 'w+') as outfile: outfile.write(json_str)



  def get_devel_period_report(self,outf):
    if not self.avail: 
      raise RequirementError('Availabilities not computed.')
    report_list = []
    for pe in self.periods:
      for dv in self.developers: 
        report_list.append(NoIndent(OrderedDict([('developer_id', dv['id']), 
  				('period_id', pe['id']), 
  				('total_days', pe['devel_avail'][dv['id']]['total_days']), 
  				('workdays', pe['devel_avail'][dv['id']]['workdays']), 
  				('weekend_days', pe['devel_avail'][dv['id']]['weekend_days']), 
  				('holidays', pe['devel_avail'][dv['id']]['holidays'])
  				])))	
    json_str = json.dumps({'availabilities': report_list}, indent=2, cls=MyEncoder)
    with open(outf, "w+") as outfile: outfile.write(json_str)



  def get_feasibility_report(self,outf):
    if not self.avail: 
      raise RequirementError('Availabilities not computed.')
    report_list = []
    for pr in self.projects:
      report_list.append(NoIndent(OrderedDict([('project_id', pr['id']), 
  			('total_days', pr['total_days']), 
  			('workdays', pr['workdays']), 
  			('weekend_days', pr['weekend_days']), 
  			('holidays', pr['holidays']),
  			('feasibility', pr['feasibility'])
  			])))
    json_str = json.dumps({'availabilities': report_list}, indent=2, cls=MyEncoder)
    with open(outf, 'w+') as outfile: outfile.write(json_str)
    
    

  def get_calendar_json(self,outf):
    if self.calendar == None: 
      print('There is no calendar to print. Create one using distribute_effort.\n')
    else:
      calendar = deepcopy(self.calendar)
      for day in calendar:
        day['date'] = str(day['date'])
      json_str = json.dumps({'calendar': calendar}, indent=2, cls=MyEncoder)
      with open(outf, 'w+') as outfile: outfile.write(json_str)



  def get_calendar_html(self,outf):
    if self.calendar == None: 
      print('There is no calendar to print. Create one using distribute_effort.\n')
    else:
      outfile = open(outf, 'w+')
      outfile.write('''
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
</head>
<body><table cellspacing="0" cellpadding="2" border=""><tbody>
<tr><th>DATE</th>''')
      for dv in self.developers:
        outfile.write('<th>{}</th>'.format(dv['name']))
      outfile.write('</tr>\n')
      width = len(self.developers)+1
      first = True
      for day in self.calendar:
        if first:
          outfile.write('<tr><th colspan="{}">{}</th></tr>\n'.format(width, day['date'].strftime('%B')))
          first=False
        elif day['date'].day ==1:
          outfile.write('<tr><th colspan="{}">{}</th></tr>\n'.format(width, day['date'].strftime('%B')))
        outfile.write('<tr><td>{}</td>'.format(day['date']))
        for dv in self.developers:
          name = dv['name']
          if day[name]=='holiday': outfile.write('<td bgcolor="LightGreen">holiday</td>')
          elif day[name]=='weekend': outfile.write('<td bgcolor="GreenYellow">weekend</td>')
          elif day[name]==None:
            outfile.write('<td bgcolor="Gainsboro">available</td>')
          else:
            outfile.write('<td bgcolor="{}">project {} </td>'.format(colorlist[day[name]],day[name]))
        outfile.write('</tr>\n')
      outfile.write('</tbody></table></body></html>')


  
  def check_plan_feasibility(self):
    start, end = min([pr['since'] for pr in self.projects]), max([pr['until'] for pr in self.projects])      
    total_avail_days = sum([check_dates(start, end, dv['holidays'])[1] for dv in self.developers])
    total_effort_days = sum([pr['effort_days'] for pr in self.projects])    
    feasible = False
    force = None
    if not self.avail: 
      raise RequirementError('Availabilities not computed')
    elif any([not pr['feasibility'] for pr in self.projects]):
      unfeasible = [pr['id'] for pr in self.projects if not pr['feasibility'] ]
      print('Can\'t distribute effort. Project(s) {} is (are) not feasible: effort days are more than the workdays available in the period assigned\n'.format(unfeasible))
    else:
      if total_avail_days < total_effort_days:
        print('Projects are individually feasible, but aren\'t feasible togheter: total effort days needed exceed total available workdays\n')
      else:
        feasible = True
    if not feasible:
        force = input('Do you want to generate an effort distribution anyway? (y/n) ')
        print()
    if force == 'y':
        feasible = True
    return feasible, start, end, total_effort_days, total_avail_days



  def distribute_effort(self):
    if not self.projects: print('There are no projects!')
    elif not self.avail: 
      print('Availabilities not computed')
    else:
      feasible, start, end, total_effort_days, total_avail_days = self.check_plan_feasibility()
      if feasible:
        sortprj = deepcopy(self.projects)
        for pr in sortprj:
          pr['effort_days_left'] = pr['effort_days']
        sortprj.sort(key=flexibility)
        self.calendar = []
        for dat in daterange(start, end):
          daytasks = {'date': dat}
          for dv in self.developers:
            daytasks[dv['name']]= None
            if dat in dv['holidays']:
              daytasks[dv['name']]= 'holiday'
            elif dat.weekday()>=5:
              daytasks[dv['name']]= 'weekend'
            else:
              for pr in sortprj:
                if pr['effort_days_left']>0 and (dat>=pr['since'] and dat<=pr['until']):
                  daytasks[dv['name']] = pr['id']
                  pr['effort_days_left'] -= 1
                  assigned = pr['id']
                  break
              for pr in sortprj:
                if pr['id'] != assigned and pr['effort_days_left']>0 and (dat>=pr['since'] and dat<=pr['until']):
                  pr['buffer_days'] -=1
              sortprj.sort(key=flexibility)
          self.calendar.append(daytasks)
        sortprj.sort(key = lambda pr: pr['id'])
        welldone = True    
        for pr in sortprj:
          if pr['effort_days_left']==0: 
            print('Project {} effort was completely distributed\n'.format(pr['id']))
          else: 
            tot = pr['effort_days']
            distr = pr['effort_days']-pr['effort_days_left']
            percent = round(distr/tot*100)
            print('Project {} effort hasn\'t been completely distributed.\nIt was possible to distribute only {} effort days out of {} ({}% of the total)\n'.format(pr['id'],distr,tot,percent))
            welldone = False      
        if welldone == False:
          print('It wasn\'t possible to distribute the effort of all projects completely. This is due to excessive overlap of project periods and lack of flexibility of the schedule provided. Consider to spread your project more evenly in time or widen their time windows, anticipating their starting date or postponing their ending date.\n')
    
    
      
      
      
      
      
      
      
      
        
      

