# --- ADMIN (Substitua a parte final do seu código por esta) ---
st.markdown("---")
with st.expander("🔐 Acesso Administrativo (Visualizar e Gerenciar)"):
    pw = st.text_input("Senha", type="password")
    if pw == "powergrid123":
        if os.path.exists('historico_powergrid.csv'):
            df_hist = pd.read_csv('historico_powergrid.csv')
            
            # Exibir a tabela
            st.write("### 📊 Histórico de Registros")
            st.dataframe(df_hist)

            st.markdown("---")
            st.write("### 🗑️ Excluir Registro")
            
            # Selecionar linha para excluir
            linha_para_excluir = st.number_input("Digite o número da linha (Index) que deseja excluir:", 
                                                 min_value=0, 
                                                 max_value=len(df_hist)-1, 
                                                 step=1)
            
            col_del1, col_del2 = st.columns(2)
            with col_del1:
                confirmar = st.checkbox(f"Confirma a exclusão da linha {linha_para_excluir}?")
            
            with col_del2:
                if st.button("❌ EXCLUIR DEFINITIVAMENTE"):
                    if confirmar:
                        try:
                            # 1. Identificar e apagar fotos associadas
                            fotos_str = df_hist.loc[linha_para_excluir, "Fotos"]
                            if pd.notna(fotos_str) and fotos_str != "":
                                lista_fotos = fotos_str.split(", ")
                                for f in lista_fotos:
                                    caminho_f = os.path.join(PASTA_FOTOS, f)
                                    if os.path.exists(caminho_f):
                                        os.remove(caminho_f)
                            
                            # 2. Remover do DataFrame e salvar CSV
                            df_hist = df_hist.drop(linha_para_excluir)
                            df_hist.to_csv('historico_powergrid.csv', index=False, encoding='utf-8-sig')
                            
                            st.success(f"Registro {linha_para_excluir} e suas fotos foram removidos!")
                            st.rerun() # Atualiza a página para mostrar a tabela nova
                        except Exception as e:
                            st.error(f"Erro ao excluir: {e}")
                    else:
                        st.warning("Você precisa marcar a caixa de confirmação primeiro.")

            st.markdown("---")
            st.write("### 🖼️ Visualizar Fotos")
            arquivos_na_pasta = sorted(os.listdir(PASTA_FOTOS), reverse=True)
            if arquivos_na_pasta:
                foto_view = st.selectbox("Selecione uma foto para ver:", arquivos_na_pasta)
                st.image(os.path.join(PASTA_FOTOS, foto_view), use_container_width=True)
            else:
                st.info("Nenhuma foto na pasta.")
        else:
            st.info("Ainda não há registros no arquivo CSV.")