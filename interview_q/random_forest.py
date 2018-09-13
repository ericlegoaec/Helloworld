import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
# Use datetime for creating date objects for plotting
import datetime

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import export_graphviz
import pydot

def main():
    features = pd.read_csv(os.path.join(os.path.dirname(__file__), 'temps.csv'))
    head_data = features.head(5)
    # print(head_data)
    # print('The shape of our features is:', features.shape)
    # print (features.describe())

    features = pd.get_dummies(features)
    labels = np.array(features['actual'])
    # print (features.iloc[:,5:].head(5))
    features = features.drop('actual', axis = 1)
    feature_list = list(features.columns)
    features = np.array(features)

    train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.25, random_state = 42)
    print('Training Features Shape:', train_features.shape)
    print('Training Labels Shape:', train_labels.shape)
    print('Testing Features Shape:', test_features.shape)
    print('Testing Labels Shape:', test_labels.shape)

    # The baseline predictions are the historical averages
    baseline_preds = test_features[:, feature_list.index('average')]
    # Baseline errors, and display average baseline error
    baseline_errors = abs(baseline_preds - test_labels)
    print('Average baseline error: ', round(np.mean(baseline_errors), 2))

    rf = RandomForestRegressor(n_estimators = 1000, random_state = 42, max_depth = 3)
    rf.fit(train_features, train_labels)
    
    # Use the forest's predict method on the test data
    predictions = rf.predict(test_features)

    # Calculate the absolute errors
    errors = abs(predictions - test_labels)

    # Print out the mean absolute error (mae)
    print('Mean Absolute Error:', round(np.mean(errors), 2), 'degrees.')

    tree = rf.estimators_[5]
    export_graphviz(tree, out_file = 'tree.dot', feature_names = feature_list, rounded = True)
    (graph, ) = pydot.graph_from_dot_file('tree.dot')
    graph.write_png('tree.png')

    # Dates of training values
    months = features[:, feature_list.index('month')]
    days = features[:, feature_list.index('day')]
    years = features[:, feature_list.index('year')]
    # List and then convert to datetime object
    dates = [str(int(year)) + '-' + str(int(month)) + '-' + str(int(day)) for year, month, day in zip(years, months, days)]
    dates = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in dates]
    # Dataframe with true values and dates
    true_data = pd.DataFrame(data = {'date': dates, 'actual': labels})
    # Dates of predictions
    months = test_features[:, feature_list.index('month')]
    days = test_features[:, feature_list.index('day')]
    years = test_features[:, feature_list.index('year')]
    # Column of dates
    test_dates = [str(int(year)) + '-' + str(int(month)) + '-' + str(int(day)) for year, month, day in zip(years, months, days)]
    # Convert to datetime objects
    test_dates = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in test_dates]
    # Dataframe with predictions and dates
    predictions_data = pd.DataFrame(data = {'date': test_dates, 'prediction': predictions})
    # Plot the actual values
    plt.plot(true_data['date'], true_data['actual'], 'b-', label = 'actual')
    # Plot the predicted values
    plt.plot(predictions_data['date'], predictions_data['prediction'], 'ro', label = 'prediction')
    plt.xticks(rotation = '60'); 
    plt.legend()
    # Graph labels
    plt.xlabel('Date')
    plt.ylabel('Maximum Temperature (F)')
    plt.title('Actual and Predicted Values')
    plt.show()
    return

if __name__ == "__main__":
    main()