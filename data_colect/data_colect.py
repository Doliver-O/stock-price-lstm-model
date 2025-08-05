import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from keras import Input
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math
import joblib


# Configurações
symbol = 'AAPL'  # Símbolo da empresa da Apple
start_date = '2015-01-01'
end_date = '2025-01-01'

# Coleta de Dados
df = yf.download(symbol, start=start_date, end=end_date, auto_adjust=False)

# Verificação e Pre-processamento
print(df.head())

# Definindo o índice de datetime
df = df[['Close']]
df = df.dropna()

# Normalização dos dados
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(df)

# Dividindo dados para treino e teste
train_size = int(len(scaled_data) * 0.8)
train_data, test_data = scaled_data[:train_size], scaled_data[train_size:]

def create_dataset(data, time_step=1):
    X, Y = [], []
    for i in range(len(data)-time_step-1):
        a = data[i:(i+time_step), 0]
        X.append(a)
        Y.append(data[i + time_step, 0])
    return np.array(X), np.array(Y)

# Criando datasets para treino e teste
time_step = 60
X_train, y_train = create_dataset(train_data, time_step)
X_test, y_test = create_dataset(test_data, time_step)

# Redimensionando as entradas para [samples, time steps, features]
X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)


#-----------------------ETAPA 2-------------------------------------------#



# Modelo LSTM
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(time_step, 1)))
model.add(LSTM(50, return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))

# Compilação
model.compile(optimizer='adam', loss='mean_squared_error')

# Treinamento
model.fit(X_train, y_train, batch_size=64, epochs=100, validation_data=(X_test, y_test))


#-------------------------------ETAPA 3-------------------------------------#



# Previsões
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)
y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

# Avaliação
mae = mean_absolute_error(y_test_actual, predictions)
rmse = math.sqrt(mean_squared_error(y_test_actual, predictions))

print(f'MAE: {mae:.2f}')
print(f'RMSE: {rmse:.2f}')


#-------------------------Extra-------------------------------#

#Visualização Gráfica dos resultados

plt.figure(figsize=(14,6))
plt.plot(y_test_actual, label='Real')
plt.plot(predictions, label='Previsto')
plt.title("Previsão de preços com LSTM")
plt.legend()
plt.show()

#----------------------Exportar o Modelo--------------------#

model.save("lstm_model_aapl.h5")
joblib.dump(scaler, "scaler.pkl")