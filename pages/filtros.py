import streamlit as st
from dataset import df
import pandas as pd
from utils import converter_csv, converter_excel, mensagem_sucesso

st.title('Dataset de Recorrência de Demandas')

with st.expander('Colunas'):
    colunas = st.multiselect(
        'Selecione as colunas',
        list(df.columns),
        list(df.columns)
    )

st.sidebar.title('Filtros')

with st.sidebar.expander('Cliente'):
    clientes = st.multiselect(
        'Selecione os clientes',
        df['Cliente'].unique(),
        []
    )

with st.sidebar.expander('Tipo de Solicitação'):
    solicitacoes = st.multiselect(
        'Selecione os tipos',
        df['Tipo de Solicitação'].unique(),
        []
    )

with st.sidebar.expander('Quantidade no Período'):
    qtd_periodo = st.slider(
        'Selecione a quantidade',
        int(df['QTD. No Periodo'].min()), 
        int(df['QTD. No Periodo'].max()), 
        (int(df['QTD. No Periodo'].min()), int(df['QTD. No Periodo'].max()))
    )

if clientes and solicitacoes:
    query = '''
        Cliente in @clientes and \
        `Tipo de Solicitação` in @solicitacoes and \
        @qtd_periodo[0] <= `QTD. No Periodo` <= @qtd_periodo[1]
    '''
    filtro_dados = df.query(query)
elif clientes:
    query = '''
        Cliente in @clientes and \
        @qtd_periodo[0] <= `QTD. No Periodo` <= @qtd_periodo[1]
    '''
    filtro_dados = df.query(query)
elif solicitacoes:
    query = '''
        `Tipo de Solicitação` in @solicitacoes and \
        @qtd_periodo[0] <= `QTD. No Periodo` <= @qtd_periodo[1]
    '''
    filtro_dados = df.query(query)
else:
    query = '''
        @qtd_periodo[0] <= `QTD. No Periodo` <= @qtd_periodo[1]
    '''
    filtro_dados = df.query(query)
filtro_dados = filtro_dados[colunas]
st.dataframe(filtro_dados)

st.markdown(f'A tabela possui :blue[{filtro_dados.shape[0]}] linhas e :blue[{filtro_dados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')

coluna1, coluna2, coluna3 = st.columns(3)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value='demandas')

with coluna2:
    st.download_button(
        'Download CSV',
        data=converter_csv(filtro_dados),
        file_name=f'{nome_arquivo}.csv',
        mime='text/csv',
        on_click=mensagem_sucesso
    )

with coluna3:
    st.download_button(
        'Download Excel',
        data=converter_excel(filtro_dados),
        file_name=f'{nome_arquivo}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        on_click=mensagem_sucesso
    )