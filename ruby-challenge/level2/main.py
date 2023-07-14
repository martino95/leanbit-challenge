from Manager import Manager


def main():
  manager = Manager()
  manager.load_data_file('data.json')
  manager.add_country_holidays('IT')
  manager.get_devel_avail_report('output.json')
  
  
if __name__ == '__main__':
  main()

  			
	



 
  
  
