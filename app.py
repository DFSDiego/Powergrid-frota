import streamlit as st
import pandas as pd
from datetime import datetime
import os

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Powergrid Energy", page_icon="⚡", layout="centered")

# --- IDENTIDADE VISUAL (CSS) ---
st.markdown(f"""
    <style>
    /* Fundo e cores principais */
    .stApp {{
        background-color: #FFFFFF;
    }}
    
    /* Títulos em Azul Powergrid */
    h1, h2, h3, p, b {{
        color: #0054A6 !important;
    }}

    /* Botão em Laranja Powergrid */
    .stButton>button {{
        width: 100%;
        background-color: #F37021 !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        height: 50px;
        font-weight: bold;
        font-size: 18px;
    }}
    
    /* Estilização dos Radio Buttons (Checklist) */
    div[data-row='true'] {{
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }}

    /* Centralizar imagem */
    .centered-image {{
        display: flex;
        justify-content: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGOTIPO CENTRALIZADO ---
col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
with col_logo2:
    try:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        elif os.path.exists("logo.jpg"):
            st.image("logo.jpg", use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center;'>POWERGRID</h1>", unsafe_allow_html=True)
    except:
        st.markdown("<h1 style='text-align: center;'>POWERGRID</h1>", unsafe_allow_html=True)

st.markdown("---")

# CAPTURAR PLACA DA URL
try:
    placa = st.query_params.get("placa", "Não Identificado")
except:
    placa = "Não Identificado"

st.markdown(f"<h2 style='text-align: center;'>Veículo: {placa}</h2>", unsafe_allow_html=True)

# --- FORMULÁRIO ---
with st.form("form_registro"):
    nome = st.text_input("👤 Nome do Colaborador")
    
    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        tipo = st.selectbox("Registro", ["Saída", "Retorno"])
    with col_inf2:
        km = st.number_input("KM Atual", min_value=0, step=1)
    
    # INDICADOR DE COMBUSTÍVEL (Conforme solicitado)
    st.write("### ⛽ Nível de Combustível")
    combustivel = st.select_slider(
        "Arraste para indicar o nível",
        options=["0 (Reserva)", "1/4", "1/2", "3/4", "1 (Cheio)"],
        value="1/2"
    )
    
    if "Reserva" in combustivel:
        st.error("⚠️ ATENÇÃO: VEÍCULO NA RESERVA!")

    st.markdown("---")
    
    # --- CHECKLIST (Lado a lado) ---
    st.write("### 📋 Checklist do Veículo")
    
    itens = [
        "Óleo do Motor", "Faróis", "Lanternas", 
        "Pneus", "Limpadores", "Nível de Água"
    ]
    
    respostas = {}
    
    for item in itens:
        col_item, col_radio = st.columns([2, 2])
        with col_item:
            st.write(f"**{item}:**")
        with col_radio:
            # horizontal=True coloca o OK e NÃO OK lado a lado
            respostas[item] = st.radio(
                item, 
                ["OK", "Não OK"], 
                key=item, 
                horizontal=True, 
                label_visibility="collapsed"
            )

    st.markdown("---")
    defeitos = st.text_area("🛠️ Outros Defeitos / Observações", placeholder="Descreva aqui caso haja algum problema...")
    
    foto = st.camera_input("📸 Foto do Painel/Veículo")
    
    submit = st.form_submit_button("REGISTRAR")

# --- SALVAR DADOS ---
if submit:
    if not nome:
        st.error("Por favor, preencha o seu nome!")
    else:
        # Criar dicionário de dados
        dados_registro = {
            "Data": [datetime.now().strftime("%d/%m/%Y %H:%M")],
            "Funcionario": [nome],
            "Veiculo": [placa],
            "Tipo": [tipo],
            "KM": [km],
            "Combustivel": [combustivel],
            "Observacoes": [defeitos]
        }
        # Adiciona checklist ao dicionário
        for item, status in respostas.items():
            dados_registro[item] = [status]
            
        df = pd.DataFrame(dados_registro)
        
        # Salva em CSV
        arquivo = 'dados_powergrid.csv'
        if not os.path.exists(arquivo):
            df.to_csv(arquivo, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(arquivo, mode='a', header=False, index=False, encoding='utf-8-sig')
            
        st.success("✅ Registro concluído com sucesso!")
        st.balloons()

# --- ADMIN ---
with st.expander("Acesso Administrativo"):
    pw = st.text_input("Senha", type="password")
    if pw == "powergrid123":
        if os.path.exists('dados_powergrid.csv'):
            st.dataframe(pd.read_csv('dados_powergrid.csv'))
        else:
            st.info("Nenhum registro encontrado.")