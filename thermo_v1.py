import streamlit as st
try:
    from CoolProp.CoolProp import PropsSI
except ImportError:
    st.error("Erro ao importar CoolProp. Por favor, verifique se a biblioteca está instalada corretamente.")

# Título do aplicativo
st.title("Calculadora de Propriedades Termodinâmicas")

# Seleção do fluido
fluido = st.selectbox("Selecione o fluido:", ["Water", "Air", "R134a", "CO2", "Ammonia"])

# Seleção das propriedades conhecidas
st.header("Propriedades Conhecidas")
input_tipo = st.selectbox("Escolha o tipo de entrada: ", [
    "Pressão e Temperatura",
    "Temperatura e Volume Específico",
    "Pressão e Entalpia",
])

# Inputs
if input_tipo == "Pressão e Temperatura":
    pressao = st.number_input("Pressão (Pa):", min_value=0.01, format="%.2f")
    temperatura = st.number_input("Temperatura (K):", min_value=0.01, format="%.2f")
    if pressao > 0 and temperatura > 0:
        try:
            volume_especifico = PropsSI('V', 'P', pressao, 'T', temperatura, fluido)
            energia_interna = PropsSI('U', 'P', pressao, 'T', temperatura, fluido)
            entalpia = PropsSI('H', 'P', pressao, 'T', temperatura, fluido)
            st.write(f"Volume Específico: {volume_especifico:.4f} m3/kg")
            st.write(f"Energia Interna: {energia_interna:.2f} J/kg")
            st.write(f"Entalpia: {entalpia:.2f} J/kg")
        except ValueError as e:
            st.error(f"Erro ao calcular propriedades: {e}")

elif input_tipo == "Temperatura e Volume Específico":
    temperatura = st.number_input("Temperatura (K):", min_value=0.01, format="%.2f")
    volume_especifico = st.number_input("Volume Específico (m3/kg):", min_value=0.01, format="%.4f")
    if temperatura > 0 and volume_especifico > 0:
        try:
            pressao = PropsSI('P', 'T', temperatura, 'D', 1/volume_especifico, fluido)
            energia_interna = PropsSI('U', 'T', temperatura, 'D', 1/volume_especifico, fluido)
            entalpia = PropsSI('H', 'T', temperatura, 'D', 1/volume_especifico, fluido)
            st.write(f"Pressão: {pressao:.2f} Pa")
            st.write(f"Energia Interna: {energia_interna:.2f} J/kg")
            st.write(f"Entalpia: {entalpia:.2f} J/kg")
        except ValueError as e:
            st.error(f"Erro ao calcular propriedades: {e}")

elif input_tipo == "Pressão e Entalpia":
    pressao = st.number_input("Pressão (Pa):", min_value=0.01, format="%.2f")
    entalpia = st.number_input("Entalpia (J/kg):", min_value=0.01, format="%.2f")
    if pressao > 0 and entalpia > 0:
        try:
            temperatura = PropsSI('T', 'P', pressao, 'H', entalpia, fluido)
            volume_especifico = PropsSI('V', 'P', pressao, 'H', entalpia, fluido)
            energia_interna = PropsSI('U', 'P', pressao, 'H', entalpia, fluido)
            st.write(f"Temperatura: {temperatura:.2f} K")
            st.write(f"Volume Específico: {volume_especifico:.4f} m3/kg")
            st.write(f"Energia Interna: {energia_interna:.2f} J/kg")
        except ValueError as e:
            st.error(f"Erro ao calcular propriedades: {e}")

# Informação adicional
st.write("\n\nAs propriedades são calculadas usando a biblioteca CoolProp.")
