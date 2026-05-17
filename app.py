import streamlit as st
import pandas as pd
from datetime import datetime
import os

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Powergrid Energy", page_icon="⚡", layout="centered")

# CSS PERSONALIZADO PARA MELHORAR O DESIGN
st.markdown("""
    <style>
    .stButton>button { width: 100%; background-color: #F37021; color: white; border-radius: 10px; font-weight: bold; height: 50px; }
    h1, h2, h3 { color: #0054A6 !important; text-align: center; }
    .logo-container { display: flex; justify-content: center; margin-bottom: 20px; }
    /* Estilo para os radio buttons de checklist em linha */
    div.row-widget.stRadio > div{flex-direction:row; justify-content: center; gap: 20px;}
    </style>
    """, unsafe_allow_html=True)

# EXIBIÇÃO DO LOGOTIPO (Centralizado e maior)
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
try:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=350)
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=350)
    else:
        st.title("⚡ POWERGRID ENERGY")
except:
    st.title("⚡ POWERGRID ENERGY")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# CAPTURAR PLACA DA URL
try:
    placa = st.query_params.get("placa", "Não Identificado")
except:
    placa = "Não Identificado"

st.subheader(f"Registro de Veículo: {placa}")

# FORMULÁRIO PRINCIPAL
with st.form("registro_veiculo"):
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("👤 Nome do Colaborador")
    with col2:
        tipo = st.selectbox("Operação", ["Saída", "Retorno"])
    
    km = st.number_input("KM Atual", min_value=0, step=1)
    
    # Nível de Combustível Livre (0 a 100)
    st.write("### ⛽ Nível de Combustível (%)")
    combustivel_valor = st.slider("", 0, 100, 50, format="%d%%")
    
    if combustivel_valor <= 10:
        st.error(f"⚠️ VEÍCULO NA RESERVA ({combustivel_valor}%)")
    elif combustivel_valor <= 25:
        st.warning(f"⛽ Nível Baixo ({combustivel_valor}%)")

    st.markdown("---")
    st.write("### 📋 Checklist de Inspeção")
    
    # Itens do Checklist
    itens_check = [
        "Óleo do Motor", "Faróis/Lanternas", "Pneus (Estado/Calibragem)", 
        "Limpador de Para-brisa", "Freios", "Nível de Água", "Estepe/Ferramentas"
    ]
    
    checklist_respostas = {}
    
    # Criando o checklist visualmente
    for item in itens_check:
        cols = st.columns([2, 1])
        with cols[0]:
            st.write(f"**{item}**")
        with cols[1]:
            checklist_respostas[item] = st.radio(f"Status {item}", ["OK", "Não OK"], key=item, label_visibility="collapsed")

    st.markdown("---")
    outros_defeitos = st.text_area("🛠️ Outros Defeitos ou Observações", placeholder="Descreva aqui qualquer irregularidade...")
    
    foto = st.camera_input("📸 Foto do Veículo (Obrigatório)")
    
    submit = st.form_submit_button("REGISTRAR AGORA")

# LÓGICA DE SALVAMENTO
if submit:
    if not nome:
        st.error("Por favor, preencha o nome do colaborador.")
    elif foto is None:
        st.warning("Por favor, tire uma foto para validar o registro.")
    else:
        # Preparar dados para o DataFrame
        dados_novos = {
            "Data/Hora": [datetime.now().strftime("%d/%m/%Y %H:%M")],
            "Funcionario": [nome],
            "Veiculo": [placa],
            "Tipo": [tipo],
            "KM": [km],
            "Combustivel": [f"{combustivel_valor}%"],
            "Defeitos_Obs": [outros_defeitos]
        }
        
        # Adicionar respostas do checklist ao dicionário
        for item, status in checklist_respostas.items():
            dados_novos[item] = [status]

        df = pd.DataFrame(dados_novos)
        
        # Salva localmente (CSV)
        arquivo = 'dados_veiculos.csv'
        if not os.path.exists(arquivo):
            df.to_csv(arquivo, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(arquivo, mode='a', header=False, index=False, encoding='utf-8-sig')
            
        st.success("✅ Registro realizado com sucesso!")
        st.balloons()

# ÁREA DO GESTOR (Protegida)
st.markdown("---")
with st.expander("🔐 Área Administrativa"):
    pw = st.text_input("Senha de Acesso", type="password")
    if pw == "powergrid123":
        if os.path.exists('dados_veiculos.csv'):
            relatorio = pd.read_csv('dados_veiculos.csv')
            st.dataframe(relatorio)
            st.download_button("Baixar Relatório Excel", relatorio.to_csv(index=False).encode('utf-8-sig'), "relatorio.csv", "text/csv")
        else:
            st.info("Nenhum dado registrado ainda.")