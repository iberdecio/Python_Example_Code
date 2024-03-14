import pandas as pd
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
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
print(transposedData['normalized_cases'])



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

# Ensuring the length of X and y are the same (necessary if the end of your dataset doesn't have 4 values to look ahead)
min_length = min(len(X), len(y))
X, y = X[:min_length], y[:min_length]

X_df = pd.DataFrame(X, columns=[f'lag_{i}' for i in range(X.shape[1])])
print(X_df)
y_df = pd.DataFrame(y, columns=[f'future_step_{i+1}' for i in range(len(y[0]))])
print(y_df)
print(f"Shape of X: {X_df.shape}")
print(f"Shape of y: {y_df.shape}")

from keras.models import Sequential
from keras.layers import LSTM, Dense

X = np.array(X_df)
y = np.array([np.array(yi) for yi in y_df.values])  # Convert y to a numpy array of arrays

# Reshape X for LSTM [samples, time steps, features]
X = X.reshape((X.shape[0], 1, X.shape[1]))

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the LSTM model
model = Sequential()
model.add(LSTM(units=50, return_sequences=False, input_shape=(X_train.shape[1], X_train.shape[2])))  # Adjust units as needed
model.add(Dense(y_train.shape[1]))  # Output layer with units equal to future steps

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=1)  # Adjust epochs and batch_size as needed

# Evaluate the model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print("Test MSE:", mse)

# Assuming the last 6*D data points are required for a single prediction
latest_data = normalized_series[-6*2:].values  # Adjust based on D and T
latest_embedded = create_time_delay_embedding(pd.Series(latest_data), D=6, T=2)
latest_embedded_values = latest_embedded.values[-1].reshape((1, 1, latest_embedded.shape[1]))  # Get the last sequence for prediction
future_normalized_cases = model.predict(latest_embedded_values)
print("Predicted Values:", future_normalized_cases)

max_smoothed_cases = transposedData['smoothed_cases'].max()
future_cases = future_normalized_cases * max_smoothed_cases
print("Unnormalized future cases:", future_cases)
