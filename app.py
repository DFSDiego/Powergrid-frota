import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# --- CONFIGURAÇÕES ---
NUMERO_WHATSAPP = "5511975000422" 
PASTA_FOTOS = "fotos_registradas"

# Criar a pasta de fotos se não existir
if not os.path.exists(PASTA_FOTOS):
    os.makedirs(PASTA_FOTOS)

st.set_page_config(page_title="Powergrid Energy", page_icon="⚡", layout="centered")

# --- ESTILIZAÇÃO VISUAL ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; }}
    h1, h2, h3, p, b, span, label {{ color: #0054A6 !important; }}
    div.stButton > button:first-child {{
        width: 100%;
        background-color: #F37021 !important;
        color: white !important;
        border-radius: 10px;
        height: 55px;
        font-weight: bold;
        font-size: 18px;
    }}
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
    </style>
    """, unsafe_allow_html=True)

# --- LOGOTIPO ---
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center;'>POWERGRID</h1>", unsafe_allow_html=True)

st.markdown("---")

# CAPTURAR PLACA
try:
    placa = st.query_params.get("placa", "Não Identificado")
except:
    placa = "Não Identificado"

st.markdown(f"<h2 style='text-align: center;'>Veículo: {placa}</h2>", unsafe_allow_html=True)

# --- FORMULÁRIO ---
with st.form("form_powergrid", clear_on_submit=False):
    nome = st.text_input("👤 Nome do Colaborador")
    
    c_tipo, c_km = st.columns(2)
    with c_tipo:
        tipo = st.selectbox("Registro", ["Saída", "Retorno"])
    with c_km:
        km = st.number_input("KM Atual", min_value=0, step=1)
    
    st.write("### ⛽ Nível de Combustível")
    combustivel = st.select_slider("Nível", options=["Reserva", "1/4", "1/2", "3/4", "1"], value="1/2")

    st.markdown("---")
    st.write("### 📋 Checklist")
    itens = ["Óleo do Motor", "Faróis", "Lanternas", "Pneus", "Limpadores", "Nível de Água"]
    respostas = {}
    for item in itens:
        col_txt, col_opt = st.columns([2, 2])
        with col_txt: st.write(f"**{item}**")
        with col_opt: respostas[item] = st.radio(item, ["OK", "Não OK"], key=item, horizontal=True, label_visibility="collapsed")

    defeitos = st.text_area("🛠️ Observações/Defeitos")

    st.markdown("---")
    st.write("### 📸 Fotos do Veículo")
    f1 = st.camera_input("1. Foto do Painel (KM/Combustível)")
    f2 = st.camera_input("2. Frente do Veículo")
    f3 = st.camera_input("3. Lateral/Traseira ou Defeito")
    
    submit = st.form_submit_button("REGISTRAR")

# --- PROCESSAMENTO ---
if submit:
    if not nome:
        st.error("Por favor, informe seu nome.")
    else:
        agora = datetime.now()
        data_str = agora.strftime("%d/%m/%Y %H:%M")
        timestamp = agora.strftime("%Y%m%d_%H%M%S")
        
        # Salvar fotos localmente
        fotos_salvas = []
        for i, f in enumerate([f1, f2, f3]):
            if f is not None:
                nome_foto = f"{timestamp}_{placa}_foto{i+1}.jpg"
                caminho_foto = os.path.join(PASTA_FOTOS, nome_foto)
                with open(caminho_foto, "wb") as arquivo_foto:
                    arquivo_foto.write(f.getvalue())
                fotos_salvas.append(nome_foto)

        # Salvar Dados no CSV
        dados = {
            "Data": [data_str], "Funcionario": [nome], "Veiculo": [placa],
            "Tipo": [tipo], "KM": [km], "Combustivel": [combustivel], 
            "Obs": [defeitos], "Fotos": [", ".join(fotos_salvas)]
        }
        for item, status in respostas.items():
            dados[item] = [status]
            
        df = pd.DataFrame(dados)
        arquivo_csv = 'historico_powergrid.csv'
        df.to_csv(arquivo_csv, mode='a', index=False, header=not os.path.exists(arquivo_csv), encoding='utf-8-sig')
        
        st.success("✅ Registro e Fotos salvos com sucesso!")

        # Link WhatsApp
        status_lista = "\n".join([f"{'✅' if v == 'OK' else '❌'} {k}" for k, v in respostas.items()])
        texto_msg = f"*RELATÓRIO POWERGRID*\n\n👤 {nome}\n🚗 {placa}\n📍 {tipo}\n🛣️ {km} KM\n⛽ {combustivel}\n\n*CHECKLIST:*\n{status_lista}\n\n📸 Fotos registradas no sistema."
        link_final = f"https://wa.me/{NUMERO_WHATSAPP}?text={urllib.parse.quote(texto_msg)}"
        
        st.markdown(f'<a href="{link_final}" target="_blank" class="btn-whatsapp">📲 Enviar Relatório para o Gestor</a>', unsafe_allow_html=True)
        st.balloons()

# --- ADMIN ---
st.markdown("---")
with st.expander("🔐 Acesso Administrativo (Visualizar Registros e Fotos)"):
    pw = st.text_input("Senha", type="password")
    if pw == "powergrid123":
        if os.path.exists('historico_powergrid.csv'):
            df_hist = pd.read_csv('historico_powergrid.csv')
            st.dataframe(df_hist)
            
            st.write("### 🖼️ Galeria de Fotos Recentes")
            lista_fotos = sorted(os.listdir(PASTA_FOTOS), reverse=True)
            if lista_fotos:
                foto_selecionada = st.selectbox("Selecione uma foto para visualizar:", lista_fotos)
                st.image(os.path.join(PASTA_FOTOS, foto_selecionada), use_container_width=True)
            else:
                st.info("Nenhuma foto encontrada.")
        else:
            st.info("Ainda não há registros.")