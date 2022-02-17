from bs4 import BeautifulSoup
import requests as req     
import pandas as pd

def get_site_data():
    raw_html = req.get(
        "https://www.alberta.ca/stats/covid-19-alberta-statistics.htm")

    html_soup = BeautifulSoup(raw_html.text, 'lxml')

    widgets = html_soup.find_all(lambda tag:
                                tag.name == 'script'
                                and 'data-for' in tag.attrs
                                and tag.attrs['data-for'].startswith('htmlwidget-'))

    # NOTE: Not all table class attributes start with 'table', but all contain it
    
    tables = html_soup.find_all(lambda tag:
                                tag.name == 'table'
                                and 'class' in tag.attrs
                                and 'table' in tag.attrs['class'])

    return widgets, tables