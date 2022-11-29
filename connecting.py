
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
contract = contract[contract['state'] == 2]
contract = contract.drop_duplicates(subset='response_id', keep='last').reset_index(drop=True)
resultat_method = resultat_method[resultat_method['lot_id'].isin(contract['lot_id'])]
#contract = contract.drop_duplicates('lot_id', keep='last').reset_index(drop=True)

#keep valid ones

resultat = resultat_method.merge(rel_db, left_on='id', right_on='resultat_method_id')
df = resultat.merge(specifications, left_on='specifications_id', right_on='id')