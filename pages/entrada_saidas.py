import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils import converter_csv, converter_excel, mensagem_sucesso

st.set_page_config(layout='wide', page_title='Entrada e Saídas dos Agentes')
st.title('🕐 Análise de Entrada e Saídas dos Agentes')

# Função para converter duração HH:MM:SS para minutos
def duracao_para_minutos(duracao_str):
    if pd.isna(duracao_str) or duracao_str == "":
        return 0
    try:
        h, m, s = map(int, duracao_str.split(':'))
        return h * 60 + m + s / 60
    except:
        return 0

# Opção de fonte de dados
data_source = st.radio(
    "Escolha a fonte dos dados:",
    ["📁 Upload de arquivo", "💾 Dados padrão do sistema"]
)

if data_source == "📁 Upload de arquivo":
    st.subheader("📁 Upload de Dados")
    
    # Botão para limpar dados
    if st.button("🗑️ Limpar Dados Carregados"):
        if 'uploaded_data_entrada_saidas' in st.session_state:
            del st.session_state.uploaded_data_entrada_saidas
        st.rerun()
    
    uploaded_file = st.file_uploader(
        "Faça upload do arquivo de acompanhamento de agentes (CSV ou Excel)", 
        type=['csv', 'xlsx', 'xls']
    )
    
    # Verificar se já existe dados na sessão
    if 'uploaded_data_entrada_saidas' in st.session_state:
        df = st.session_state.uploaded_data_entrada_saidas
        st.success(f"Arquivo já carregado! {len(df)} registros encontrados.")
    elif uploaded_file is not None:
        try:
            # Carrega o arquivo
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, sep=';')
            else:
                df = pd.read_excel(uploaded_file)
            
            # Salvar na sessão
            st.session_state.uploaded_data_entrada_saidas = df
            st.success(f"Arquivo carregado com sucesso! {len(df)} registros encontrados.")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {str(e)}")
            df = None
    else:
        st.info("👆 Faça upload de um arquivo para começar a análise")
        st.markdown("""
        ### 📋 Formato esperado do arquivo:
        - **CSV** ou **Excel** (.xlsx, .xls)
        - Colunas: Usuario, Dia, Data Evento 1, Tipo Evento 1, Data Evento 2, Tipo Evento 2, Duracao
        - Representa logs de mudanças de status dos atendentes
        """)
        df = None
else:
    # Carregar dados padrão
    try:
        df = pd.read_csv('dados/Acompanhamento de Atendentes - Omnidesk.csv', sep=';')
        st.success(f"Dados padrão carregados! {len(df)} registros encontrados.")
    except:
        st.info("💾 Dados padrão não disponíveis. Faça upload de um arquivo.")
        df = None

if df is not None:
    # Processamento dos dados
    df['Duracao_Minutos'] = df['Duracao'].apply(duracao_para_minutos)
    df['Dia'] = pd.to_datetime(df['Dia'], dayfirst=True, errors='coerce')
    
    # Filtros globais
    st.sidebar.title('🔍 Filtros Globais')
    
    # Filtro por período
    with st.sidebar.expander('📅 Período'):
        data_min = df['Dia'].min().date()
        data_max = df['Dia'].max().date()
        
        data_inicio = st.date_input('Data início', value=data_min, min_value=data_min, max_value=data_max, format='DD/MM/YYYY')
        data_fim = st.date_input('Data fim', value=data_max, min_value=data_min, max_value=data_max, format='DD/MM/YYYY')
        
        df_filtrado = df[(df['Dia'].dt.date >= data_inicio) & (df['Dia'].dt.date <= data_fim)]
    
    # Filtro por usuário
    with st.sidebar.expander('👤 Usuário'):
        usuario_selecionado = st.selectbox(
            'Selecione um usuário específico (opcional)',
            ['Todos'] + list(df_filtrado['Usuario'].unique())
        )
        if usuario_selecionado != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Usuario'] == usuario_selecionado]
    
    # Filtro por tipo de evento
    with st.sidebar.expander('📊 Tipo de Status'):
        tipos_evento = df_filtrado['Tipo Evento 1'].unique()
        tipos_selecionados = st.multiselect(
            'Selecione os tipos de status',
            tipos_evento,
            default=tipos_evento
        )
        df_filtrado = df_filtrado[df_filtrado['Tipo Evento 1'].isin(tipos_selecionados)]
    
    # Métricas principais
    st.subheader("📈 Métricas Gerais")
    if usuario_selecionado != 'Todos':
        st.info(f"📊 Métricas para o usuário: **{usuario_selecionado}**")
    
    # Calcular métricas por tipo de evento
    metricas_por_tipo = df_filtrado.groupby('Tipo Evento 1')['Duracao_Minutos'].sum()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        tempo_online = metricas_por_tipo.get('Online', 0)
        st.metric("Tempo Online", f"{tempo_online:.0f} min")
    
    with col2:
        tempo_offline = metricas_por_tipo.get('Offline', 0)
        st.metric("Tempo Offline", f"{tempo_offline:.0f} min")
    
    with col3:
        tempo_alta_demanda = metricas_por_tipo.get('Alta demanda', 0)
        st.metric("Tempo Alta Demanda", f"{tempo_alta_demanda:.0f} min")
    
    with col4:
        tempo_total = metricas_por_tipo.sum()
        tempo_produtivo = tempo_online + tempo_alta_demanda
        percentual_produtivo = (tempo_produtivo / tempo_total * 100) if tempo_total > 0 else 0
        st.metric("% Tempo Produtivo", f"{percentual_produtivo:.1f}%")
    
    with col5:
        usuarios_unicos = df_filtrado['Usuario'].nunique()
        st.metric("Usuários Únicos", usuarios_unicos)
    
    # Análises
    tab1, tab2, tab3 = st.tabs(['📊 Análise Detalhada', '📋 Dados Filtrados', '📥 Download'])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Tempo Total por Status")
            fig_status = px.bar(
                x=metricas_por_tipo.values,
                y=metricas_por_tipo.index,
                orientation='h',
                title="Distribuição de Tempo por Status"
            )
            fig_status.update_layout(xaxis_title="Tempo (minutos)", yaxis_title="Status")
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            st.subheader("Proporção dos Status")
            fig_pie = px.pie(
                values=metricas_por_tipo.values,
                names=metricas_por_tipo.index,
                title="Proporção de Tempo por Status"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Análise por usuário
        st.subheader("Performance por Usuário")
        performance_usuario = df_filtrado.groupby(['Usuario', 'Tipo Evento 1'])['Duracao_Minutos'].sum().unstack(fill_value=0)
        
        if not performance_usuario.empty:
            # Calcular totais e percentuais
            performance_usuario['Total'] = performance_usuario.sum(axis=1)
            if 'Online' in performance_usuario.columns and 'Alta demanda' in performance_usuario.columns:
                performance_usuario['Tempo_Produtivo'] = performance_usuario.get('Online', 0) + performance_usuario.get('Alta demanda', 0)
                performance_usuario['%_Produtivo'] = (performance_usuario['Tempo_Produtivo'] / performance_usuario['Total'] * 100).round(1)
            
            st.dataframe(performance_usuario.sort_values('Total', ascending=False), use_container_width=True)
            
            # Gráfico stacked por usuário
            st.subheader("Distribuição de Tempo por Usuário")
            fig_stacked = px.bar(
                df_filtrado.groupby(['Usuario', 'Tipo Evento 1'])['Duracao_Minutos'].sum().reset_index(),
                x='Usuario',
                y='Duracao_Minutos',
                color='Tipo Evento 1',
                title="Tempo por Status por Usuário"
            )
            fig_stacked.update_layout(xaxis_title="Usuário", yaxis_title="Tempo (minutos)")
            st.plotly_chart(fig_stacked, use_container_width=True)
    
    with tab2:
        st.subheader("Dados Filtrados")
        
        # Colunas para exibição
        colunas_exibicao = ['Usuario', 'Dia', 'Data Evento 1', 'Tipo Evento 1', 'Data Evento 2', 'Tipo Evento 2', 'Duracao', 'Duracao_Minutos']
        colunas_disponiveis = [col for col in colunas_exibicao if col in df_filtrado.columns]
        
        st.dataframe(df_filtrado[colunas_disponiveis], use_container_width=True)
        st.markdown(f'A tabela possui **{df_filtrado.shape[0]}** linhas e **{df_filtrado.shape[1]}** colunas')
    
    with tab3:
        st.subheader("Download dos Dados")
        nome_arquivo = st.text_input('Nome do arquivo', value='entrada_saidas')
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                '📥 Download CSV',
                data=converter_csv(df_filtrado),
                file_name=f'{nome_arquivo}.csv',
                mime='text/csv',
                on_click=mensagem_sucesso
            )
        
        with col2:
            st.download_button(
                '📥 Download Excel',
                data=converter_excel(df_filtrado),
                file_name=f'{nome_arquivo}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                on_click=mensagem_sucesso
            )