from flask import Flask, request, jsonify
import numpy as np
import joblib
import tensorflow as tf
from flask import Blueprint, render_template, jsonify,request,send_file, Flask, redirect
import pandas as pd
import time
import psutil
import os
from flask import jsonify
from collections import deque

main = Blueprint('main', __name__)

model = tf.keras.models.load_model("app/model/lstm_model_aapl.h5")
scaler = joblib.load("app/model/scaler.pkl")

@main.route('/')
def index():
    return render_template('index.html', title='Página Inicial')

@main.route("/predict")
def predict_home():
    return render_template('predict.html')


@main.route("/predict_csv", methods=["POST"])
def predict_csv():
    if "file" not in request.files or request.files["file"].filename == "":
        return "Nenhum arquivo válido enviado", 400

    try:
        file = request.files["file"]
        df = pd.read_csv(file)

        if "close" not in df.columns:
            return "O CSV deve conter uma coluna chamada 'close'", 400

        close_prices = df["close"].values
        if len(close_prices) < 60:
            return "Pelo menos 60 valores são necessários", 400

        n_days = 10  # Quantos dias prever

        last_60 = np.array(close_prices[-60:], dtype=np.float32).reshape(-1, 1)
        scaled = scaler.transform(last_60)

        input_seq = scaled.flatten().tolist()
        predictions = []

        for _ in range(n_days):
            X_input = np.array(input_seq[-60:]).reshape(1, 60, 1)
            pred = model.predict(X_input)
            predictions.append(pred[0][0])
            input_seq.append(pred[0][0])

        predictions = np.array(predictions).reshape(-1, 1)
        predictions_rescaled = scaler.inverse_transform(predictions)

        predicted_prices = [round(float(p[0]), 2) for p in predictions_rescaled]

        return render_template("predict.html", predictions=predicted_prices)

    except Exception as e:
        return f"Erro ao processar o arquivo: {str(e)}", 500


@main.route("/predict_manual", methods=["POST"])
def predict_manual():
    try:
        prices_str = request.form["prices"]
        price_list = [float(p.strip()) for p in prices_str.split(",") if p.strip()]

        if len(price_list) != 60:
            return "Você deve fornecer exatamente 60 valores", 400

        n_days = 10  # Quantos dias prever

        input_data = np.array(price_list, dtype=np.float32).reshape(-1, 1)
        scaled = scaler.transform(input_data)

        input_seq = scaled.flatten().tolist()
        predictions = []

        for _ in range(n_days):
            X_input = np.array(input_seq[-60:]).reshape(1, 60, 1)
            pred = model.predict(X_input)
            predictions.append(pred[0][0])
            input_seq.append(pred[0][0])

        predictions = np.array(predictions).reshape(-1, 1)
        predictions_rescaled = scaler.inverse_transform(predictions)

        predicted_prices = [round(float(p[0]), 2) for p in predictions_rescaled]

        return render_template("predict.html", predictions=predicted_prices)

    except Exception as e:
        return f"Erro ao processar os dados manuais: {str(e)}", 500


#----------------------METRICS---------------------------------------#



# Variáveis globais para armazenar as últimas métricas
metrics = {
    "response_time": 0,
    "cpu_percent": 0,
    "memory_mb": 0
}

@main.before_request
def start_timer():
    from flask import g
    g.start = time.time()

MAX_HISTORY = 100 
metrics_history = deque(maxlen=MAX_HISTORY)

@main.after_request
def after_request(response):
    from flask import g, request
    elapsed = time.time() - g.start
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 ** 2)
    cpu = process.cpu_percent(interval=None)

    current_metrics = {
        "timestamp": time.time(),
        "response_time": round(elapsed, 3),
        "cpu_percent": round(cpu, 1),
        "memory_mb": round(mem, 2)
    }
    metrics_history.append(current_metrics)

    # Atualiza as métricas globais para a API atual
    metrics.update(current_metrics)

    return response

@main.route("/metrics_history")
def get_metrics_history():
    return jsonify(list(metrics_history))

@main.route('/metrics')
def monitor():
    return render_template('metrics.html')




