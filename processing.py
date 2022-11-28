from sqlalchemy import create_engine
from decouple import config
import pandas as pd
import numpy as np


password = config('PASSWORD')

 
#connect to database
engine = create_engine(f'postgresql://postgres:{password}@localhost:5433/dxmapdb')
#authentication
conn = engine.connect()

resultat_method = pd.read_sql_table('resultat_method', conn)
rel_db = pd.read_sql_table('resultat_method_specifications', conn)
specifications = pd.read_sql_table('specifications', conn)

#contract
contract = pd.read_sql_table('contract_info', conn) 

#only keep state = 2

contract = contract[contract['lot_id'].isin(resultat_method['lot_id'])]
contract = contract[contract['state'] == 2]
contract = contract.drop_duplicates(subset='response_id', keep='last').reset_index(drop=True)
#contract = contract.drop_duplicates('lot_id', keep='last').reset_index(drop=True)

#keep valid ones

resultat = resultat_method.merge(rel_db, left_on='id', right_on='resultat_method_id')
df = resultat.merge(specifications, left_on='specifications_id', right_on='id')

df = df.merge(contract, left_on='lot_id', right_on='lot_id', how='inner')

df.info()

print(df.proc_id.value_counts())
#process vendor data
terr_dict = {
    1703: 'Andijon viloyati',
    1706: 'Buxoro viloyati',
    1730: 'Farg\‘ona viloyati',
    1708: 'Jizzax viloyati',
    1735: 'Qoraqalpog\‘iston Respublikasi',
    1710: 'Qashqadaryo viloyati',
    1733: 'Xorazm viloyati',
    1714: 'Namangan viloyati',
    1712: 'Navoiy viloyati',
    1718: 'Samarqand viloyati',
    1724: 'Sirdaryo viloyati',
    1722: 'Surxondaryo viloyati',
    1726: 'Toshkent shahri',
    1727: 'Toshkent viloyati'
}
df['vendor_terr'] = df['vendor_terr'] + 1700000
df = df[df.vendor_terr != 1700000]
df.vendor_terr = df.vendor_terr[df.vendor_terr.astype(str).str.len() == 4]
df.vendor_terr = df.vendor_terr.astype(str)
df['region_name'] = df['vendor_terr'].map(terr_dict)


#data
df = pd.read_csv('data/dashboard_df.csv', sep=',')
df['contract_dat'] = pd.to_datetime(df['contract_dat'])
df['contract_dat'] = df['contract_dat'].dt.strftime('%Y-%m-%d')
df['contract_dat'] = pd.to_datetime(df['contract_dat'])

#columnss
vendor_terr = df['vendor_terr'].unique()
contract_dat = pd.to_datetime(df['contract_dat'])
month_dict = {1: 'Январь', 2:'Февраль', 3:'Март', 4:'Апрель', 5:'Май', 6:'Июнь', 7:'Июль', 8:'Август', 9:'Сентябрь', 10:'Октябрь', 11:'Ноябрь', 12:'Декабрь'}
months = contract_dat.dt.month.unique()
months_names = [month_dict[elem] for elem in months]

df['month'] = df['contract_dat'].dt.month
df['month'] = df['month'].apply(lambda x: month_dict[x])

df['year'] = df['contract_dat'].dt.year



#some preprocessing
counts = df.vendor_terr.value_counts()  
counts = counts.reset_index()

df['counts'] = df['vendor_terr'].map(counts.set_index('index')['vendor_terr'])

