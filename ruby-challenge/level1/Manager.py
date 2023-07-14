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

class Manager():

  def __init__(self):
    self.periods = []
    self.holidays = []
  
  def load_data_file(self,fn):
    with open(fn) as df: 
      self.data = json.load(df)
    if self.data.get('periods') != None:
      self.add_periods()
      
  def add_periods(self):
    if self.data.get('periods') == None:
      raise ValueError('Data file does not contain periods. Expected a periods list identified by the key "periods"')
    self.periods += [getperiod(pdict) for pdict in self.data['periods']]
    
  def add_country_holidays(self, country):
    sy = min([p['since'].year for p in self.periods])
    ey = max([p['until'].year for p in self.periods])
    yl = [y for y in range(sy,ey+1)]
    self.holidays += [h for h in country_holidays(country, years=yl).keys()]


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




