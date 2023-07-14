from datetime import datetime, timedelta
from collections import OrderedDict
from holidays import country_holidays
from copy import deepcopy
from .JsonEncoder import *
import sys




colorlist = ['LightCoral','Khaki','Thistle','PaleTurquoise','BurlyWood','RosyBrown','peachpuff,','LightSalmon','HotPink','mediumslateblue']




class RequirementError(Exception):
  #Emerge quando funzione viene eseguita senza alcuni prerequisiti.
  pass




def daterange(start, end):
  dr = [start + timedelta(days=n) for n in range((end-start).days+1)]
  return dr




def check_dates(start, end, holidays):
  work, wend, holi = 0, 0, 0
  total = (end-start).days+1
  dates = daterange(start, end)
  for d in dates:
    iswend, isholi = d.weekday()>4, d in holidays
    work, wend, holi =  work + (not(iswend or isholi)), wend + iswend, holi + (isholi and not iswend)
  return total, work, wend, holi




def check_developer_availability(developer, period):
    total, work, wend, holi = check_dates(period['since'], period['until'], developer['holidays'])
    return total, work, wend, holi




def flexibility(pr):
  return pr['buffer_days']/(pr['effort_days']+0.1)
  



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
    start = datetime.strptime(pdict['since'], '%Y-%m-%d').date()
  if pdict.get('until') == None:
    raise ValueError('Every period must have a starting date, identified by the key "until"')
  else: 
    end = datetime.strptime(pdict['until'], '%Y-%m-%d').date()
  if (end-start).days < 0:
     raise ValueError('Ending date of period {} precedes its starting date'.format(idx))
  period = {'id':idx,'since': start, 'until':end}
  return period




def getproject(pdict):
  project = getperiod(pdict)
  if pdict.get('effort_days') == None:
    raise ValueError('Every project must have an assigned number of effort days')
  else:
    project['effort_days']=pdict['effort_days']
  return project




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
    print('You provided a birthday for {}\'s (id {}). It will be automatically set as free \n'.format(name, idx))
    birthday  =  datetime.strptime(ddict['birthday'], '%Y-%m-%d').date()
    allbirthdays = [birthday.replace(year=y) for y in range(birthday.year,birthday.year+100) ]
    developer['holidays']+=allbirthdays
  return developer






