from flask import Flask, jsonify
import pandas as pd
import boto3
from datetime import datetime
import io
from flask import Blueprint, render_template, jsonify,request,send_file, Flask, redirect
import joblib
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import plotly.graph_objs as go
import plotly.offline as pyo
import plotly.express as px
import plotly.io as pio
import base64
import time


main = Blueprint('main', __name__)

# Configurações AWS

@main.route('/')
def index():
    return render_template('index.html', title='Página Inicial')



# Função para carregar dados do CSV
def carregar_dados(arquivo):
    try:
        return pd.read_csv(arquivo)
    except FileNotFoundError:
        return pd.DataFrame()

# Função para salvar dados de peso
def salvar_peso(data, peso):
    nova_entrada = pd.DataFrame({
        'data': [data],
        'peso': [peso]
    })
    nova_entrada.to_csv('FitTrack\\dados\\peso.csv', mode='a', header=not os.path.exists('FitTrack\\dados\\peso.csv'), index=False)

# Função para gerar gráfico de peso
def gerar_grafico():
    dados = carregar_dados('FitTrack\\dados\\peso.csv')
    if dados.empty:
        return None



    df = pd.read_csv('FitTrack\\dados\\peso.csv')
    
    # Remover duplicatas com base na coluna 'data'
    df = df.drop_duplicates(subset='data', keep='first')  # 'first' mantém a primeira ocorrência
    
    # Redefinir o índice após a remoção das duplicatas (opcional)
    df.reset_index(drop=True, inplace=True)

    df['peso'] = df['peso'].astype(str).str.replace(',', '.', regex=False)

    df['peso'] = pd.to_numeric(df['peso'], errors='coerce')

    print(df)

    # Criar o gráfico com Plotly
    #fig = go.Figure()
    fig = px.line(df, x='data', y='peso', title='Evolução Peso')

    # Adicionar a linha do gráfico
    fig.add_trace(go.Scatter(
        x=df['data'],
        y=df['peso'],
        mode='lines+markers',
        text=df['peso'],  # Mostra os valores
        textposition='top left',
        textfont=dict(color='rgb(23, 128, 234)', size=12),
        name='Peso',
        line=dict(color='rgb(23, 128, 234)', width=2),  # Cor da linha
        marker=dict(size=6)  # Tamanho dos marcadores
    ))

    for index, row in df.iterrows():
        fig.add_annotation(
        x=row['data'],
        y=row['peso'],
        text=str(row['peso']),
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40,
        bgcolor='rgb(32, 59, 86)',  # Fundo da anotação
        font=dict(color='rgb(23, 128, 234)', size=12)
    )

    # Configurar o layout
    fig.update_layout(
        title='Evolução do Peso ao Longo do Tempo',
    xaxis=dict(
        title='Data',
        title_font=dict(size=12, color='rgb(157, 164, 174)'),  # Cor e tamanho do título do eixo X
        tickfont=dict(color='rgb(157, 164, 174)'),  # Cor dos valores do eixo X
        showgrid=True, 
        gridcolor='white'
    ),
    yaxis=dict(
        title='Peso (kg)',
        title_font=dict(size=12, color='rgb(157, 164, 174)'),  # Cor e tamanho do título do eixo Y
        tickfont=dict(color='rgb(157, 164, 174)'),  # Cor dos valores do eixo Y
        showgrid=True, 
        gridcolor='white'
    ),
        title_font=dict(size=16, color='rgb(157, 164, 174)', family='Arial, sans-serif'),
        plot_bgcolor='rgba(255, 255, 255, 0)',  # Define o fundo do gráfico como transparente
        paper_bgcolor='rgba(255, 255, 255, 0)',
    )

    fig.update_yaxes(autorange=True)

    # Gerar HTML para o gráfico
    return pio.to_html(fig, full_html=False)

# Rota para registro de peso
@main.route('/peso', methods=['GET', 'POST'])
def peso_post():
    if request.method == 'POST':
        peso = request.form['peso']
        data = datetime.now().strftime("%Y-%m-%d")
        salvar_peso(data, peso)
        return redirect('/peso')

    # Ler CSV de pesos
    df = pd.read_csv("FitTrack\\dados\\peso.csv", sep=",", decimal=",")
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')
    df['peso'] = df['peso'].astype(str).str.replace(",", ".").astype(float)
    df['dias'] = (df['data'] - df['data'].min()).dt.days

    # Calcular tendência (regressão linear)
    if len(df) >= 2:
        coef = np.polyfit(df['dias'], df['peso'], 1)
        inclinacao = coef[0]  # kg/dia

        if inclinacao < 0:
            tendencia = "queda"
            cor = "green"
            icone = "⬇️"
        else:
            tendencia = "subida"
            cor = "red"
            icone = "⬆️"
        
        tendencia_texto = f"{icone} Tendência de {tendencia}: {inclinacao:.2f} kg/dia"
    else:
        tendencia_texto = "Dados insuficientes para calcular a tendência."
        cor = "gray"

    # Gerar gráfico
    grafico = gerar_grafico()

    return render_template(
        'peso.html',
        grafico=grafico,
        tendencia_texto=tendencia_texto,
        cor=cor
    )



@main.route('/metas', methods=['GET', 'POST'])
def metas():
    if request.method == 'POST':
        # Obter dados do formulário
        data = datetime.now().strftime("%Y-%m-%d")
        agua = request.form['agua']
        creatina = request.form['creatina']
        proteina = request.form['proteina']
        carbo = request.form['carbo']
        gordura = request.form['gordura']
        calorias = request.form['calorias']
        
        # Salvar metas no CSV
        novas_metas = pd.DataFrame({
            'data': [data],
            'agua': [agua],
            'creatina': [creatina],
            'proteina': [proteina],
            'carbo': [carbo],
            'gordura': [gordura],
            'calorias': [calorias]
        })
        
        novas_metas.to_csv('FitTrack\\dados\\metas.csv', mode='a', header=not pd.io.common.file_exists('FitTrack\\dados\\metas.csv'), index=False)
        
        return redirect('/metas')

    # Carregar as últimas 30 dias de dados
    data_atual = datetime.now()
    datas = [(data_atual - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]

    # Calcular as metas e verificar se foram atingidas
    try:
        # Carregar a última meta do arquivo metas_periodo.csv
        metas_periodo_df = pd.read_csv('FitTrack\\dados\\metas_periodo.csv')
        ultima_meta = metas_periodo_df.iloc[-1]
        
        # Extraindo as metas
        agua_meta = ultima_meta['agua']
        calorias_meta = ultima_meta['calorias']
        
        # Calcular as metas em diferentes períodos
        meta_semanal_calorias = calorias_meta * 7
        meta_quinzenal_calorias = calorias_meta * 14
        meta_mensal_calorias = calorias_meta * 30

        meta_semanal_agua = agua_meta * 7
        meta_quinzenal_agua = agua_meta * 14
        meta_mensal_agua = agua_meta * 30

        # Obter metas dos últimos 30 dias
        data_atual = datetime.now()
        datas = [(data_atual - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]

        # Carregar dados do arquivo CSV
        df = pd.read_csv('FitTrack\\dados\\metas.csv')
        print(df)
        df = df[df['data'].isin(datas)]  # Filtrar apenas os últimos 30 dias

        if not df.empty:
            # Contar quantas metas foram batidas
            total_agua_consumida = df['agua'].astype(float).sum()
            calorias_batidas = df['calorias'].astype(float).sum()

            # Calcular o progresso
            progresso_calorias_semanal = min(calorias_batidas / meta_semanal_calorias * 100, 100)
            progresso_calorias_quinzenal = min(calorias_batidas / meta_quinzenal_calorias * 100, 100)
            progresso_calorias_mensal = min(calorias_batidas / meta_mensal_calorias * 100, 100)

            progresso_agua_semanal = min(total_agua_consumida / meta_semanal_agua * 100, 100)
            progresso_agua_quinzenal = min(total_agua_consumida / meta_quinzenal_agua * 100, 100)
            progresso_agua_mensal = min(total_agua_consumida / meta_mensal_agua * 100, 100)

            # Criar gráficos de progresso (gauge) para água e calorias
            fig = go.Figure()

            # Gráfico de progresso semanal de calorias
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=progresso_calorias_semanal,
                title={'text': "Progresso Semanal Calorias (%)", 'font': {'color': 'rgb(157, 164, 174)'}},
                number={'font': {'color': 'rgb(157, 164, 174)'}},
                gauge=dict(
                    axis=dict(range=[0, 100]),
                    bar=dict(color="#04c1e7"),
                    bgcolor="white",  # Remove o fundo do gráfico
                    steps=[
                        {'range': [0, 100], 'color': "lightgray"}
                    ],
                ),
                domain={'row': 0, 'column': 0}
            ))

            # Gráfico de progresso quinzenal de calorias
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=progresso_calorias_quinzenal,
                title={'text': "Progresso Quinzenal Calorias (%)", 'font': {'color': 'rgb(157, 164, 174)'}},
                number={'font': {'color': "rgb(157, 164, 174)"}},
                gauge=dict(
                    axis=dict(range=[0, 100]),
                    bar=dict(color="#04c1e7"),
                    bgcolor="white",
                    steps=[
                        {'range': [0, 100], 'color': "lightgray"}
                    ],
                ),
                domain={'row': 0, 'column': 1}
            ))

            # Gráfico de progresso mensal de calorias
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=progresso_calorias_mensal,
                title={'text': "Progresso Mensal Calorias (%)", 'font': {'color': 'rgb(157, 164, 174)'}},
                number={'font': {'color': 'rgb(157, 164, 174)'}},
                gauge=dict(
                    axis=dict(range=[0, 100]),
                    bar=dict(color="#04c1e7"),
                    bgcolor="white",
                    steps=[
                        {'range': [0, 100], 'color': "lightgray"}
                    ],
                ),
                domain={'row': 0, 'column': 2}
            ))
            '''
            # Gráfico de progresso semanal de água
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=progresso_agua_semanal,
                title={'text': "Progresso Semanal Água (%)"},
                gauge=dict(
                    axis=dict(range=[0, 100]),
                    bar=dict(color="blue"),
                    bgcolor="white",
                    steps=[
                        {'range': [0, 100], 'color': "lightgray"}
                    ],
                ),
                domain={'row': 0, 'column': 1}
            ))

            # Gráfico de progresso quinzenal de água
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=progresso_agua_quinzenal,
                title={'text': "Progresso Quinzenal Água (%)"},
                gauge=dict(
                    axis=dict(range=[0, 100]),
                    bar=dict(color="green"),
                    bgcolor="white",
                    steps=[
                        {'range': [0, 100], 'color': "lightgray"}
                    ],
                ),
                domain={'row': 1, 'column': 1}
            ))

            # Gráfico de progresso mensal de água
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=progresso_agua_mensal,
                title={'text': "Progresso Mensal Água (%)"},
                gauge=dict(
                    axis=dict(range=[0, 100]),
                    bar=dict(color="orange"),
                    bgcolor="white",
                    steps=[
                        {'range': [0, 100], 'color': "lightgray"}
                    ],
                ),
                domain={'row': 2, 'column': 1}
            ))'''

            # Layout do gráfico
            fig.update_layout(
                grid=dict(rows=1, columns=3),  # Define uma grade de 3 x 2
                width=1500,
                height=150,
                plot_bgcolor='rgba(255, 255, 255, 0)',  # Define o fundo do gráfico como transparente
                paper_bgcolor='rgba(255, 255, 255, 0)',
                margin=dict(l=50, r=50, t=50, b=50),

            )

            # Gerar HTML para os gráficos de progresso
            rodas_grafico = fig.to_html(full_html=False)

        else:
            rodas_grafico = ""

    except FileNotFoundError:
        rodas_grafico = ""
    sequencia = calcular_sequencia_creatina_ok()
    grafico_creatina = gerar_grafico_creatina(sequencia)

    return render_template('metas.html', metas=df.to_dict(orient='records'), rodas_grafico=rodas_grafico, grafico=grafico_creatina)

@main.route('/definir_metas', methods=['GET', 'POST'])
def definir_metas():
    if request.method == 'POST':
        # Obter dados do formulário
        data = datetime.now().strftime("%Y-%m-%d")
        agua = float(request.form.get('agua', 0))  # Água em litros
        calorias = int(request.form.get('calorias', 0))      # Calorias
        proteina = int(request.form.get('proteina', 0))      # Proteína em gramas
        carboidrato = int(request.form.get('carboidrato', 0))# Carboidratos em gramas
        
        # Salvar metas no CSV
        novas_metas = pd.DataFrame({
            'data': [data],
            'agua': [agua],
            'calorias': [calorias],
            'proteina': [proteina],
            'carbo': [carboidrato]
        })

        novas_metas.to_csv('dados/metas_periodo.csv', mode='a', header=not pd.io.common.file_exists('dados/metas_periodo.csv'), index=False)
        
        return redirect('/definir_metas')

    return render_template('definir_metas.html')

@main.route('/medidas', methods=['GET', 'POST'])
def medidas():
    sequencia = calcular_sequencia_creatina_ok()
    grafico_creatina = gerar_grafico_creatina(sequencia)
    return render_template('medidas.html', grafico=grafico_creatina)

def calcular_sequencia_creatina_ok():
    # Lê o CSV
    df = pd.read_csv('FitTrack\\dados\\metas.csv')
    # Ordena por data (importante)
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data')

    # Converte creatina em booleano: OK = True, NOK = False
    df['creatina_ok'] = df['creatina'].str.upper() == 'OK'

    # Calcula sequência atual
    sequencia = 0
    for status in reversed(df['creatina_ok'].tolist()):
        if status:
            sequencia += 1
        else:
            break

    return sequencia

def gerar_grafico_creatina(sequencia):
    cor = '#087d9a' if sequencia >= 2 else '#6b6b6b'

    fig = go.Figure(go.Indicator(
        mode="number",
        value=sequencia,
        number={'font': {'size': 15, 'color': 'white'}},
        domain={'x': [0, 0], 'y': [0, 0]},
    ))

    fig.update_layout(
        paper_bgcolor=cor,
        height=50,
        width=50,
        margin=dict(l=20, r=20, t=20, b=20),
    )

    graph_html = pio.to_html(fig, full_html=False)
    return graph_html