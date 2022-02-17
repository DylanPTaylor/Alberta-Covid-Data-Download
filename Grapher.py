import sys
from traceback import print_list
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

data = pd.read_csv(sys.argv[1], header=[0,1], index_col=0)
graphs = np.sort(list(set(data.columns.get_level_values(0))))

while True:
    print('\nSelect a graph to view:')
    print(*[str(i+1)+' '+str(g) for i,g in enumerate(graphs)], sep='\n') 
    
    requested_graph = int(input('> ')) - 1
    
    line_names = np.array(data[graphs[requested_graph]].columns)

    print('\nSelect the lines to view: (as a comma seperated list)')
    print(*[str(i+1)+' '+str(l) for i,l in enumerate(line_names)], sep='\n') 
    requested_lines =  np.apply_along_axis(lambda x: x-1, 0, np.array(input('> ').split(','), dtype=int)) 
    
    