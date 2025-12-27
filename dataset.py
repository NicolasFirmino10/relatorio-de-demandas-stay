import pandas as pd

# Lendo o arquivo CSV com separador correto
df = pd.read_csv('dados/Recorrência de Demandas.csv', sep=';', encoding='utf-8')

# Limpeza e processamento dos dados
df['QTD. No Periodo'] = pd.to_numeric(df['QTD. No Periodo'], errors='coerce')

# Análise por tipo de solicitação
analise_solicitacao = df.groupby('Tipo de Solicitação').agg({
    'QTD. No Periodo': ['sum', 'count', 'mean']
}).round(2)
analise_solicitacao.columns = ['Total_Demandas', 'Num_Clientes', 'Media_Por_Cliente']
analise_solicitacao = analise_solicitacao.reset_index()

# Análise por categoria
analise_categoria = df.groupby('Categoria 1').agg({
    'QTD. No Periodo': ['sum', 'count', 'mean']
}).round(2)
analise_categoria.columns = ['Total_Demandas', 'Num_Clientes', 'Media_Por_Cliente']
analise_categoria = analise_categoria.reset_index()

# Análise por matriz
analise_matriz = df.groupby('Matriz').agg({
    'QTD. No Periodo': ['sum', 'count', 'mean']
}).round(2)
analise_matriz.columns = ['Total_Demandas', 'Num_Clientes', 'Media_Por_Cliente']
analise_matriz = analise_matriz.reset_index()

# Top clientes com mais demandas (agrupando por cliente)
top_clientes_agrupado = df.groupby('Cliente').agg({
    'QTD. No Periodo': 'sum',
    'Tipo de Solicitação': lambda x: ', '.join(x.unique()),
    'Categoria 1': lambda x: ', '.join(x.unique())
}).reset_index()
top_clientes = top_clientes_agrupado.nlargest(20, 'QTD. No Periodo')