from Cleaners import *
from Scraper import get_site_data
 
widgets, tables = get_site_data()
 
bronze, maps = extract_raw_data(widgets)

silver = partition_graphs(bronze)

gold = build_date_driven_table(silver)

gold.to_csv('Covid_over_time.csv')
#pd.to_pickle draws maps?
