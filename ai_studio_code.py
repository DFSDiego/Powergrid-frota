import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da Página
st.set_page_config(page_title="Powergrid - Controle de Frota", page_icon="⚡")

# Criar pastas para fotos e dados se não existirem
if not os.path.exists("registros"):
    os.makedirs("registros")
if not os.path.exists("fotos_danos"):
    os.makedirs("fotos_danos")

# Título e Logo
st.title("⚡ Powergrid - Gestão de Veículos")
st.markdown("---")

# Identificação do Veículo via URL (Ex: ?placa=ABC1234)
query_params = st.query_params
veiculo_detectado = query_params.get("placa", "Não Identificado")

st.info(f"**Veículo Selecionado:** {veiculo_detectado}")

# Formulário de Uso
with st.form("check_list_form"):
    st.subheader("📋 Checklist de Saída/Entrada")
    
    nome_funcionario = st.text_input("Nome do Colaborador")
    tipo_movimentacao = st.selectbox("Tipo", ["Saída", "Retorno"])
    km_atual = st.number_input("Quilometragem Atual (KM)", min_value=0)
    
    st.write("**Estado do Veículo:**")
    col1, col2 = st.columns(2)
    with col1:
        limpeza = st.checkbox("Veículo Limpo?")
        pneus = st.checkbox("Pneus Calibrados/Bons?")
    with col2:
        luzes = st.checkbox("Faróis/Lanternas OK?")
        combustivel = st.slider("Nível de Combustível", 0, 100, 50)

    st.write("**Relato de Danos ou Observações:**")
    obs = st.text_area("Descreva qualquer avaria, risco ou problema mecânico:")
    
    foto = st.camera_input("Tirar foto do estado do veículo (Obrigatório em caso de dano)")

    submit = st.form_submit_button("Registrar no Sistema Powergrid")

# Processamento do Registro
if submit:
    if nome_funcionario == "":
        st.error("Por favor, preencha seu nome.")
    else:
        # Criar dicionário de dados
        novo_registro = {
            "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Funcionário": nome_funcionario,
            "Veículo": veiculo_detectado,
            "Tipo": tipo_movimentacao,
            "KM": km_atual,
            "Combustível %": combustivel,
            "Limpeza": limpeza,
            "Luzes": luzes,
            "Pneus": pneus,
            "Observações": obs
        }

        # Salvar Foto se houver
        if foto:
            nome_foto = f"foto_{veiculo_detectado}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            with open(f"fotos_danos/{nome_foto}", "wb") as f:
                f.write(foto.getbuffer())
            novo_registro["Link_Foto"] = nome_foto

        # Salvar em CSV (Banco de Dados simples)
        df = pd.DataFrame([novo_registro])
        arquivo_db = 'registros/uso_veiculos.csv'
        
        if not os.path.isfile(arquivo_db):
            df.to_csv(arquivo_db, index=False)
        else:
            df.to_csv(arquivo_db, mode='a', header=False, index=False)

        st.success(f"Registro de {tipo_movimentacao} realizado com sucesso! Pode seguir viagem, {nome_funcionario}.")
        st.balloons()

# Área do Administrador (Protegida)
with st.expander("Acesso Administrativo"):
    senha = st.text_input("Senha Admin", type="password")
    if senha == "powergrid123":
        if os.path.exists('registros/uso_veiculos.csv'):
            dados = pd.read_csv('registros/uso_veiculos.csv')
            st.write("### Histórico de Uso")
            st.dataframe(dados)
            st.download_button("Baixar Relatório Excel", dados.to_csv(), "relatorio_powergrid.csv")
        else:
            st.warning("Nenhum registro encontrado.")