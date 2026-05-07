"""
Script adapted from: https://fairmlbook.org/code/adult.html

The purpose of this script is to implement a standard logistic regression model
training on the UCI Adult to compare to the results reported in the paper.

  Ding, F., Hardt, M., Miller, J., & Schmidt, L. (2021).
  Retiring Adult: New Datasets for Fair Machine Learning.
  Advances in Neural Information Processing Systems, 34, 6478–6490.

This example uses the Adult dataset including the original train/test split
available from:

  Becker, Barry and Kohavi, Ronny. (1996). Adult.
  UCI Machine Learning Repository.
  https://doi.org/10.24432/C5XW20.

"""
import pandas as pd
import numpy as np
import os
from utils import run_regression

# Field names as specified in adult.names
columns = ["age", "workclass", "fnlwgt", "education", "education-num",
            "marital-status", "occupation", "relationship", "race", "sex",
            "capital-gain", "capital-loss", "hours-per-week", "native-country",
            "income"]

# Read the training and test data into their respective data frames
orig_train_data = pd.read_csv('./data/adult/adult.data', names=columns,
                              sep=', ', engine='python')
orig_test_data = pd.read_csv('./data/adult/adult.test', names=columns,
                             sep=', ', skiprows=1, engine='python')

# Combine the training and test datasets
full_data = pd.concat([orig_train_data, orig_test_data])

# Convert predictor to binary value. Note that the test data contains "."
full_data['income'] = full_data['income'].replace('<=50K', 0).replace('>50K', 1)
full_data['income'] = full_data['income'].replace('<=50K.', 0).replace('>50K.', 1)

# Calculate the training set size based on the original data
pct_train = len(orig_train_data)/len(full_data)
print(f'Number of rows: {len(full_data)}')

# Drop duplicate or unused columns
full_data.drop(['fnlwgt', 'education-num'] , axis=1, inplace=True)

# Remove rows with missing values
full_data.replace('?', np.nan, inplace=True)
full_data.dropna(inplace=True)
print(f'Number of rows after dropna : {len(full_data)}')

# Categorical variables that need to be converted to dummy/indicator variables.
dummy_cols = ['workclass', 'education', 'marital-status', 'occupation', 'relationship',
              'race', 'sex', 'native-country']

# Run the logistic regression for the full data
overall_accuracy = run_regression(full_data, pct_train, dummy_cols)

# Run the logistic regression for a subset of the data
black_data = full_data[full_data['race'] == 'Black']
black_accuracy = run_regression(black_data, pct_train, dummy_cols)

# Run the logistic regression for a subset of the data
female_data = full_data[full_data['sex'] == 'Female']
female_accuracy = run_regression(female_data, pct_train, dummy_cols)

if not os.path.exists("results"):
    os.path.makedirs("results", exists_ok=True)

# Report the accuracy of the three conditions.
results_file = 'results/uci_adult_results.txt'
print(f'Writing results {results_file}')
with open(results_file, "wt") as f:
      f.write(f'Accuracy: {round(overall_accuracy, 3)}, '
        f'{round(black_accuracy, 3)}, '
        f'{round(female_accuracy, 3)}')