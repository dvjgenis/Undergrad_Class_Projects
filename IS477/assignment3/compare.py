import pandas as pd

sql_data = pd.read_csv('results/sql-fac-types.csv')
pandas_data = pd.read_csv('results/pandas-fac-types.csv')

comparison = sql_data.compare(pandas_data)

comparison.to_csv('results/comparison.csv')