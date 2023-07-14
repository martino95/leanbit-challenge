from datetime import datetime, timedelta
from collections import OrderedDict
from JsonEncoder import *
from holidays import country_holidays


def check_dates(start, end, holidays):
  work, wend, holi = 0, 0, 0
  total = (end-start).days+1
  dates = [start.date() + timedelta(days=n) for n in range(total)]
  for d in dates:
    iswend, isholi = d.weekday()>4, d in holidays
    work, wend, holi =  work + (not(iswend or isholi)), wend + iswend, holi + (isholi and not iswend)
  return total, work, wend, holi

def check_developer_availability(developer, period):
    total, work, wend, holi = check_dates(period['since'], period['until'], developer['holidays'])
    return total, work, wend, holi
    
def getperiod(pdict):
  if pdict.get('id') == None:
    raise ValueError('Every period must have an id')
  elif type(pdict['id']) != int:
    raise TypeError('Period ids must be integer values')
  else:
    idx = pdict['id']
  if pdict.get('since') == None:
    raise ValueError('Every period must have a starting date, identified by the key "since"')
  else:
    start = datetime.strptime(pdict['since'], '%Y-%m-%d')
  if pdict.get('until') == None:
    raise ValueError('Every period must have a starting date, identified by the key "until"')
  else: 
    end = datetime.strptime(pdict['until'], '%Y-%m-%d')
  if (end-start).days < 0:
     raise ValueError('Ending date of period {} precedes its starting date'.format(idx))
  period = OrderedDict({'id':idx,'since': start, 'until':end})
  return period

def getdeveloper(ddict):
  if ddict.get('id') == None:
    raise ValueError('Every developer must have an id')
  elif type(ddict['id']) != int:
    raise TypeError('Developer ids must be integer values')
  else: 
    idx = ddict['id']
  if ddict.get('name') == None:
    raise ValueError('You forgot developer {} name.'.format(idx))
  else:
    name = ddict['name']
  developer = OrderedDict({'id':idx,'name': name, 'holidays': []})
  if ddict.get('birthday') == None:
    print('You haven\'t provided {}\'s (id {}) birthday. Insert it if he wants he\'s bithday free!'.format(name, idx))
  else:
    print('You provided a birthday for {}\'s (id {}). It will be automatically set as free'.format(name, idx))
    birthday  =  datetime.strptime(ddict['birthday'], '%Y-%m-%d').date()
    allbirthdays = [birthday.replace(year=y) for y in range(birthday.year,birthday.year+100) ]
    developer['holidays']+=allbirthdays

  return developer



class Manager():

  def __init__(self):
    self.periods = []
    self.developers = []
    self.holidays = []
    
  def load_data_file(self,fn):
    with open(fn) as df: 
      self.data = json.load(df)
    if self.data.get('periods') != None:
      self.add_periods()
    if self.data.get('developers') != None:
      self.add_developers()
    if self.data.get('local_holidays') != None:
      self.add_local_holidays()
      
  def add_periods(self):
    if self.data.get('periods') == None:
      raise ValueError('Data file does not contain periods. Expected a periods list identified by the key "periods"')
    self.periods += [getperiod(pdict) for pdict in self.data['periods']]
  
  def add_developers(self):
    if self.data.get('developers') == None:
      raise ValueError('Data file does not contain developers. Expected a developers list identified by the key "developers"')
    self.developers += [getdeveloper(ddict) for ddict in self.data['developers']]

  def add_country_holidays(self, country):
    sy = min([p['since'].year for p in self.periods])
    ey = max([p['until'].year for p in self.periods])
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
      print('Local holidays: {} added'.format(names))
      self.holidays += localholidays
    for developer in self.developers:
      developer['holidays'] += localholidays
    
    
  def get_workdays_report(self, outf):
    report_list=[]
    for period in self.periods:
      total, work, wend, holi = check_dates(period['since'], period['until'], self.holidays)
      report_list.append(NoIndent(OrderedDict([('period_id', period['id']), 
  					('total_days', total), 
  					('workdays', work), 
  					('weekend_days', wend), 
  					('holidays', holi)
  					])))
    json_str = json.dumps({'availabilities': report_list}, indent=2, cls=MyEncoder)
    with open(outf, 'w') as outfile: outfile.write(json_str)


  def get_devel_avail_report(self,outf):
    report_list = []
    for period in self.periods:
      for devel in self.developers: 
        total, work, wend, holi = check_developer_availability(devel, period)
        report_list.append(NoIndent(OrderedDict([('developer_id', devel['id']), 
  				('period_id', period['id']), 
  				('total_days', total), 
  				('workdays', work), 
  				('weekend_days', wend), 
  				('holidays', holi)
  				])))	
    json_str = json.dumps({'availabilities': report_list}, indent=2, cls=MyEncoder)
    with open(outf, "w") as outfile: outfile.write(json_str)









