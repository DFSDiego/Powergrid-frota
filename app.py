import streamlit as st
import pandas as pd
from datetime import datetime
import os

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Powergrid Energy", page_icon="⚡")

# CSS para cores
st.markdown("""
    <style>
    .stButton>button { width: 100%; background-color: #F37021; color: white; border-radius: 10px; }
    h1, h2, h3 { color: #0054A6 !important; }
    </style>
    """, unsafe_allow_html=True)

# TENTAR CARREGAR A LOGO (Sem travar o app)
try:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=200)
    else:
        st.title("⚡ POWERGRID ENERGY")
except:
    st.title("⚡ POWERGRID ENERGY")

st.markdown("---")

# CAPTURAR PLACA DA URL DE FORMA SEGURA
try:
    placa = st.query_params.get("placa", "Não Identificado")
except:
    placa = "Não Identificado"

st.subheader(f"Veículo: {placa}")

# FORMULÁRIO
with st.container():
    nome = st.text_input("👤 Nome do Colaborador")
    tipo = st.selectbox("Registro", ["Saída", "Retorno"])
    km = st.number_input("KM Atual", min_value=0)
    
    # Combustível conforme solicitado
    combustivel = st.select_slider(
        "Nível de Combustível",
        options=["0 (Reserva)", "1/4", "1/2", "3/4", "1 (Cheio)"],
        value="1/2"
    )

    if combustivel == "0 (Reserva)":
        st.error("⚠️ VEÍCULO NA RESERVA")
    elif combustivel == "1/4":
        st.warning("⛽ Nível Baixo")

    foto = st.camera_input("Foto do Veículo")
    submit = st.button("REGISTRAR")

# SALVAR DADOS
if submit:
    if not nome:
        st.error("Digite seu nome!")
    else:
        dados_novos = {
            "Data": [datetime.now().strftime("%d/%m/%Y %H:%M")],
            "Funcionario": [nome],
            "Veiculo": [placa],
            "Tipo": [tipo],
            "KM": [km],
            "Combustivel": [combustivel]
        }
        df = pd.DataFrame(dados_novos)
        
        # Salva localmente (No Streamlit Cloud, isso é temporário)
        if not os.path.exists('dados.csv'):
            df.to_csv('dados.csv', index=False)
        else:
            df.to_csv('dados.csv', mode='a', header=False, index=False)
            
        st.success("Registrado com sucesso!")
        st.balloons()

# ÁREA GESTOR
with st.expander("Admin"):
    pw = st.text_input("Senha", type="password")
    if pw == "powergrid123":
        if os.path.exists('dados.csv'):
            st.dataframe(pd.read_csv('dados.csv'))