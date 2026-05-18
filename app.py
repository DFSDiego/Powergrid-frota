import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# --- CONFIGURAÇÕES GERAIS ---
NUMERO_WHATSAPP = "5511975000422" 
PASTA_FOTOS = "fotos_registradas"
ARQUIVO_CSV = "historico_powergrid.csv"
SENHA_ADMIN = "powergrid123"

# Criar infraestrutura inicial
if not os.path.exists(PASTA_FOTOS):
    os.makedirs(PASTA_FOTOS)

st.set_page_config(page_title="Powergrid Energy", page_icon="⚡", layout="centered")

# --- ESTILO VISUAL POWERGRID ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; }}
    h1, h2, h3, p, b, span, label {{ color: #0054A6 !important; }}
    
    /* Botão de Registro (Laranja) */
    div.stButton > button:first-child {{
        width: 100%;
        background-color: #F37021 !important;
        color: white !important;
        border-radius: 10px;
        height: 60px;
        font-weight: bold;
        font-size: 18px;
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
        margin-top: 10px;
    }}

    /* Checklist Horizontal */
    .stRadio > div {{ flex-direction: row !important; gap: 25px; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGO ---
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center;'>POWERGRID</h1>", unsafe_allow_html=True)

# --- IDENTIFICAÇÃO DO VEÍCULO ---
try:
    placa_veiculo = st.query_params.get("placa", "Não Identificado")
except:
    placa_veiculo = "Não Identificado"

st.markdown(f"<h2 style='text-align: center;'>Veículo: {placa_veiculo}</h2>", unsafe_allow_html=True)
st.markdown("---")

# --- FORMULÁRIO ---
with st.form("form_powergrid", clear_on_submit=False):
    nome = st.text_input("👤 Nome do Colaborador")
    
    col_1, col_2 = st.columns(2)
    with col_1:
        tipo_reg = st.selectbox("Registro", ["Saída", "Retorno"])
    with col_2:
        km_atual = st.number_input("KM Atual", min_value=0, step=1)
    
    st.write("### ⛽ Nível de Combustível")
    combustivel = st.select_slider("Selecione o nível", options=["Reserva", "1/4", "1/2", "3/4", "1"], value="1/2")
    if combustivel == "Reserva":
        st.warning("⚠️ Atenção: Veículo na reserva!")

    st.markdown("---")
    st.write("### 📋 Checklist de Segurança")
    itens_check = ["Óleo Motor", "Faróis", "Lanternas", "Pneus", "Limpadores", "Água/Arrefecimento"]
    respostas = {}
    for item in itens_check:
        c1, c2 = st.columns([2, 2])
        with c1: st.write(f"**{item}**")
        with c2: respostas[item] = st.radio(item, ["OK", "Não OK"], key=item, horizontal=True, label_visibility="collapsed")

    st.markdown("---")
    obs_defeitos = st.text_area("🛠️ Observações ou Defeitos", placeholder="Descreva qualquer problema...")

    st.write("### 📸 Fotos do Registro")
    st.caption("As fotos são salvas apenas no servidor da Powergrid.")
    f1 = st.camera_input("Foto 1: Painel (KM/Combustível)")
    f2 = st.camera_input("Foto 2: Frente do Veículo")
    f3 = st.camera_input("Foto 3: Lateral ou Avaria")
    
    btn_enviar = st.form_submit_button("REGISTRAR AGORA")

# --- LÓGICA DE SALVAMENTO ---
if btn_enviar:
    if not nome:
        st.error("Erro: Informe o nome do colaborador!")
    elif not f1:
        st.error("Erro: A foto do painel é obrigatória!")
    else:
        agora = datetime.now()
        data_txt = agora.strftime("%d/%m/%Y %H:%M")
        timestamp = agora.strftime("%Y%m%d_%H%M%S")
        
        # Salvar Fotos
        lista_nomes_fotos = []
        for i, foto_data in enumerate([f1, f2, f3]):
            if foto_data:
                nome_arq = f"{timestamp}_{placa_veiculo}_foto{i+1}.jpg"
                caminho_salvar = os.path.join(PASTA_FOTOS, nome_arq)
                with open(caminho_salvar, "wb") as f:
                    f.write(foto_data.getvalue())
                lista_nomes_fotos.append(nome_arq)

        # Salvar no CSV
        novos_dados = {
            "Data": [data_txt], "Funcionario": [nome], "Veiculo": [placa_veiculo],
            "Tipo": [tipo_reg], "KM": [km_atual], "Combustivel": [combustivel],
            "Obs": [obs_defeitos], "Fotos": [", ".join(lista_nomes_fotos)]
        }
        for k, v in respostas.items():
            novos_dados[k] = [v]
        
        df_novo = pd.DataFrame(novos_dados)
        df_novo.to_csv(ARQUIVO_CSV, mode='a', index=False, header=not os.path.exists(ARQUIVO_CSV), encoding='utf-8-sig')
        
        st.success("✅ Registro salvo com sucesso no banco de dados!")

        # Gerar Link WhatsApp
        msg_wpp = f"*CHECKLIST POWERGRID*\n\n👤 {nome}\n🚗 {placa_veiculo}\n📍 {tipo_reg}\n🛣️ KM: {km_atual}\n⛽ Fuel: {combustivel}\n\n"
        for k, v in respostas.items():
            icon = "✅" if v == "OK" else "❌"
            msg_wpp += f"{icon} {k}\n"
        msg_wpp += f"\n🛠️ Obs: {obs_defeitos if obs_defeitos else 'Nenhuma'}"
        
        link_wpp = f"https://wa.me/{NUMERO_WHATSAPP}?text={urllib.parse.quote(msg_wpp)}"
        st.markdown(f'<a href="{link_wpp}" target="_blank" class="btn-whatsapp">📲 Enviar para o Gestor (WhatsApp)</a>', unsafe_allow_html=True)
        st.balloons()

# --- ÁREA DO ADMINISTRADOR ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
with st.expander("🔐 Acesso Administrativo"):
    senha = st.text_input("Senha de acesso", type="password")
    if senha == SENHA_ADMIN:
        if os.path.exists(ARQUIVO_CSV):
            df_adm = pd.read_csv(ARQUIVO_CSV)
            st.write("### Histórico de Registros")
            st.dataframe(df_adm)

            st.markdown("---")
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.write("### 🗑️ Excluir Registro")
                if not df_adm.empty:
                    idx_del = st.number_input("Número da linha (Index):", min_value=0, max_value=len(df_adm)-1, step=1)
                    confirma_del = st.checkbox("Confirma exclusão permanente?")
                    if st.button("EXCLUIR AGORA"):
                        if confirma_del:
                            # Tenta apagar fotos se a coluna existir
                            if "Fotos" in df_adm.columns:
                                fotos_celula = str(df_adm.loc[idx_del, "Fotos"])
                                if fotos_celula and fotos_celula != "nan":
                                    for f_nome in fotos_celula.split(", "):
                                        caminho_f = os.path.join(PASTA_FOTOS, f_nome.strip())
                                        if os.path.exists(caminho_f):
                                            os.remove(caminho_f)
                            
                            # Remove do CSV
                            df_adm = df_adm.drop(idx_del)
                            df_adm.to_csv(ARQUIVO_CSV, index=False, encoding='utf-8-sig')
                            st.success("Registro e fotos apagados!")
                            st.rerun()
                else:
                    st.info("Lista vazia.")

            with col_b:
                st.write("### 🖼️ Visualizar Fotos")
                lista_arquivos = sorted(os.listdir(PASTA_FOTOS), reverse=True)
                if lista_arquivos:
                    foto_escolhida = st.selectbox("Selecione o arquivo:", lista_arquivos)
                    st.image(os.path.join(PASTA_FOTOS, foto_escolhida), use_container_width=True)
                else:
                    st.info("Nenhuma foto no servidor.")
        else:
            st.info("Aguardando o primeiro registro...")