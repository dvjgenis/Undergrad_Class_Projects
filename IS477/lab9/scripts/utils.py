"""
IS477 Fall 2024 Lab 9

Utility function to fit a logistic regression model.
"""
import pandas as pd
from sklearn import linear_model
from sklearn import preprocessing
from sklearn.metrics import accuracy_score


def run_regression(data, pct_train, dummy_cols):

    # Store the dependent variable for prediction
    Y = data['income']

    # Convert categorical variables into dummy/indicator variables.
    data = pd.get_dummies(data, columns=dummy_cols)

    # Drop the dependent variable from the dataframe
    data = data.drop('income', axis=1)

    # Standardize features
    scaler = preprocessing.StandardScaler()
    scaled_features = pd.DataFrame(scaler.fit_transform(data),
                                   columns=data.columns)

    # Setup train/test sets
    num_train = int(len(data) * pct_train)
    X_train = scaled_features[:num_train]
    Y_train = Y[:num_train]

    X_test = scaled_features[num_train:]
    Y_test = Y[num_train:]

    # Train the logistic regression model
    model = linear_model.LogisticRegression()
    model.fit(X_train, Y_train)

    # Predict
    predicted_classes = model.predict(X_test)

    # Calculate overall accuracy
    accuracy = accuracy_score(predicted_classes, Y_test.values)

    return accuracy
