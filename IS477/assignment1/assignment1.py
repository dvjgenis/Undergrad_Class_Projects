import pandas as pd
import requests
import hashlib
import matplotlib.pyplot as plt
from datetime import datetime

with open('assignment1/fred_apikey.txt', 'r') as file:
    API_KEY = file.read().strip()

FRED_URL = f'https://api.stlouisfed.org/fred/series/observations?series_id=SP500&api_key={API_KEY}&file_type=json&observation_start=2019-01-01&observation_end=2024-01-01'

response = requests.get(FRED_URL)
data = response.json()


df = pd.DataFrame(data['observations'])[['date', 'value']]

df['value'] = pd.to_numeric(df['value'], errors='coerce')
df.dropna(inplace=True)

df.to_csv('assignment1/data/sp500.csv', index=False)

with open('assignment1/data/sp500.csv', 'r') as file:
    csv_data = file.read()

csv_data = csv_data.replace('\r\n', '\n').replace('\r', '\n')

with open('assignment1/data/sp500.csv', 'w') as file:
    file.write(csv_data)


df['date'] = pd.to_datetime(df['date'])
plt.figure(figsize=(10, 6))
plt.plot(df['date'], df['value'], label='S&P 500')
plt.title('S&P 500 Index Value (2019 - 2024)')
plt.xlabel('Date')
plt.ylabel('Index Value')
plt.grid(True)
plt.legend()

plt.savefig('assignment1/results/sp500.png')
plt.show()


with open('assignment1/data/sp500.csv', 'rb') as f:
    file_hash = hashlib.sha256(f.read()).hexdigest()

with open('assignment1/data/sp500.sha', 'w') as f:
    f.write(file_hash)


citation = f"""
@misc{{SP500,
    author = {{Federal Reserve Economic Data}},
    title = {{S&P 500 Index}},
    publisher = {{Federal Reserve Bank of St. Louis}},
    year = {{2024}},
    note = {{Retrieved on {datetime.today().strftime('%Y-%m-%d')}}},
    url = {{https://api.stlouisfed.org/fred/series/observations?series_id=SP500&api_key=apikey&file_type=json&observation_start=2019-01-01&observation_end=2024-01-01}}
}}
"""

with open('assignment1/data_citation.bib', 'w') as f:
    f.write(citation)