import streamlit as st
import pandas as pd
import plotly.express as px
from utils import converter_csv, converter_excel, mensagem_sucesso

st.set_page_config(layout='wide', page_title='Atendimentos dos Agentes')
st.title('🎧 Análise de Atendimentos dos Agentes')

# Opção de fonte de dados
data_source = st.radio(
    "Escolha a fonte dos dados:",
    ["📁 Upload de arquivo", "💾 Dados padrão do sistema"]
)

if data_source == "📁 Upload de arquivo":
    st.subheader("📁 Upload de Dados")
    
    # Botão para limpar dados
    if st.button("🗑️ Limpar Dados Carregados"):
        if 'uploaded_data' in st.session_state:
            del st.session_state.uploaded_data
        st.rerun()
    
    uploaded_file = st.file_uploader(
        "Faça upload do arquivo de atendimentos (CSV ou Excel)", 
        type=['csv', 'xlsx', 'xls']
    )
    
    # Verificar se já existe dados na sessão
    if 'uploaded_data' in st.session_state:
        df = st.session_state.uploaded_data
        st.success(f"Arquivo já carregado! {len(df)} registros encontrados.")
    elif uploaded_file is not None:
        try:
            # Carrega o arquivo
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Salvar na sessão
            st.session_state.uploaded_data = df
            st.success(f"Arquivo carregado com sucesso! {len(df)} registros encontrados.")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {str(e)}")
            df = None
    else:
        st.info("👆 Faça upload de um arquivo para começar a análise")
        st.markdown("""
        ### 📋 Formato esperado do arquivo:
        - **CSV** ou **Excel** (.xlsx, .xls)
        - Colunas sugeridas: Agente/Atendente, Data, Tempo/Duração, Satisfação/Nota, Cliente, Tipo de Atendimento
        - Primeira linha deve conter os cabeçalhos
        """)
        df = None
else:
    st.info("💾 Dados padrão não disponíveis para esta análise. Faça upload de um arquivo.")
    df = None

if df is not None:
    # Remover colunas indesejadas
    colunas_remover = ['Tipo Contrato', 'Contexto', 'Problema', 'Status', 'SLA']
    df = df.drop(columns=[col for col in colunas_remover if col in df.columns])
    
    # Filtros globais
    st.sidebar.title('🔍 Filtros Globais')
    
    # Filtro por Data
    date_cols = [col for col in df.columns if any(palavra in col.lower() for palavra in ['data', 'date', 'dia', 'mes', 'ano', 'time', 'timestamp'])]
    
    # Seleção manual de coluna de data sempre disponível
    with st.sidebar.expander('📅 Selecionar Coluna de Data'):
        colunas_data_especificas = ['DT Abertura', 'DT Conclusão']
        colunas_data_disponiveis = [col for col in colunas_data_especificas if col in df.columns]
        
        coluna_data_selecionada = st.selectbox(
            'Escolha uma coluna para usar como data:',
            ['Nenhuma'] + colunas_data_disponiveis,
            index=1 if colunas_data_disponiveis else 0
        )
        if coluna_data_selecionada != 'Nenhuma':
            date_cols = [coluna_data_selecionada]
    
    if date_cols:
        with st.sidebar.expander('📅 Período'):
            df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], dayfirst=True, errors='coerce')
            data_min = df[date_cols[0]].min().date()
            data_max = df[date_cols[0]].max().date()
            
            data_inicio = st.date_input('Data início', value=data_min, min_value=data_min, max_value=data_max, format='DD/MM/YYYY')
            data_fim = st.date_input('Data fim', value=data_max, min_value=data_min, max_value=data_max, format='DD/MM/YYYY')
            
            df = df[(df[date_cols[0]].dt.date >= data_inicio) & (df[date_cols[0]].dt.date <= data_fim)]
    
    # Filtro por Agente Global
    agente_cols = [col for col in df.columns if 'agente' in col.lower() or 'atendente' in col.lower()]
    if agente_cols:
        with st.sidebar.expander('👤 Agente'):
            agente_selecionado = st.selectbox(
                'Selecione um agente específico (opcional)',
                ['Todos'] + list(df[agente_cols[0]].unique())
            )
            if agente_selecionado != 'Todos':
                df = df[df[agente_cols[0]] == agente_selecionado]
    
    # Métricas principais (baseadas nos filtros globais)
    st.subheader("📈 Métricas Gerais")
    if agente_selecionado != 'Todos':
        st.info(f"📊 Métricas para o agente: **{agente_selecionado}**")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total de Atendimentos", len(df))
    
    with col2:
        if agente_cols:
            st.metric("Agentes Únicos", df[agente_cols[0]].nunique())
        else:
            st.metric("Agentes Únicos", "N/A")
    
    with col3:
        # Métrica de Visitas Técnicas
        visitas_tecnicas = 0
        tipo_cols = [col for col in df.columns if 'tipo' in col.lower()]
        if tipo_cols:
            for col in tipo_cols:
                visitas_tecnicas += df[col].astype(str).str.contains('técnica|tecnica|visita', case=False, na=False).sum()
        st.metric("Visitas Técnicas", visitas_tecnicas)
    
    with col4:
        tempo_cols = [col for col in df.columns if 'tempo' in col.lower() or 'duracao' in col.lower()]
        if tempo_cols:
            tempo_medio = df[tempo_cols[0]].mean()
            st.metric("Tempo Médio", f"{tempo_medio:.1f}")
        else:
            st.metric("Tempo Médio", "N/A")
    
    with col5:
        satisfacao_cols = [col for col in df.columns if 'satisfacao' in col.lower() or 'nota' in col.lower()]
        if satisfacao_cols:
            satisfacao_media = df[satisfacao_cols[0]].mean()
            st.metric("Satisfação Média", f"{satisfacao_media:.1f}")
        else:
            st.metric("Satisfação Média", "N/A")
    
    # Análises
    tab1, tab2, tab3 = st.tabs(['📊 Análise com Filtros', '📋 Dados Filtrados', '📥 Download'])
    
    with tab1:
        # Filtro por Satisfação
        satisfacao_cols = [col for col in df.columns if 'satisfacao' in col.lower() or 'nota' in col.lower()]
        if satisfacao_cols:
            with st.sidebar.expander('Satisfação'):
                satisfacao_range = st.slider(
                    'Selecione a faixa de satisfação',
                    float(df[satisfacao_cols[0]].min()), 
                    float(df[satisfacao_cols[0]].max()), 
                    (float(df[satisfacao_cols[0]].min()), float(df[satisfacao_cols[0]].max()))
                )
        else:
            satisfacao_range = None
        
        # Filtro por Tempo
        tempo_cols = [col for col in df.columns if 'tempo' in col.lower() or 'duracao' in col.lower()]
        if tempo_cols:
            with st.sidebar.expander('Tempo de Atendimento'):
                tempo_range = st.slider(
                    'Selecione a faixa de tempo',
                    float(df[tempo_cols[0]].min()), 
                    float(df[tempo_cols[0]].max()), 
                    (float(df[tempo_cols[0]].min()), float(df[tempo_cols[0]].max()))
                )
        else:
            tempo_range = None
        
        # Aplicar filtros
        filtro_dados = df.copy()
        
        if satisfacao_range and satisfacao_cols:
            filtro_dados = filtro_dados[
                (filtro_dados[satisfacao_cols[0]] >= satisfacao_range[0]) & 
                (filtro_dados[satisfacao_cols[0]] <= satisfacao_range[1])
            ]
        
        if tempo_range and tempo_cols:
            filtro_dados = filtro_dados[
                (filtro_dados[tempo_cols[0]] >= tempo_range[0]) & 
                (filtro_dados[tempo_cols[0]] <= tempo_range[1])
            ]
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            if agente_cols:
                st.subheader("Top 10 Agentes por Atendimentos")
                top_agentes = filtro_dados[agente_cols[0]].value_counts().head(10)
                fig = px.bar(x=top_agentes.values, y=top_agentes.index, orientation='h')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if satisfacao_cols:
                st.subheader("Distribuição de Satisfação")
                fig = px.histogram(filtro_dados, x=satisfacao_cols[0], nbins=10)
                st.plotly_chart(fig, use_container_width=True)
        
        # Performance por agente
        if agente_cols and satisfacao_cols:
            st.subheader("Performance por Agente")
            performance = filtro_dados.groupby(agente_cols[0]).agg({
                satisfacao_cols[0]: 'mean',
                agente_cols[0]: 'count'
            }).rename(columns={agente_cols[0]: 'Total_Atendimentos', satisfacao_cols[0]: 'Satisfacao_Media'})
            
            if tempo_cols:
                performance['Tempo_Medio'] = filtro_dados.groupby(agente_cols[0])[tempo_cols[0]].mean()
            
            st.dataframe(performance.sort_values('Satisfacao_Media', ascending=False), use_container_width=True)
    
    with tab2:
        st.subheader("Dados Filtrados")
        
        # Colunas específicas para exibição (baseadas no arquivo atendimento-agentes.xlsx)
        colunas_especificas = [
            'Atendente Criador', 'Atendente', 'ID Contrato', 'Protocolo', 'Cliente', 'Tipo Geral', 'Tipo Específico', 'Descrição', 'Dt Abertura', 'Dt Conclusão', 'Solução','Cidade', 'Bairro', 'Ponto de Acesso'
            
        ]
        
        # Filtrar apenas colunas que existem no DataFrame
        colunas_disponiveis = [col for col in colunas_especificas if col in filtro_dados.columns]
        
        if colunas_disponiveis:
            filtro_dados_display = filtro_dados[colunas_disponiveis]
        else:
            st.warning("Nenhuma das colunas especificadas foi encontrada no arquivo.")
            filtro_dados_display = filtro_dados
        
        st.dataframe(filtro_dados_display, use_container_width=True)
        st.markdown(f'A tabela possui **{filtro_dados_display.shape[0]}** linhas e **{filtro_dados_display.shape[1]}** colunas')
    
    with tab3:
        st.subheader("Download dos Dados")
        nome_arquivo = st.text_input('Nome do arquivo', value='atendimentos')
        
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