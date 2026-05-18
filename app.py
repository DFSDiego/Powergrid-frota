import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# --- CONFIGURAÇÕES BÁSICAS ---
NUMERO_WHATSAPP = "5511975000422" 
PASTA_FOTOS = "fotos_registradas"
ARQUIVO_CSV = "historico_powergrid.csv"
SENHA_ADMIN = "powergrid123"

# Criar pasta de fotos se não existir
if not os.path.exists(PASTA_FOTOS):
    os.makedirs(PASTA_FOTOS)

st.set_page_config(page_title="Powergrid Energy", page_icon="⚡", layout="centered")

# --- ESTILIZAÇÃO VISUAL (Cores Powergrid) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; }}
    
    /* Títulos e Textos */
    h1, h2, h3, p, b, span, label {{ color: #0054A6 !important; }}

    /* Botão de Registro (Laranja) */
    div.stButton > button:first-child {{
        width: 100%;
        background-color: #F37021 !important;
        color: white !important;
        border-radius: 10px;
        height: 60px;
        font-weight: bold;
        font-size: 20px;
        border: none;
    }}

    /* Botão WhatsApp (Verde) */
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

    /* Estilo dos Radio Buttons (Checklist) */
    .stRadio > div {{ flex-direction: row !important; gap: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO / LOGO ---
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center;'>POWERGRID</h1>", unsafe_allow_html=True)

# CAPTURAR PLACA VIA URL
try:
    placa_url = st.query_params.get("placa", "Não Identificado")
except:
    placa_url = "Não Identificado"

st.markdown(f"<h2 style='text-align: center;'>Veículo: {placa_url}</h2>", unsafe_allow_html=True)
st.markdown("---")

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
    
    st.write("### 📸 Fotos Obrigatórias")
    st.info("As fotos são salvas apenas no sistema da empresa.")
    f1 = st.camera_input("1. Foto do Painel (KM e Combustível)")
    f2 = st.camera_input("2. Foto da Frente do Veículo")
    f3 = st.camera_input("3. Foto Lateral ou Defeito Específico")
    
    submit = st.form_submit_button("REGISTRAR")

# --- PROCESSAMENTO APÓS SUBMISSÃO ---
if submit:
    if not nome:
        st.error("Por favor, informe seu nome para prosseguir.")
    elif not f1 or not f2:
        st.error("Por favor, tire pelo menos as fotos do Painel e da Frente.")
    else:
        agora = datetime.now()
        data_hora = agora.strftime("%d/%m/%Y %H:%M")
        timestamp = agora.strftime("%Y%m%d_%H%M%S")
        
        # 1. Salvar Fotos localmente
        nomes_fotos = []
        for i, foto_arq in enumerate([f1, f2, f3]):
            if foto_arq is not None:
                nome_img = f"{timestamp}_{placa_url}_foto{i+1}.jpg"
                caminho_img = os.path.join(PASTA_FOTOS, nome_img)
                with open(caminho_img, "wb") as f:
                    f.write(foto_arq.getvalue())
                nomes_fotos.append(nome_img)

        # 2. Preparar Dados para CSV
        dados = {
            "Data": [data_hora], "Funcionario": [nome], "Veiculo": [placa_url],
            "Tipo": [tipo], "KM": [km], "Combustivel": [combustivel], 
            "Obs": [defeitos], "Fotos": [", ".join(nomes_fotos)]
        }
        for item, status in respostas.items():
            dados[item] = [status]
            
        df_novo = pd.DataFrame(dados)
        df_novo.to_csv(ARQUIVO_CSV, mode='a', index=False, header=not os.path.exists(ARQUIVO_CSV), encoding='utf-8-sig')
        
        st.success("✅ Registro realizado com sucesso!")

        # 3. Montar Mensagem do WhatsApp
        status_lista = "\n".join([f"{'✅' if v == 'OK' else '❌'} {k}" for k, v in respostas.items()])
        texto_msg = (
            f"*RELATÓRIO DE VEÍCULO - POWERGRID*\n\n"
            f"👤 *Colaborador:* {nome}\n"
            f"🚗 *Veículo:* {placa_url}\n"
            f"📅 *Data:* {data_hora}\n"
            f"📍 *Tipo:* {tipo}\n"
            f"🛣️ *KM:* {km}\n"
            f"⛽ *Combustível:* {combustivel}\n\n"
            f"*CHECKLIST:*\n{status_lista}\n\n"
            f"🛠️ *Obs:* {defeitos if defeitos else 'Tudo em ordem'}\n\n"
            f"📸 *Fotos:* Registradas no servidor."
        )
        
        link_final = f"https://wa.me/{NUMERO_WHATSAPP}?text={urllib.parse.quote(texto_msg)}"
        st.markdown(f'<a href="{link_final}" target="_blank" class="btn-whatsapp">📲 Enviar para o Gestor</a>', unsafe_allow_html=True)
        st.balloons()

# --- ÁREA ADMINISTRATIVA ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("🔐 Acesso Administrativo"):
    pw = st.text_input("Senha", type="password")
    if pw == SENHA_ADMIN:
        if os.path.exists(ARQUIVO_CSV):
            df_adm = pd.read_csv(ARQUIVO_CSV)
            
            st.write("### Histórico de Registros")
            st.dataframe(df_adm)

            st.markdown("---")
            col_adm1, col_adm2 = st.columns(2)
            
            with col_adm1:
                st.write("### 🗑️ Excluir Registro")
                idx_excluir = st.number_input("Index da linha para excluir:", min_value=0, max_value=len(df_adm)-1, step=1)
                confirma = st.checkbox("Confirmo que desejo apagar este registro e suas fotos.")
                if st.button("EXCLUIR DEFINITIVAMENTE"):
                    if confirma:
                        # Apagar fotos associadas
                        fotos_para_deletar = str(df_adm.loc[idx_excluir, "Fotos"]).split(", ")
                        for f_nome in fotos_para_deletar:
                            caminho_f = os.path.join(PASTA_FOTOS, f_nome)
                            if os.path.exists(caminho_f):
                                os.remove(caminho_f)
                        
                        # Atualizar CSV
                        df_adm = df_adm.drop(idx_excluir)
                        df_adm.to_csv(ARQUIVO_CSV, index=False, encoding='utf-8-sig')
                        st.success("Registro removido!")
                        st.rerun()
            
            with col_adm2:
                st.write("### 🖼️ Ver Fotos")
                arquivos_pasta = sorted(os.listdir(PASTA_FOTOS), reverse=True)
                if arquivos_pasta:
                    foto_sel = st.selectbox("Escolha a foto:", arquivos_pasta)
                    st.image(os.path.join(PASTA_FOTOS, foto_sel), use_container_width=True)
                else:
                    st.info("Nenhuma foto salva.")
        else:
            st.info("Nenhum dado registrado ainda.")