import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import os
import urllib.parse

# --- CONFIGURAÇÕES ---
NUMERO_WHATSAPP = "5511975000422" 
PASTA_FOTOS = "fotos_registradas"
ARQUIVO_CSV = "historico_powergrid.csv"
SENHA_ADMIN = "powergrid123"

# Função para pegar o horário de Brasília (UTC-3)
def get_brasilia_time():
    fuso_horario = timezone(timedelta(hours=-3))
    return datetime.now(fuso_horario)

if not os.path.exists(PASTA_FOTOS):
    os.makedirs(PASTA_FOTOS)

st.set_page_config(page_title="Powergrid Energy", page_icon="⚡", layout="centered")

# --- ESTILO VISUAL POWERGRID ---
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
        font-size: 18px;
        border: none;
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

# Pegar placa da URL
placa = st.query_params.get("placa", "Não Identificado")

st.markdown(f"<h3 style='text-align: center;'>Veículo: {placa}</h3>", unsafe_allow_html=True)

# --- FORMULÁRIO ---
st.write("### 📋 Informações Gerais")
nome = st.text_input("👤 Nome do Colaborador")

c1, c2 = st.columns(2)
with c1: tipo = st.selectbox("Registro", ["Saída", "Retorno"])
with c2: km = st.number_input("KM Atual", min_value=0, step=1)

combustivel = st.select_slider("⛽ Nível de Combustível", options=["Reserva", "1/4", "1/2", "3/4", "1"], value="1/2")

st.markdown("---")
st.write("### 📋 Checklist de Segurança")

itens = {
    "Óleo do Motor": "oleo",
    "Faróis": "farois",
    "Lanternas": "lanternas",
    "Pneus": "pneus",
    "Limpadores": "limpadores",
    "Nível de Água": "agua"
}

respostas = {}
for label, key in itens.items():
    cols = st.columns([2, 2])
    with cols[0]: st.write(f"**{label}**")
    with cols[1]: respostas[label] = st.radio(label, ["OK", "Não OK"], key=key, horizontal=True, label_visibility="collapsed")

st.markdown("---")
defeitos = st.text_area("🛠️ Outros Defeitos / Observações", placeholder="Relate barulhos, trincas ou irregularidades...")

# --- SEÇÃO DE FOTOS ---
st.write("### 📸 Fotos (Obrigatório)")
f1 = st.camera_input("1. Foto do Painel (KM e Combustível)", key="foto_painel")

f2 = None
if f1:
    st.success("✅ Foto do Painel capturada!")
    f2 = st.camera_input("2. Foto Frontal / Avaria / Irregularidade", key="foto_veiculo")
    if f2:
        st.success("✅ Foto do Veículo capturada!")
else:
    st.info("Aguardando foto do painel para liberar a segunda câmera...")

st.markdown("---")

if st.button("REGISTRAR"):
    if not nome:
        st.error("Por favor, preencha o Nome do Colaborador.")
    elif not f1:
        st.error("A foto do Painel é obrigatória.")
    else:
        agora = get_brasilia_time()
        data_txt = agora.strftime("%d/%m/%Y %H:%M")
        ts = agora.strftime("%Y%m%d_%H%M%S")
        
        nomes_fotos = []
        for i, foto in enumerate([f1, f2]):
            if foto:
                nome_f = f"{ts}_{placa}_f{i+1}.jpg"
                with open(os.path.join(PASTA_FOTOS, nome_f), "wb") as f:
                    f.write(foto.getvalue())
                nomes_fotos.append(nome_f)

        novo_reg = {
            "Data": data_txt, "Funcionario": nome, "Veiculo": placa,
            "Tipo": tipo, "KM": km, "Combustivel": combustivel,
            "Obs": defeitos.replace("\n", " "), "Fotos": ", ".join(nomes_fotos)
        }
        for k, v in respostas.items():
            novo_reg[k] = v
        
        df_novo = pd.DataFrame([novo_reg])
        
        if os.path.exists(ARQUIVO_CSV):
            try:
                df_hist = pd.read_csv(ARQUIVO_CSV)
                df_final = pd.concat([df_hist, df_novo], ignore_index=True)
            except:
                df_final = df_novo
        else:
            df_final = df_novo
        
        df_final.to_csv(ARQUIVO_CSV, index=False, encoding='utf-8-sig')
        
        st.success("✅ Registro realizado com sucesso!")

        msg_wpp = (
            f"*RELATÓRIO DE VEÍCULO - POWERGRID*\n\n"
            f"👤 *Colaborador:* {nome}\n"
            f"🚗 *Veículo:* {placa}\n"
            f"📅 *Data:* {data_txt}\n"
            f"📍 *Tipo:* {tipo}\n"
            f"🛣️ *KM:* {km}\n"
            f"⛽ *Combustível:* {combustivel}\n\n"
            f"*CHECKLIST:*\n"
        )
        for item, status in respostas.items():
            icon = "✅" if status == "OK" else "❌"
            msg_wpp += f"{icon} {item}\n"
        
        msg_wpp += f"\n🛠️ *Obs:* {defeitos if defeitos else 'Tudo em ordem'}"
        
        link_final = f"https://wa.me/{NUMERO_WHATSAPP}?text={urllib.parse.quote(msg_wpp)}"
        st.markdown(f'<a href="{link_final}" target="_blank" class="btn-whatsapp">📲 Enviar para o Gestor</a>', unsafe_allow_html=True)
        st.balloons()

# --- ADMINISTRAÇÃO ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("🔐 Acesso Administrativo"):
    senha = st.text_input("Senha Admin", type="password")
    if senha == SENHA_ADMIN:
        if os.path.exists(ARQUIVO_CSV):
            df_adm = pd.read_csv(ARQUIVO_CSV)
            st.write("### Histórico de Registros")
            st.dataframe(df_adm)
            
            st.write("---")
            st.write("### 🖼️ Visualizar/Gerenciar")
            
            if not df_adm.empty:
                linha_idx = st.selectbox("Selecione o registro:", df_adm.index, format_func=lambda x: f"ID {x} - {df_adm.loc[x, 'Data']} - {df_adm.loc[x, 'Funcionario']}")
                
                f_celula = str(df_adm.loc[linha_idx, "Fotos"])
                if f_celula != "nan":
                    fotos_registro = f_celula.split(", ")
                    cols_fotos = st.columns(len(fotos_registro))
                    for i, f_nome in enumerate(fotos_registro):
                        caminho_img = os.path.join(PASTA_FOTOS, f_nome.strip())
                        if os.path.exists(caminho_img):
                            with cols_fotos[i]:
                                st.image(caminho_img, caption=f"Foto {i+1}")

                st.write("---")
                
                # --- LÓGICA DE CONFIRMAÇÃO DE EXCLUSÃO ---
                if "confirmar_excluir" not in st.session_state:
                    st.session_state.confirmar_excluir = False

                if not st.session_state.confirmar_excluir:
                    if st.button("🗑️ Solicitar Exclusão deste Registro"):
                        st.session_state.confirmar_excluir = True
                        st.rerun()
                else:
                    st.warning(f"⚠️ **ATENÇÃO:** Tem certeza que deseja apagar o registro ID {linha_idx} e suas fotos? Esta ação não pode ser desfeita.")
                    col_sim, col_nao = st.columns(2)
                    
                    with col_sim:
                        if st.button("✅ SIM, APAGAR"):
                            # Apagar arquivos de foto
                            if f_celula != "nan":
                                for f_nome in f_celula.split(", "):
                                    c_f = os.path.join(PASTA_FOTOS, f_nome.strip())
                                    if os.path.exists(c_f): os.remove(c_f)
                            
                            # Atualizar CSV
                            df_adm.drop(linha_idx).to_csv(ARQUIVO_CSV, index=False, encoding='utf-8-sig')
                            
                            st.session_state.confirmar_excluir = False
                            st.success("Excluído com sucesso!")
                            st.rerun()
                            
                    with col_nao:
                        if st.button("❌ CANCELAR"):
                            st.session_state.confirmar_excluir = False
                            st.rerun()
        else:
            st.info("Nenhum registro encontrado.")