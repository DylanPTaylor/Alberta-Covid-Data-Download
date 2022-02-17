import json
import numpy as np
import pandas as pd
from jsonpath_ng import parse
import datetime

# Adding to this will make the clean_graph function return the data at the path, assuming the path is valid.
GRAPH_PARSING_EXPRESSIONS = [parse('$.layout.xaxis.title'),
                             parse('$.layout.xaxis.type'),
                             parse('$.layout.xaxis.categoryarray'),
                             parse('$.layout.yaxis.title'),
                             parse('$.layout.legend.title.text'),
                             parse('$.layout.annotations[*].text'),
                             parse('$.data[*].x'),
                             parse('$.data[*].y'),
                             parse('$.data[*].type'),
                             parse('$.data[*].name')]
# TBD
MAP_PARSING_EXPRESSIONS = None


"""
extract_raw_data deals with extracting all relevant JSON data, and does not filter any
invalid values like nulls, whitespace, or html non-sense
"""
def extract_raw_data(widgets):

    # Other entries in obj.text contain no or irrelevant data
    json_widgets = [json.loads(obj.text)['x'] for obj in widgets]

    # widgets seem to come in 1 of 2 types, based on the JSON object that describes them.
    graphs = [widget for widget in json_widgets if 'data' in widget.keys()]
    maps = [widget for widget in json_widgets if 'calls' in widget.keys()]

    for i, graph in enumerate(graphs):
        graphs[i] = clean_graph(graph)
    for i, map in enumerate(maps):
        maps[i] = clean_map(map)

    return np.array(graphs, dtype=object), np.array(maps)

def clean_graph(tag):

    # Fast, and potentially high reward
    for key in list(tag.keys()):
        if key not in ['layout', 'data']:
            del tag[key]

    extracted_items = []

    for expression in GRAPH_PARSING_EXPRESSIONS:
        for match in expression.find(tag):
            if match.value in ['', ' ']:
                continue
            else:
                extracted_items.append((str(match.full_path), match.value))

    return np.array(extracted_items, dtype=tuple)

def clean_map(tag):
    # Undecided what (if any) data from the maps I will use.
    # Could be used to visualize and compare different statistics by region.
    return {key: tag[key] for key in ['calls', 'limits']}


def partition_graphs(graphs):       
    columns = np.unique(np.concatenate([graph[:, 0] for graph in graphs]))[::-1]
    indicies = np.arange(len(graphs))

    df = pd.DataFrame([], columns=columns, index=indicies)
    df.index.name = 'Graphs'
    df.columns.name = 'Attributes:'
    
    for i, g in enumerate(graphs):
        series = pd.Series(g[:, 1], index=g[:, 0])

        series = series.reindex(series.index.sort_values()[::-1])
        series = series.reindex(df.columns)

        df.iloc[i] = series

    #TODO:
    #Clean individual values of html tags, handle NaN and nulls, trim whitespace, etc

    return df



"""
Param: silver
    A dataframe containing all the unstructured data contained in the graphs

Returns: gold
    A dataframe containing only time-dependant data, structured so that the first key is
    the graph name, and the second is the line name, and the third is the date.
    The data is dated from 2020-01-04 to datetime.datetime.today()
    
    E.G. to get the total active cases from October 1st, 2021 to January 5th 2022:
    gold['COVID-19 cases (n)']['Active']['2021-10-01':'2022-01-05']
"""

def build_date_driven_table(silver):
    #Get only the graphs the display values over time  
    temporal_graphs = silver.loc[silver['layout.xaxis.type'] == 'date']
    graph_titles = temporal_graphs['layout.yaxis.title']
    
    #Will need for indexing the data.
    x_data = temporal_graphs.filter(regex='^data\.\[.*\]\.x$')
    dates = dates_since(2020,1,4) #Earliest date for which the Govenment has data. 

    line_names = temporal_graphs.filter(regex='^data\.\[.*\]\.name$')
    line_names.index = graph_titles
    
    #Pair the graphs names with names of their lines 
    paired_names = line_names.apply(zip_graph_name_with_line_names, axis=1)
    hierarchical_columns = pd.MultiIndex.from_frame(pd.DataFrame(np.concatenate(paired_names), columns =['Graph','Line']))  

    y_data = temporal_graphs.filter(regex='^data\.\[.*\]\.y$')
    y_data.index = graph_titles
    
    golden_data = mine_gold(dates, x_data,y_data)
    
    gold = pd.DataFrame(np.transpose(golden_data), index=dates, columns=hierarchical_columns)

    return gold

def mine_gold(complete_dates, x_data, y_data):
    golden_data = []
    for i, graph_data in enumerate(y_data.iloc):        
        for j, line in enumerate(graph_data.dropna()):
            try:
                s = pd.Series(line, index = x_data.iloc[i].dropna()[j]) #Pair data with its dates
                s = s.reindex(complete_dates, method = 'pad', fill_value = 0)    #Forward fill missing data, replace NaN with 0
            except ValueError:
                s = pd.Series(np.zeros(len(complete_dates)))
            
            golden_data.append(s.values)    
    return golden_data
            
#my_train_wreck = lambda row: list(map((lambda e: (row.name,e)),row.dropna())) if not row.dropna().empty else [(row.name, row.name)]
def zip_graph_name_with_line_names(row):
    row_values = row.dropna()
    
    if not row_values.empty:
        mapped_tuples = map((lambda element: (row.name,element)), row_values)
        zipped_names = list(mapped_tuples)
    else:
        zipped_names = [(row.name, row.name)]
    
    return zipped_names
    
def dates_since(year,month,day):
    start_date = datetime.datetime(year, month, day)
    today = datetime.datetime.today()
    
    number_of_days = (today-start_date).days

    date_list = [str((start_date + datetime.timedelta(days = day)).date()) for day in range(number_of_days)]
    return list(date_list)