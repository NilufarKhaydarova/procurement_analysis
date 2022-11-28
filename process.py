import pandas as pd
import numpy as np
from dictionary import *
from connecting import df

#process vendor_terr


def vendor_terr_process(df):

    df['vendor_terr'] = df['vendor_terr'].fillna(0)
    #turn float into int
    df['vendor_terr'] = df['vendor_terr'].astype(int)
    
    #add 1700000 to all values
    df['vendor_terr'] = df['vendor_terr'] + 1700000

    #drop any row with 1700000
    df = df.drop(df[df['vendor_terr'] == 1700000].index)

    #only keep first 4 digits
    df['vendor_terr'] = df['vendor_terr'].astype(str).str[:4]

    #turn into int
    df['vendor_terr'] = df['vendor_terr'].astype(int)

    df = df.drop(df[df['vendor_terr'] == 1701].index)

    df['region_name'] = df['vendor_terr'].map(terr_dict)

    return df

def contract_dat_process(df):
    #process contract_dat
    df['contract_dat'] = pd.to_datetime(df['contract_dat'], format='%Y-%m-%d')
    df['month'] = df['contract_dat'].dt.month
    df['year'] = df['contract_dat'].dt.year

    #remove nan values
    df = df.drop(df[df['month'].isna()].index)
    df = df.drop(df[df['year'].isna()].index)

    
    df['month'] = df['month'].map(month_dict)

    return df

def proc_id_process(df):
    df['proc_id'] = df['proc_id'].map(proc_dict)
    return df

def vendor_ter_counts(df):
    counts = df['vendor_terr'].value_counts()
    df['counts'] = df['vendor_terr'].map(counts)
    return df

def etp_process(df):
    df['etp_id'] = df['etp_id'].map(etp_dict)
    return df

def process(df):

    df = vendor_terr_process(df)
    df = contract_dat_process(df)
    df = proc_id_process(df)
    df = vendor_ter_counts(df)
    df = etp_process(df)
    return df

df = process(df)    
