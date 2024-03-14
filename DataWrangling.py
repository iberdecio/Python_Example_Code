import pandas as pd
import os
import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dense
print(os.getcwd())
file_path = 'C:/Users/iberd/Bioinformatics/TestTaken.csv'
test_takens = pd.read_csv(file_path)
#transpose data

transposedData = test_takens.transpose()
transposedData.columns = ['weekly_cases']
transposedData = transposedData[1:] 

print("Original shape:", test_takens.shape)
print("Transposed shape:",transposedData.shape)

transposedData.index = pd.to_datetime(transposedData.index)


#rolling mean of 3 weeks at a time
transposedData['weekly_cases'] = pd.to_numeric(transposedData['weekly_cases'], errors='coerce')
print(transposedData['weekly_cases'].dtype)
transposedData['smoothed_cases'] = transposedData['weekly_cases'].rolling(window=3).mean()
transposedData['normalized_cases'] = transposedData['smoothed_cases'] / transposedData['smoothed_cases'].max()




def create_time_delay_embedding(series, D, T):
    N = len(series)
    lagged_data = pd.DataFrame(index=series.index)
    for i in range(D):
        lagged_data[f'lag_{T*i}'] = series.shift(T * i)
    lagged_data.dropna(inplace=True)  # Drop rows with NaN values
    return lagged_data

# Assuming 'normalized_cases' is a column in 'transposedData'
normalized_series = transposedData['normalized_cases']
embedded_data = create_time_delay_embedding(normalized_series, D=6, T=2)


# Number of steps to predict
n_future_steps = 4

# Inputs (embedded data)
X = embedded_data.values

# Outputs (next 4 values)
y = [transposedData['normalized_cases'].iloc[i + n_future_steps:i + n_future_steps + 4].values for i in range(len(embedded_data))]


min_length = min(len(X), len(y))
X, y = X[:min_length], y[:min_length]

X_df = pd.DataFrame(X, columns=[f'lag_{i}' for i in range(X.shape[1])])
y_df = pd.DataFrame(y, columns=[f'future_step_{i+1}' for i in range(len(y[0]))])
print(f"Shape of X: {X_df.shape}")
print(f"Shape of y: {y_df.shape}")

combined_df = pd.concat([X_df, y_df], axis=1)

print(combined_df)




