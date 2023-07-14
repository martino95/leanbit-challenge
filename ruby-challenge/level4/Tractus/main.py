from .Manager import Manager
from .avail_countries import avail_countries
import sys




def main(filename):
  manager = Manager()
  manager.load_data_file(filename)
  manager.compute_availabilities()
  quit = False
  while quit==False:
    print('What do you want to do?')
    print('hl = add holidays by country')
    print('pr = get a general report on workdays and holidays in the given periods, in json format')
    print('dr = get a report on workdays and holidays in the given periods detailed for every given developer, in json format')
    print('fr = get a report evaluating the feasibility of the given projects, in json format')
    print('de = try to distribute di effort days of the given projects between developers')
    print('cj = get a calendar in json format (requires de before)')
    print('ch = get a calendar in html format (requires de before)')
    print('q  = quit')
    arg = input()
    if arg == 'q': quit = True
    elif arg == 'hl':
      print('Enter a country code. Type b to go back. For a list of country codes available type "list"')
      code = input()
      go = True
      while go:
        if code == 'list':
          print(avail_countries)
          print('Enter a country code.')
          code = input()
        if code == 'b': go = False
        try:
          manager.add_country_holidays(code)
          print('holidays added')
          go = False
        except: 
          print('Enter a valid country code. Type b to go back. For a list of country codes available type "list"')
          code = input()
      manager.compute_availabilities()
      print() 
    elif arg == 'pr':
      fn = input('type outfile name (without extension) ')+'.json'
      manager.get_period_report(fn)
    elif arg == 'dr':
      fn = input('type outfile name (without extension) ')+'.json'
      manager.get_devel_period_report(fn)
    elif arg == 'fr':
      fn = input('type outfile name (without extension) ')+'.json'
      manager.get_feasibility_report(fn)
    elif arg == 'de':
      manager.distribute_effort()
    elif arg == 'cj':
      fn = input('type outfile name (without extension) ')+'.json'
      manager.get_calendar_json(fn)
    elif arg == 'ch':
      fn = input('type outfile name (without extension) ')+'.html'
      manager.get_calendar_html(fn)
    
  sys.exit()
    
    

  manager.add_country_holidays('IT')
  manager.compute_availabilities()

  manager.get_calendar_html('calendar.html')
  
