import pandas as pd
import datetime
from datetime import datetime
from datetime import timedelta
import numpy as np
import hmac
import hashlib


# Reading and Writing Files
df = pd.read_csv('lab2/private_data.csv', sep='|')
df.to_csv('lab2/deidentified_data.csv')


# Inspecting your data | Suppression
df = df.drop(columns=['name', 'phone'])
print(df.head())


# Generalization
print("Generalize address to 5-digit ZIP Code and drop the address field")
df["zip"] = df["address"].str[-5:]
# df["zip"] = df["address"].str.split(' ').str[-1]
df.drop(columns="address", inplace=True)
print(df.head())


# Perturbation
print("\nConvert the birthdate to age and perturb by +1-3 years")

study_date = datetime(2024, 1, 1)

np.random.seed(123)
random_years = np.random.randint(low=1, high=4, size=100)

df["age"] = round((study_date - pd.to_datetime(df["birthdate"]))/timedelta(365)) + random_years
df.drop(columns="birthdate", inplace=True)
print(df.head())


# Pseudonymization
with open("lab2/secret.txt") as f:
    secret_key = f.readline().strip()

secret_key = '123abc'
message = 'my private data'

df["id"] = df["ssn"].apply(
    lambda x: hmac.new(
        bytes(secret_key, 'latin-1'),
        msg=bytes(x, 'latin-1'),
        digestmod=hashlib.sha256
    ).hexdigest()
)

df.drop(columns="ssn", inplace=True)

print(df.head())


# Saving the De-identified/Anonymized Data
df.to_csv("lab2/deidentified_data.csv")