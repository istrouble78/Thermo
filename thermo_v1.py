import streamlit as st
from math import pow

# Título do aplicativo
st.title("Calculadora de Propriedades Termodinâmicas")

# Seleção do fluido
fluido = st.selectbox("Selecione o fluido:", ["Air", "Water", "R134a", "CO2", "Ammonia"])

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
            # Utilizando aproximação de gás ideal
            R = 287.05  # Constante do gás ideal para ar (J/(kg*K))
            volume_especifico = R * temperatura / pressao
            energia_interna = 1.5 * R * temperatura  # Aproximação para energia interna de gás ideal monoatômico
            entalpia = 2.5 * R * temperatura  # Aproximação para entalpia de gás ideal monoatômico

            st.write(f"Volume Específico: {volume_especifico:.4f} m3/kg")
            st.write(f"Energia Interna: {energia_interna:.2f} J/kg")
            st.write(f"Entalpia: {entalpia:.2f} J/kg")
        except ValueError as e:
            st.error(f"Erro ao calcular propriedades: {e}")
        except Exception as e:
            st.error(f"Erro inesperado: {e}")

elif input_tipo == "Temperatura e Volume Específico":
    temperatura = st.number_input("Temperatura (K):", min_value=0.01, format="%.2f")
    volume_especifico = st.number_input("Volume Específico (m3/kg):", min_value=0.01, format="%.4f")
    if temperatura > 0 and volume_especifico > 0:
        try:
            # Utilizando aproximação de gás ideal
            R = 287.05  # Constante do gás ideal para ar (J/(kg*K))
            pressao = (R * temperatura) / volume_especifico
            energia_interna = 1.5 * R * temperatura  # Aproximação para energia interna de gás ideal monoatômico
            entalpia = 2.5 * R * temperatura  # Aproximação para entalpia de gás ideal monoatômico

            st.write(f"Pressão: {pressao:.2f} Pa")
            st.write(f"Energia Interna: {energia_interna:.2f} J/kg")
            st.write(f"Entalpia: {entalpia:.2f} J/kg")
        except ValueError as e:
            st.error(f"Erro ao calcular propriedades: {e}")
        except Exception as e:
            st.error(f"Erro inesperado: {e}")

elif input_tipo == "Pressão e Entalpia":
    pressao = st.number_input("Pressão (Pa):", min_value=0.01, format="%.2f")
    entalpia = st.number_input("Entalpia (J/kg):", min_value=0.01, format="%.2f")
    if pressao > 0 and entalpia > 0:
        try:
            # Utilizando aproximação de gás ideal
            R = 287.05  # Constante do gás ideal para ar (J/(kg*K))
            temperatura = entalpia / (2.5 * R)  # Aproximação para temperatura de gás ideal monoatômico
            volume_especifico = R * temperatura / pressao
            energia_interna = 1.5 * R * temperatura  # Aproximação para energia interna de gás ideal monoatômico

            st.write(f"Temperatura: {temperatura:.2f} K")
            st.write(f"Volume Específico: {volume_especifico:.4f} m3/kg")
            st.write(f"Energia Interna: {energia_interna:.2f} J/kg")
        except ValueError as e:
            st.error(f"Erro ao calcular propriedades: {e}")
        except Exception as e:
            st.error(f"Erro inesperado: {e}")

# Informação adicional
st.write("\n\nAs propriedades são calculadas utilizando aproximações de gás ideal.")
