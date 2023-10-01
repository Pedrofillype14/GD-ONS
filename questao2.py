import requests
import json
import pprint
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import time

# Utilizar uma paleta de cores pré-definida
cores = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'cyan', 'magenta','black','yellow','dark-blue']

# Criar o gráfico
fig = go.Figure()

#importando dados da API da ANELL
print('Baixando dados da API da ANEEL')
link = requests.get('https://dadosabertos.aneel.gov.br/api/3/action/datastore_search?resource_id=b1bd71e7-d0ad-4214-9053-cbd58e9564a7&offset=0&limit=1000')
informacoes = link.json()

#selecionando os dados resul e records
records = informacoes['result']['records']

#tranformando em um dataframe apenas as informações do records
data = pd.DataFrame(records)

#selecionando as colunas desejadas 
data = data[['DthAtualizaCadastralEmpreend','DscClasseConsumo','MdaPotenciaInstaladaKW','SigUF']]

# Converter coluna de data para tipo datetime
data['DthAtualizaCadastralEmpreend'] = pd.to_datetime(data['DthAtualizaCadastralEmpreend'])

# Extrair mês e ano da data
data['MesAno'] = data['DthAtualizaCadastralEmpreend'].dt.to_period('M')

# Agrupar por mês, estado e classe de consumo e contar os empreendimentos
df_agrupado = data.groupby(['MesAno', 'SigUF', 'DscClasseConsumo']).size().reset_index(name='Total')
df_agrupado2 = data.groupby(['MesAno', 'SigUF', 'MdaPotenciaInstaladaKW']).size().reset_index(name='Total')

print('Gerando Grafico')
time.sleep(1)

# Remover vírgula dos valores da coluna 'MdaPotenciaInstaladaKW' e converter para float
if ((data['MdaPotenciaInstaladaKW'].dtype)== 'float64'):
    df_agrupado2['MdaPotenciaInstaladaKW'] = df_agrupado2['MdaPotenciaInstaladaKW'].round(2)
    df_agrupado2 = data.groupby(['MesAno', 'SigUF'])['MdaPotenciaInstaladaKW'].sum().reset_index()
else:
    data['MdaPotenciaInstaladaKW'] = data['MdaPotenciaInstaladaKW'].str.replace(',', '').astype(float)
    df_agrupado2 = data.groupby(['MesAno', 'SigUF'])['MdaPotenciaInstaladaKW'].sum().reset_index()

# Criar um gráfico de linhas
plt.figure(figsize=(12, 6))

# Loop pela coluna de estados
for i, estado in enumerate(df_agrupado['SigUF'].unique()):
    df_estado = df_agrupado[df_agrupado['SigUF'] == estado]
    
    # Loop pelas classes de consumo
    for j, classe_consumo in enumerate(df_estado['DscClasseConsumo'].unique()):
        df_plot = df_estado[df_estado['DscClasseConsumo'] == classe_consumo].drop_duplicates()
       
        # Adicionar a linha do estado e classe de consumo ao gráfico com cor personalizada
        fig.add_trace(go.Scatter(
            x=df_plot['MesAno'].dt.to_timestamp(),
            y=df_plot['Total'],
            name=f"{estado} - {classe_consumo}",
            line=dict(color=cores[(i * len(df_estado['DscClasseConsumo'].unique())) + j])
        ))

# Configurar o layout do gráfico          
fig.update_layout(
    title={
        'text':'Evolução Temporal do Total Mensal de Empreendimentos por Estado e Classe de Consumo',
        'y': 0.95,  # Define a posição vertical do título (0-1)
        'x': 0.5,  # Define a posição horizontal do título (0-1)
        'xanchor': 'center',  # Ancora do título no eixo x
        'yanchor': 'top'  # Ancora do título no eixo y
        },
    xaxis=dict(title='Mês/Ano'),
    yaxis=dict(title='Total de Empreendimentos'),
    xaxis_tickangle=-45,
    showlegend=True
)


# Salvar o gráfico em HTML
fig.write_html("grafico_ClasseXEstado.html")


###GERAR GRÁFICO DE POTENCIA

# Criar um gráfico de linhas
fig = go.Figure()

# Loop pela coluna de estados
for i, estado in enumerate(df_agrupado2['SigUF'].unique()):
    df_estado = df_agrupado2[df_agrupado2['SigUF'] == estado]
    
    # Plotar a linha do estado
    fig.add_trace(go.Scatter(
        x=df_estado['MesAno'].dt.to_timestamp(),
        y=df_estado['MdaPotenciaInstaladaKW'],
        name=estado,
        line=dict(color=cores[i % len(cores)])
    ))

# Configurar o layout do gráfico          
fig.update_layout(
    title={
        'text': 'Evolução Temporal da Soma da Potência por Estado',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis=dict(title='Mês/Ano'),
    yaxis=dict(title='Soma da Potência em KW'),
    xaxis_tickangle=-45,
    showlegend=True
)

# Salvar o gráfico em HTML
fig.write_html("grafico_SomaPotenciaXEstado.html")

print('Grafico Gerado com sucesso!')
time.sleep(2)