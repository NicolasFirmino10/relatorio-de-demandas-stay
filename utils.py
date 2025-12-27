import streamlit as st
import pandas as pd
from io import BytesIO

def converter_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def converter_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def mensagem_sucesso():
    st.success('Download realizado com sucesso!')