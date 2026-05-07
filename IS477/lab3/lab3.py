import json
import requests
import pandas as pd
import hashlib

# 3. Reading Your API Key
with open('lab3/fred_apikey.txt', "r") as f:
    apikey = f.readline().strip()
print(apikey)

# 4. Dow Jones Industrial Average (DJIA)
series = "DJIA"
start = "2019-01-01"
end = "2023-01-01"
url = (f"https://api.stlouisfed.org/fred/series/observations?"
      f"series_id={series}&api_key={apikey}"
      f"&observation_start={start}&observation_end={end}&file_type=json")

response = requests.get(url)
response.raise_for_status()

#5. Working with JSON Data
json_data = response.json()

with open("lab3/djia.json", "w") as f:
    f.write(json.dumps(json_data, indent=4))

# 6. Reading JSON data in Pandas
df = pd.json_normalize(json_data, 'observations')

print(df.head())
print(df.dtypes)

df = df.drop(["realtime_start", "realtime_end"], axis=1)

df = df[df.value != "."]

df["date"] = pd.to_datetime(df["date"])
df["value"] = pd.to_numeric(df["value"])

# Plot the Index
df = df.set_index(["date"])
plt = df.plot(title="DJIA (2019-2023)", legend=False)
plt.set_xlabel("Date")
plt.set_ylabel("Index Value")
plt.get_figure().savefig("lab3/djia.png")

df.to_csv("lab3/djia.csv")

with open("lab3/djia.csv", "rb") as f:
    data = f.read()
    sha256hash = hashlib.sha256(data).hexdigest()

with open("lab3/djia.sha", "w") as f:
    f.write(sha256hash)