import streamlit as st
import pandas as pd
from dataset import df, analise_solicitacao, analise_categoria, top_clientes

st.set_page_config(layout='wide', page_title='Análise Stay - Dashboard')

# Sidebar para navegação
st.sidebar.title("📊 Análise Stay")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏠 Página Principal")
st.sidebar.info("Esta é a página principal com dados pré-carregados")
st.sidebar.markdown("### 📄 Outras Páginas")
st.sidebar.markdown("- 📊 Recorrência de Demandas")
st.sidebar.markdown("- 👥 Entradas e Saídas")
st.sidebar.markdown("- 🎧 Atendimentos dos Agentes")
st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Dica:** Use as páginas acima para fazer upload de seus próprios arquivos!")

st.title("🏠 Dashboard Principal - Análise de Recorrência de Demandas")
st.markdown("*Dados pré-carregados do sistema*")

# Métricas principais
st.subheader("📈 Métricas Gerais")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Registros", len(df))

with col2:
    st.metric("Total de Demandas", int(df['QTD. No Periodo'].sum()))

with col3:
    st.metric("Clientes Únicos", df['Cliente'].nunique())

with col4:
    st.metric("Tipos de Solicitação", df['Tipo de Solicitação'].nunique())

# Abas para organizar as análises
aba1, aba2, aba3, aba4 = st.tabs(['Tipos de Solicitação', 'Categorias', 'Top Clientes', 'Dados Completos'])

with aba1:
    st.subheader("Análise por Tipo de Solicitação")
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(analise_solicitacao.sort_values('Total_Demandas', ascending=False))
    
    with col2:
        st.bar_chart(analise_solicitacao.set_index('Tipo de Solicitação')['Total_Demandas'].head(10))

with aba2:
    st.subheader("Análise por Categoria")
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(analise_categoria.sort_values('Total_Demandas', ascending=False))
    
    with col2:
        st.bar_chart(analise_categoria.set_index('Categoria 1')['Total_Demandas'].head(10))

with aba3:
    st.subheader("Top 20 Clientes com Mais Demandas")
    st.dataframe(top_clientes)
    

with aba4:
    st.subheader("Dados Completos")
    st.dataframe(df)

# Rodapé
st.markdown("---")
st.markdown("### 🚀 Próximos Passos")
st.info("""Para análises personalizadas com seus próprios dados, acesse as páginas específicas:
- **Recorrência de Demandas**: Upload de arquivos de demandas personalizados
- **Entradas e Saídas**: Análise de movimentação de funcionários
- **Atendimentos dos Agentes**: Performance e métricas de atendimento
""")