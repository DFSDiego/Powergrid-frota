import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# --- CONFIGURAÇÕES ---
NUMERO_WHATSAPP = "5511975000422" 
PASTA_FOTOS = "fotos_registradas"
ARQUIVO_CSV = "historico_powergrid.csv"
SENHA_ADMIN = "powergrid123"

if not os.path.exists(PASTA_FOTOS):
    os.makedirs(PASTA_FOTOS)

st.set_page_config(page_title="Powergrid Energy", page_icon="⚡", layout="centered")

# --- ESTILO ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; }}
    h1, h2, h3, p, b, span, label {{ color: #0054A6 !important; }}
    div.stButton > button:first-child {{
        width: 100%;
        background-color: #F37021 !important;
        color: white !important;
        border-radius: 10px;
        height: 60px;
        font-weight: bold;
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
        margin-top: 10px;
    }}
    .stRadio > div {{ flex-direction: row !important; gap: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center;'>POWERGRID</h1>", unsafe_allow_html=True)

try:
    placa = st.query_params.get("placa", "Não Identificado")
except:
    placa = "Não Identificado"

st.markdown(f"<h2 style='text-align: center;'>Veículo: {placa}</h2>", unsafe_allow_html=True)
st.markdown("---")

# --- FORMULÁRIO ---
with st.form("form_powergrid"):
    nome = st.text_input("👤 Nome do Colaborador")
    
    c1, c2 = st.columns(2)
    with c1: tipo = st.selectbox("Registro", ["Saída", "Retorno"])
    with c2: km = st.number_input("KM Atual", min_value=0, step=1)
    
    combustivel = st.select_slider("⛽ Combustível", options=["Reserva", "1/4", "1/2", "3/4", "1"], value="1/2")
    
    st.markdown("### 📋 Checklist")
    itens = ["Óleo Motor", "Faróis", "Lanternas", "Pneus", "Limpadores", "Água"]
    respostas = {}
    for item in itens:
        cols = st.columns([2, 2])
        with cols[0]: st.write(f"**{item}**")
        with cols[1]: respostas[item] = st.radio(item, ["OK", "Não OK"], key=item, horizontal=True, label_visibility="collapsed")

    defeitos = st.text_area("🛠️ Observações")
    
    st.write("### 📸 Fotos")
    f1 = st.camera_input("Painel (KM)")
    f2 = st.camera_input("Frente")
    f3 = st.camera_input("Lateral/Avaria")
    
    enviar = st.form_submit_button("REGISTRAR")

# --- LÓGICA DE SALVAMENTO ROBUSTA ---
if enviar:
    if not nome or not f1:
        st.error("Preencha o nome e tire a foto do painel!")
    else:
        agora = datetime.now()
        data_txt = agora.strftime("%d/%m/%Y %H:%M")
        ts = agora.strftime("%Y%m%d_%H%M%S")
        
        # 1. Salvar Fotos
        nomes_fotos = []
        for i, foto in enumerate([f1, f2, f3]):
            if foto:
                nome_f = f"{ts}_{placa}_f{i+1}.jpg"
                with open(os.path.join(PASTA_FOTOS, nome_f), "wb") as f:
                    f.write(foto.getvalue())
                nomes_fotos.append(nome_f)

        # 2. Criar DataFrame da nova linha
        novo_registro = {
            "Data": data_txt, "Funcionario": nome, "Veiculo": placa,
            "Tipo": tipo, "KM": km, "Combustivel": combustivel,
            "Obs": defeitos.replace("\n", " "), "Fotos": ", ".join(nomes_fotos)
        }
        for k, v in respostas.items():
            novo_registro[k] = v
        
        df_nova_linha = pd.DataFrame([novo_registro])

        # 3. SALVAR (Modo Robusto: Lê tudo, concatena e salva)
        if os.path.exists(ARQUIVO_CSV):
            try:
                df_antigo = pd.read_csv(ARQUIVO_CSV)
                df_final = pd.concat([df_antigo, df_nova_linha], ignore_index=True)
            except:
                # Se o arquivo estiver corrompido, ele ignora o antigo e cria um novo
                df_final = df_nova_linha
        else:
            df_final = df_nova_linha
            
        df_final.to_csv(ARQUIVO_CSV, index=False, encoding='utf-8-sig')
        
        st.success("✅ Salvo!")
        
        # WhatsApp
        msg = f"*CHECKLIST POWERGRID*\n👤 {nome}\n🚗 {placa}\n🛣️ {km} KM\n\n📸 Fotos no servidor."
        link = f"https://wa.me/{NUMERO_WHATSAPP}?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{link}" target="_blank" class="btn-whatsapp">📲 Enviar WhatsApp</a>', unsafe_allow_html=True)
        st.balloons()

# --- ADMIN ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("🔐 Administração"):
    if st.text_input("Senha", type="password") == SENHA_ADMIN:
        if os.path.exists(ARQUIVO_CSV):
            try:
                df_adm = pd.read_csv(ARQUIVO_CSV)
                st.dataframe(df_adm)
                
                # Deletar
                st.write("---")
                idx = st.number_input("Linha para apagar:", 0, max(0, len(df_adm)-1), 0)
                if st.button("Confirmar Exclusão"):
                    # Apagar fotos
                    f_str = str(df_adm.loc[idx, "Fotos"])
                    if f_str != "nan":
                        for f_n in f_str.split(", "):
                            c_f = os.path.join(PASTA_FOTOS, f_n.strip())
                            if os.path.exists(c_f): os.remove(c_f)
                    # Salvar CSV
                    df_adm.drop(idx).to_csv(ARQUIVO_CSV, index=False, encoding='utf-8-sig')
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao ler histórico. Sugerimos apagar o arquivo CSV. Detalhe: {e}")
                if st.button("Apagar arquivo corrompido agora"):
                    os.remove(ARQUIVO_CSV)
                    st.rerun()