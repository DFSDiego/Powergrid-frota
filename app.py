import streamlit as st
import pandas as pd
from datetime import datetime
import os

# CONFIGURAÇÃO DA PÁGINA E IDENTIDADE VISUAL
st.set_page_config(page_title="Powergrid Energy - Frota", page_icon="⚡", layout="centered")

# CSS Customizado para Identidade Visual (Cores da Powergrid)
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        background-color: #F37021; /* Laranja da Logo */
        color: white;
        border-radius: 10px;
        border: none;
        height: 3em;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0054A6; /* Azul da Logo */
        color: white;
    }
    h1, h2, h3 {
        color: #0054A6 !important;
    }
    .stSelectbox, .stTextInput, .stNumberInput {
        border-radius: 10px;
    }
    /* Estilização da Barra de Combustível */
    .combustivel-status {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# EXIBIÇÃO DO LOGOTIPO
if os.path.exists("logo.png"):
    st.image("logo.png", width=250)
else:
    st.title("⚡ POWERGRID ENERGY")
    st.caption("POTÊNCIA PARA TRANSFORMAR O MUNDO")

st.markdown("---")

# IDENTIFICAÇÃO DO VEÍCULO
query_params = st.query_params
veiculo_detectado = query_params.get("placa", "Não Identificado")

st.subheader(f"Controle de Uso - Veículo: {veiculo_detectado}")

# FORMULÁRIO PROFISSIONAL
with st.container():
    nome_funcionario = st.text_input("👤 Nome do Colaborador")
    
    col_tipo, col_km = st.columns(2)
    with col_tipo:
        tipo_movimentacao = st.selectbox("Tipo de Registro", ["Saída", "Retorno"])
    with col_km:
        km_atual = st.number_input("Quilometragem Atual (KM)", min_value=0, step=1)

    st.markdown("### ⛽ Nível de Combustível")
    # Seletor de combustível conforme solicitado
    niveis = ["0 (Reserva)", "1/4", "1/2", "3/4", "1 (Cheio)"]
    combustivel = st.select_slider(
        "Arraste para indicar o nível no painel:",
        options=niveis,
        value="1/2"
    )

    # Feedback visual das cores de combustível
    if combustivel == "0 (Reserva)":
        st.markdown('<div class="combustivel-status" style="background-color: #FF0000;">⚠️ ATENÇÃO: VEÍCULO NA RESERVA</div>', unsafe_allow_html=True)
    elif combustivel == "1/4":
        st.markdown('<div class="combustivel-status" style="background-color: #F37021;">⛽ Nível Baixo</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="combustivel-status" style="background-color: #28a745;">✅ Nível Seguro</div>', unsafe_allow_html=True)

    st.markdown("### 🔍 Checklist de Estado")
    col1, col2 = st.columns(2)
    with col1:
        limpeza = st.checkbox("🧼 Veículo Limpo?")
        pneus = st.checkbox("🛞 Pneus em bom estado?")
    with col2:
        luzes = st.checkbox("💡 Faróis e Lanternas OK?")
        danos = st.checkbox("⚠️ Existe algum dano novo?")

    obs = st.text_area("Observações adicionais ou descrição de danos:")
    
    st.markdown("### 📸 Registro Fotográfico")
    foto = st.camera_input("Tirar foto do veículo (Obrigatório em caso de danos)")

    # BOTÃO DE ENVIO
    submit = st.button("REGISTRAR NA BASE POWERGRID")

# LÓGICA DE SALVAMENTO
if submit:
    if not nome_funcionario:
        st.error("Por favor, informe seu nome antes de salvar.")
    else:
        novo_registro = {
            "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Funcionário": nome_funcionario,
            "Veículo": veiculo_detectado,
            "Tipo": tipo_movimentacao,
            "KM": km_atual,
            "Combustível": combustivel,
            "Limpeza": "Sim" if limpeza else "Não",
            "Pneus": "Sim" if pneus else "Não",
            "Luzes": "Sim" if luzes else "Não",
            "Dano_Relatado": "Sim" if danos else "Não",
            "Observações": obs
        }

        # Salvar em CSV
        df = pd.DataFrame([novo_registro])
        arquivo_db = 'registros_powergrid.csv'
        
        if not os.path.isfile(arquivo_db):
            df.to_csv(arquivo_db, index=False)
        else:
            df.to_csv(arquivo_db, mode='a', header=False, index=False)

        st.success(f"Protocolo registrado! Boa viagem, {nome_funcionario}.")
        st.balloons()

# PAINEL DO GESTOR (RODAPÉ)
st.markdown("---")
with st.expander("🔐 Área do Gestor Powergrid"):
    senha = st.text_input("Senha de Acesso", type="password")
    if senha == "powergrid2024":
        if os.path.exists('registros_powergrid.csv'):
            dados = pd.read_csv('registros_powergrid.csv')
            st.write("### Relatório Consolidado")
            st.dataframe(dados)
            st.download_button("📥 Baixar Planilha para Controle de Multas", dados.to_csv(index=False), "relatorio_frota_powergrid.csv")
        else:
            st.info("Ainda não há registros no sistema.")