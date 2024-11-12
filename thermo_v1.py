import streamlit as st
import numpy as np
from scipy.constants import R

def calcular_gas_ideal(P, V, n, T):
    """Calcula propriedades do gás ideal"""
    R_val = R  # Constante universal dos gases em J/(mol·K)
    
    # Equação dos gases ideais: PV = nRT
    if P is None:
        P = (n * R_val * T) / V
    elif V is None:
        V = (n * R_val * T) / P
    elif n is None:
        n = (P * V) / (R_val * T)
    elif T is None:
        T = (P * V) / (n * R_val)
        
    # Energia interna (gás monoatômico ideal)
    U = (3/2) * n * R_val * T
    
    # Entalpia
    H = U + P * V
    
    return P, V, n, T, U, H

def main():
    st.title("Calculadora de Propriedades Termodinâmicas")
    st.write("Insira os valores no Sistema Internacional (SI)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        P = st.number_input("Pressão (Pa)", value=None, placeholder="Digite a pressão")
        V = st.number_input("Volume (m³)", value=None, placeholder="Digite o volume")
    
    with col2:
        n = st.number_input("Número de mols", value=None, placeholder="Digite o número de mols")
        T = st.number_input("Temperatura (K)", value=None, placeholder="Digite a temperatura")
    
    # Verifica se apenas uma variável está faltando
    valores = [P, V, n, T]
    if valores.count(None) != 1:
        st.warning("Por favor, deixe exatamente uma variável em branco para calcular")
        return
    
    if st.button("Calcular"):
        P, V, n, T, U, H = calcular_gas_ideal(P, V, n, T)
        
        st.write("### Resultados:")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"Pressão: {P:.2f} Pa")
            st.write(f"Volume: {V:.6f} m³")
        
        with col2:
            st.write(f"Número de mols: {n:.4f}")
            st.write(f"Temperatura: {T:.2f} K")
        
        with col3:
            st.write(f"Energia Interna: {U:.2f} J")
            st.write(f"Entalpia: {H:.2f} J")

if __name__ == "__main__":
    main()
