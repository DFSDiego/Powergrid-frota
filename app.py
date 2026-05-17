import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# --- CONFIGURAÇÃO DO GESTOR ---
NUMERO_WHATSAPP = "5511975000422" 

st.set_page_config(page_title="Powergrid Energy", page_icon="⚡", layout="centered")

# --- ESTILIZAÇÃO VISUAL (Cores Powergrid: Azul #0054A6, Laranja #F37021) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; }}
    
    /* Títulos e Textos em Azul */
    h1, h2, h3, p, b, span, label {{ 
        color: #0054A6 !important; 
    }}

    /* Botão Principal em Laranja */
    div.stButton > button:first-child {{
        width: 100%;
        background-color: #F37021 !important;
        color: white !important;
        border-radius: 10px;
        height: 55px;
        font-weight: bold;
        font-size: 18px;
        border: none;
    }}

    /* Botão do WhatsApp (Verde) */
    .btn-whatsapp {{
        display: block;
        width: 100%;
        background-color: #25D366;
        color: white !important;
        text-align: center;
        padding: 15px;
        text-decoration: none;
        border-radius: 10px;
        font-weight: bold;
        font-size: 18px;
        margin-top: 15px;
    }}

    /* Checklist: Botões de rádio lado a lado */
    .stRadio > div {{ 
        flex-direction: row !important; 
        gap: 30px; 
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGOTIPO CENTRALIZADO ---
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center;'>POWERGRID</h1>", unsafe_allow_html=True)

st.markdown("---")

# CAPTURAR PLACA VIA URL
try:
    placa = st.query_params.get("placa", "Não Identificado")
except:
    placa = "Não Identificado"

st.markdown(f"<h2 style='text-align: center;'>Veículo: {placa}</h2>", unsafe_allow_html=True)

# --- FORMULÁRIO DE REGISTRO ---
with st.form("form_powergrid", clear_on_submit=False):
    nome = st.text_input("👤 Nome do Colaborador")
    
    c_tipo, c_km = st.columns(2)
    with c_tipo:
        tipo = st.selectbox("Registro", ["Saída", "Retorno"])
    with c_km:
        km = st.number_input("KM Atual", min_value=0, step=1)
    
    st.write("### ⛽ Nível de Combustível")
    combustivel = st.select_slider(
        "Arraste para selecionar",
        options=["Reserva", "1/4", "1/2", "3/4", "1"],
        value="1/2"
    )
    if combustivel == "Reserva":
        st.error("⚠️ ATENÇÃO: VEÍCULO NA RESERVA!")

    st.markdown("---")
    st.write("### 📋 Checklist de Segurança")
    
    itens = ["Óleo do Motor", "Faróis", "Lanternas", "Pneus", "Limpadores", "Nível de Água"]
    respostas = {}
    
    for item in itens:
        col_txt, col_opt = st.columns([2, 2])
        with col_txt:
            st.write(f"**{item}**")
        with col_opt:
            respostas[item] = st.radio(item, ["OK", "Não OK"], key=item, horizontal=True, label_visibility="collapsed")

    st.markdown("---")
    defeitos = st.text_area("🛠️ Outros Defeitos / Observações", placeholder="Relate aqui qualquer barulho ou problema...")
    
    foto = st.camera_input("📸 Foto do Painel/Veículo")
    
    submit = st.form_submit_button("REGISTRAR")

# --- PROCESSAMENTO APÓS SUBMISSÃO ---
if submit:
    if not nome:
        st.error("Por favor, informe seu nome para prosseguir.")
    else:
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Salvar Dados localmente (Base histórica)
        dados = {
            "Data": [data_hora], "Funcionario": [nome], "Veiculo": [placa],
            "Tipo": [tipo], "KM": [km], "Combustivel": [combustivel], "Obs": [defeitos]
        }
        for item, status in respostas.items():
            dados[item] = [status]
            
        df = pd.DataFrame(dados)
        arquivo = 'historico_powergrid.csv'
        df.to_csv(arquivo, mode='a', index=False, header=not os.path.exists(arquivo), encoding='utf-8-sig')
        
        st.success("✅ Registro realizado com sucesso!")

        # Montar Mensagem do WhatsApp
        status_lista = "\n".join([f"{'✅' if v == 'OK' else '❌'} {k}" for k, v in respostas.items()])
        texto_msg = (
            f"*RELATÓRIO DE VEÍCULO - POWERGRID*\n\n"
            f"👤 *Colaborador:* {nome}\n"
            f"🚗 *Veículo:* {placa}\n"
            f"📅 *Data:* {data_hora}\n"
            f"📍 *Tipo:* {tipo}\n"
            f"🛣️ *KM:* {km}\n"
            f"⛽ *Combustível:* {combustivel}\n\n"
            f"*CHECKLIST:*\n{status_lista}\n\n"
            f"🛠️ *Obs:* {defeitos if defeitos else 'Tudo em ordem'}"
        )
        
        link_final = f"https://wa.me/{NUMERO_WHATSAPP}?text={urllib.parse.quote(texto_msg)}"

        # Exibir Botão de Envio
        st.markdown(f'<a href="{link_final}" target="_blank" class="btn-whatsapp">📲 Enviar para o Gestor</a>', unsafe_allow_html=True)
        st.balloons()

# --- ADMIN ---
with st.expander("Acesso Administrativo"):
    pw = st.text_input("Senha", type="password")
    if pw == "powergrid123":
        if os.path.exists('historico_powergrid.csv'):
            st.dataframe(pd.read_csv('historico_powergrid.csv'))