import pandas as pd
import numpy as np

data_path = 'data_dx'

names = ['']

def load_data():

    for name in names:  
        globals()[name] = pd.read_csv(data_path+name+'.dat')
