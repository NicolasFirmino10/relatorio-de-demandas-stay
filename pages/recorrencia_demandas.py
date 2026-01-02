import streamlit as st
from dataset import df as df_default
import pandas as pd
import plotly.express as px
from utils import converter_csv, converter_excel, mensagem_sucesso

st.set_page_config(layout='wide', page_title='Recorrência de Demandas')
st.title('📊 Análise de Recorrência de Demandas')

# Opção de fonte de dados
data_source = st.radio(
    "Escolha a fonte dos dados:",
    ["📁 Upload de arquivo", "💾 Dados padrão do sistema"]
)

if data_source == "📁 Upload de arquivo":
    st.subheader("📁 Upload de Dados")
    uploaded_file = st.file_uploader(
        "Faça upload do arquivo de demandas (CSV ou Excel)", 
        type=['csv', 'xlsx', 'xls']
    )
    
    if uploaded_file is not None:
        try:
            # Carrega o arquivo
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"Arquivo carregado com sucesso! {len(df)} registros encontrados.")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {str(e)}")
            df = None
    else:
        st.info("👆 Faça upload de um arquivo para começar a análise")
        st.markdown("""
        ### 📋 Formato esperado do arquivo:
        - **CSV** ou **Excel** (.xlsx, .xls)
        - Colunas sugeridas: Cliente, Tipo de Solicitação, Categoria, Data, Quantidade
        - Primeira linha deve conter os cabeçalhos
        """)
        df = None
else:
    df = df_default
    st.success(f"Dados padrão carregados! {len(df)} registros encontrados.")

if df is not None:
    # Métricas principais
    st.subheader("📈 Métricas Gerais")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Registros", len(df))
    
    with col2:
        if 'QTD. No Periodo' in df.columns:
            st.metric("Total de Demandas", int(df['QTD. No Periodo'].sum()))
        else:
            st.metric("Total de Demandas", "N/A")
    
    with col3:
        if 'Cliente' in df.columns:
            st.metric("Clientes Únicos", df['Cliente'].nunique())
        else:
            st.metric("Clientes Únicos", "N/A")
    
    with col4:
        if 'Tipo de Solicitação' in df.columns:
            st.metric("Tipos de Solicitação", df['Tipo de Solicitação'].nunique())
        else:
            st.metric("Tipos de Solicitação", "N/A")
    
    # Análises
    tab1, tab2, tab3 = st.tabs(['📊 Análise com Filtros', '📋 Dados Filtrados', '📥 Download'])
    
    with tab1:
        with st.expander('Colunas'):
            colunas = st.multiselect(
                'Selecione as colunas',
                list(df.columns),
                list(df.columns)
            )
        
        st.sidebar.title('🔍 Filtros')
        
        if 'Cliente' in df.columns:
            with st.sidebar.expander('Cliente'):
                clientes = st.multiselect(
                    'Selecione os clientes',
                    df['Cliente'].unique(),
                    []
                )
        else:
            clientes = []
        
        if 'Tipo de Solicitação' in df.columns:
            with st.sidebar.expander('Tipo de Solicitação'):
                solicitacoes = st.multiselect(
                    'Selecione os tipos',
                    df['Tipo de Solicitação'].unique(),
                    []
                )
        else:
            solicitacoes = []
        
        if 'QTD. No Periodo' in df.columns:
            with st.sidebar.expander('Quantidade no Período'):
                qtd_periodo = st.slider(
                    'Selecione a quantidade',
                    int(df['QTD. No Periodo'].min()), 
                    int(df['QTD. No Periodo'].max()), 
                    (int(df['QTD. No Periodo'].min()), int(df['QTD. No Periodo'].max()))
                )
        else:
            qtd_periodo = None
        
        # Aplicar filtros
        filtro_dados = df.copy()
        
        if clientes and 'Cliente' in df.columns:
            filtro_dados = filtro_dados[filtro_dados['Cliente'].isin(clientes)]
        
        if solicitacoes and 'Tipo de Solicitação' in df.columns:
            filtro_dados = filtro_dados[filtro_dados['Tipo de Solicitação'].isin(solicitacoes)]
        
        if qtd_periodo and 'QTD. No Periodo' in df.columns:
            filtro_dados = filtro_dados[
                (filtro_dados['QTD. No Periodo'] >= qtd_periodo[0]) & 
                (filtro_dados['QTD. No Periodo'] <= qtd_periodo[1])
            ]
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Tipo de Solicitação' in filtro_dados.columns:
                st.subheader("Top 10 Tipos de Solicitação")
                top_solicitacoes = filtro_dados['Tipo de Solicitação'].value_counts().head(10)
                fig = px.bar(x=top_solicitacoes.values, y=top_solicitacoes.index, orientation='h')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'Cliente' in filtro_dados.columns:
                st.subheader("Top 10 Clientes")
                top_clientes = filtro_dados['Cliente'].value_counts().head(10)
                fig = px.bar(x=top_clientes.values, y=top_clientes.index, orientation='h')
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Dados Filtrados")
        filtro_dados_display = filtro_dados[colunas] if 'colunas' in locals() else filtro_dados
        st.dataframe(filtro_dados_display, use_container_width=True)
        st.markdown(f'A tabela possui **{filtro_dados_display.shape[0]}** linhas e **{filtro_dados_display.shape[1]}** colunas')
    
    with tab3:
        st.subheader("Download dos Dados")
        nome_arquivo = st.text_input('Nome do arquivo', value='demandas')
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                '📥 Download CSV',
                data=converter_csv(filtro_dados_display),
                file_name=f'{nome_arquivo}.csv',
                mime='text/csv',
                on_click=mensagem_sucesso
            )
        
        with col2:
            st.download_button(
                '📥 Download Excel',
                data=converter_excel(filtro_dados_display),
                file_name=f'{nome_arquivo}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                on_click=mensagem_sucesso
            )