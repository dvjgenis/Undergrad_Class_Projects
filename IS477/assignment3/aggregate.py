import pandas as pd

data = pd.read_csv('input/Food_Inspections_50k.csv')

result = data.groupby('Facility Type').size().reset_index(name='Count')

result = result.sort_values('Facility Type')

result.to_csv('results/pandas-fac-types.csv', index=False)