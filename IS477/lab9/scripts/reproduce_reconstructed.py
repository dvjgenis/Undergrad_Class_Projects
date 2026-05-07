"""
This example uses the adult_reconstruction.csv described in:

  Ding, F., Hardt, M., Miller, J., & Schmidt, L. (2021).
  Retiring Adult: New Datasets for Fair Machine Learning.
  Advances in Neural Information Processing Systems, 34, 6478–6490.

The purpose of this script is to implement a standard logistic
regression model training on the reconstructed data to compare to the
results reported in the paper.
"""
import pandas as pd
from utils import run_regression

# Read the source data
reconstructed_data = pd.read_csv('./data/folktables/adult_reconstruction.csv',
                                 sep=',', engine='python')

# The following will be converted to dummy variables for the regression
dummy_cols = ['workclass', 'education', 'marital-status', 'occupation',
              'relationship', 'race', 'gender', 'native-country']

# Make a copy of the dataframe and create an income threshold based on UCI Adult baseline
thresholded_data = reconstructed_data.copy()
thresholded_data.loc[thresholded_data['income'] <= 50000, 'income'] = 0
thresholded_data.loc[thresholded_data['income'] > 50000, 'income'] = 1

# Fit the regression model and report accuracy for each of the three conditions
# Train using 30% of data based on default UCI Adult train/test split.
pct_train = 0.3

# Full data
accuracy = run_regression(thresholded_data, pct_train, dummy_cols)

# Black instances
black_data = thresholded_data[thresholded_data['race'] == 'Black']
black_accuracy = run_regression(black_data, pct_train, dummy_cols)

# Female insteances
female_data = thresholded_data[thresholded_data['gender'] == 'Female']
female_accuracy = run_regression(female_data, pct_train, dummy_cols)

# Report the accuracy of the three conditions.
results_file = 'results/adult_reconstruction_results.txt'
print(f'Writing results {results_file}')
with open(results_file, mode='wt') as f:
  f.write(f'Accuracy: {round(accuracy, 3)},'
        f'{round(black_accuracy, 3)},'
        f'{round(female_accuracy, 3)}')

# Fit regression models and report accuracy at multiple income threshold levels
accuracy_df = pd.DataFrame(columns=['accuracy'])
for threshold in range(15000, 85000, 5000):

    thresholded_data = reconstructed_data.copy()
    thresholded_data.loc[thresholded_data['income'] <= threshold, 'income'] = 0
    thresholded_data.loc[thresholded_data['income'] > threshold, 'income'] = 1

    accuracy = run_regression(thresholded_data, pct_train, dummy_cols)
    accuracy_df.loc[threshold] = accuracy

# Plot accuracy v income threshold
plt = accuracy_df.plot.line(xlim={10000, 85000}, ylim={0.65, 1.00},
                            xlabel='Income threshold', ylabel='Accuracy',
                            legend=False)

figure_file = 'results/income_threshold.pdf'
print(f'Writing figure to {figure_file}')
plt.figure.savefig(figure_file)
