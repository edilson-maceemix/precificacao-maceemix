import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Ferramenta de Precificação - Macee Mix", layout="wide")

# Título e Estilo
st.title("📊 Calculadora de Lucratividade - Macee Mix")
st.markdown("---")

# --- INICIALIZAÇÃO DE DADOS (Simulando Banco de Dados) ---
if 'custos_fixos' not in st.session_state:
    st.session_state.custos_fixos = pd.DataFrame(columns=['Descrição', 'Valor', 'Categoria'])
if 'insumos' not in st.session_state:
    st.session_state.insumos = pd.DataFrame(columns=['Produto', 'Unidade', 'Qtd Compra', 'Valor Compra', 'Custo Unitário'])
if 'faturamento_medio' not in st.session_state:
    st.session_state.faturamento_medio = 20000.0

# --- BARRA LATERAL (NAVEGAÇÃO) ---
menu = st.sidebar.radio("Navegação", ["1. Custos Fixos & Configuração", "2. Banco de Insumos", "3. Precificação (Revenda)", "4. Ficha Técnica (Produção)"])

# --- MÓDULO 1: CUSTOS FIXOS ---
if menu == "1. Custos Fixos & Configuração":
    st.header("🏢 Estrutura de Custos da Empresa")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configuração Global")
        novo_faturamento = st.number_input("Faturamento Médio Mensal (R$)", value=float(st.session_state.faturamento_medio), step=500.0)
        st.session_state.faturamento_medio = novo_faturamento
        
        st.info("Adicione suas despesas fixas abaixo (Aluguel, Internet, Pro-labore, etc).")
        with st.form("add_custo"):
            desc = st.text_input("Descrição (ex: Internet)")
            valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
            cat = st.selectbox("Categoria", ["Despesas Fixas", "Pessoal", "Outros"])
            submit = st.form_submit_button("Adicionar Custo")
            
            if submit and desc:
                novo_custo = pd.DataFrame({'Descrição': [desc], 'Valor': [valor], 'Categoria': [cat]})
                st.session_state.custos_fixos = pd.concat([st.session_state.custos_fixos, novo_custo], ignore_index=True)
                st.success("Custo adicionado!")

    with col2:
        st.subheader("Resumo Financeiro")
        if not st.session_state.custos_fixos.empty:
            st.dataframe(st.session_state.custos_fixos, use_container_width=True)
            
            total_custo_fixo = st.session_state.custos_fixos['Valor'].sum()
            percentual_custo_fixo = (total_custo_fixo / st.session_state.faturamento_medio) * 100
            
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Total Custos Fixos", f"R$ {total_custo_fixo:,.2f}")
            kpi2.metric("Faturamento Base", f"R$ {st.session_state.faturamento_medio:,.2f}")
            kpi3.metric("Rateio (Custo Fixo %)", f"{percentual_custo_fixo:.2f}%")
            
            st.warning(f"💡 **Impacto:** Cada produto vendido deve cobrir **{percentual_custo_fixo:.2f}%** do seu preço para pagar as contas da empresa.")
            
            # Botão para limpar
            if st.button("Limpar Tabela de Custos"):
                st.session_state.custos_fixos = pd.DataFrame(columns=['Descrição', 'Valor', 'Categoria'])
                st.rerun()
        else:
            st.warning("Cadastre seus custos fixos para calcular o rateio.")

# --- MÓDULO 2: INSUMOS ---
elif menu == "2. Banco de Insumos":
    st.header("📦 Cadastro de Insumos/Matéria Prima")
    st.markdown("Cadastre aqui materiais para kits ou produtos de revenda.")
    
    with st.form("add_insumo"):
        c1, c2, c3, c4 = st.columns(4)
        prod = c1.text_input("Nome do Produto/Insumo")
        unid = c2.selectbox("Unidade", ["unid", "kg", "g", "litro", "ml", "metro"])
        qtd = c3.number_input("Qtd na Embalagem de Compra", min_value=0.1)
        val = c4.number_input("Valor Pago na Compra (R$)", min_value=0.0)
        
        submit_insumo = st.form_submit_button("Salvar Insumo")
        
        if submit_insumo and prod:
            custo_unit = val / qtd if qtd > 0 else 0
            novo_insumo = pd.DataFrame({
                'Produto': [prod], 
                'Unidade': [unid], 
                'Qtd Compra': [qtd], 
                'Valor Compra': [val], 
                'Custo Unitário': [custo_unit]
            })
            st.session_state.insumos = pd.concat([st.session_state.insumos, novo_insumo], ignore_index=True)
            st.success(f"{prod} cadastrado com custo unitário de R$ {custo_unit:.2f}")

    if not st.session_state.insumos.empty:
        st.dataframe(st.session_state.insumos.style.format({"Valor Compra": "R$ {:.2f}", "Custo Unitário": "R$ {:.4f}"}), use_container_width=True)
        if st.button("Limpar Insumos"):
            st.session_state.insumos = pd.DataFrame(columns=['Produto', 'Unidade', 'Qtd Compra', 'Valor Compra', 'Custo Unitário'])
            st.rerun()

# --- MÓDULO 3: PRECIFICAÇÃO REVENDA (DIRETA) ---
elif menu == "3. Precificação (Revenda)":
    st.header("🏷️ Precificação de Revenda (Mercado Livre/Shopee/Magalu)")
    
    # Recalcula percentual atual
    total_fixo = st.session_state.custos_fixos['Valor'].sum() if not st.session_state.custos_fixos.empty else 0
    perc_fixo = (total_fixo / st.session_state.faturamento_medio) if st.session_state.faturamento_medio > 0 else 0
    
    col_input, col_result = st.columns([1, 1])
    
    with col_input:
        st.subheader("Dados do Produto")
        nome_prod = st.text_input("Nome do Produto")
        custo_compra = st.number_input("Custo de Aquisição (R$)", min_value=0.0, format="%.2f")
        custo_embalagem = st.number_input("Custo Embalagem/Etiqueta (R$)", min_value=0.0, format="%.2f")
        
        st.subheader("Taxas de Venda")
        imposto = st.number_input("Imposto Simples Nacional (%)", value=4.0, step=0.5) / 100
        taxa_mkt = st.number_input("Comissão Marketplace + Cartão (%)", value=18.0, step=0.5, help="Soma da comissão da Shopee/ML + Taxa Financeira") / 100
        outras_taxas_fixas = st.number_input("Taxa Fixa por Venda (R$)", value=3.00, help="Ex: Taxa de frete grátis ou taxa fixa do ML")
        
        st.subheader("Lucro Desejado")
        markup_desejado = st.number_input("Markup Desejado (%)", value=30.0, step=5.0) / 100

    with col_result:
        st.subheader("Análise de Preço")
        
        if custo_compra > 0:
            # Cálculos
            custo_produto_total = custo_compra + custo_embalagem
            rateio_fixo_valor = custo_produto_total * perc_fixo # Rateio simples proporcional ao custo
            
            # Preço Sugerido (Markup sobre custo base)
            # Fórmula Base: Custo Total * (1 + Markup) + Taxas Fixas
            # Nota: Para cálculo reverso considerando taxas sobre a venda (Mark-up divisor), a fórmula muda.
            # Aqui usaremos a lógica da sua planilha (Markup multiplicador sobre custo)
            
            base_calculo = custo_produto_total + rateio_fixo_valor
            preco_venda = (base_calculo * (1 + markup_desejado)) / (1 - (imposto + taxa_mkt)) + outras_taxas_fixas
            
            st.metric("PREÇO DE VENDA SUGERIDO", f"R$ {preco_venda:.2f}")
            
            # Detalhamento
            st.markdown("### Composição do Preço")
            dados_composicao = {
                "Item": ["Custo Produto + Emb.", "Rateio Custo Fixo", "Impostos", "Taxas Marketplace", "Taxa Fixa Mkt", "Margem de Lucro"],
                "Valor (R$)": [
                    custo_produto_total,
                    rateio_fixo_valor,
                    preco_venda * imposto,
                    preco_venda * taxa_mkt,
                    outras_taxas_fixas,
                    preco_venda - (custo_produto_total + rateio_fixo_valor + (preco_venda*imposto) + (preco_venda*taxa_mkt) + outras_taxas_fixas)
                ]
            }
            df_comp = pd.DataFrame(dados_composicao)
            st.dataframe(df_comp.style.format({"Valor (R$)": "R$ {:.2f}"}), use_container_width=True)
            
            lucro_liquido = df_comp.iloc[5, 1]
            margem_contrib = (lucro_liquido / preco_venda) * 100
            
            if margem_contrib < 10:
                st.error(f"⚠️ Margem Líquida Baixa: {margem_contrib:.1f}%")
            else:
                st.success(f"✅ Margem Líquida Saudável: {margem_contrib:.1f}%")

# --- MÓDULO 4: FICHA TÉCNICA (PRODUÇÃO) ---
elif menu == "4. Ficha Técnica (Produção)":
    st.header("👨‍🍳 Precificação de Receitas/Kits")
    
    if st.session_state.insumos.empty:
        st.warning("Cadastre insumos na aba 'Banco de Insumos' primeiro.")
    else:
        # Seleção de ingredientes
        lista_insumos = st.session_state.insumos['Produto'].tolist()
        
        st.subheader("Composição do Kit/Receita")
        
        if 'receita_atual' not in st.session_state:
            st.session_state.receita_atual = []
            
        c1, c2, c3 = st.columns([3, 1, 1])
        item_add = c1.selectbox("Selecione o Insumo", lista_insumos)
        qtd_add = c2.number_input("Qtd Usada", min_value=0.0, step=0.1, format="%.3f")
        bt_add = c3.button("Adicionar Item")
        
        if bt_add:
            dados_item = st.session_state.insumos[st.session_state.insumos['Produto'] == item_add].iloc[0]
            custo_item = dados_item['Custo Unitário'] * qtd_add
            st.session_state.receita_atual.append({
                "Ingrediente": item_add,
                "Qtd": qtd_add,
                "Unid": dados_item['Unidade'],
                "Custo Total": custo_item
            })
            
        if st.session_state.receita_atual:
            df_receita = pd.DataFrame(st.session_state.receita_atual)
            st.dataframe(df_receita, use_container_width=True)
            
            custo_insumos_total = df_receita['Custo Total'].sum()
            st.metric("Custo Total de Insumos (CMV)", f"R$ {custo_insumos_total:.2f}")
            
            if st.button("Limpar Receita"):
                st.session_state.receita_atual = []
                st.rerun()
            
            st.markdown("---")
            st.subheader("Definição de Preço Final")
            # Usa lógica simplificada aqui para fechar o preço
            markup_prod = st.slider("Markup Multiplicador", 1.0, 4.0, 2.0)
            preco_final_kit = custo_insumos_total * markup_prod
            
            st.success(f"💰 Preço de Venda Sugerido: R$ {preco_final_kit:.2f}")
