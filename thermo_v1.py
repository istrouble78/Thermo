import streamlit as st
import numpy as np
from scipy.constants import R

# Dicionário com propriedades dos gases
GASES = {
    'Ar': {
        'M': 0.028964,  # kg/mol
        'gamma': 1.4,    # cp/cv
        'cp': 1005,     # J/(kg·K)
    },
    'N2': {
        'M': 0.028014,
        'gamma': 1.4,
        'cp': 1039,
    },
    'O2': {
        'M': 0.032,
        'gamma': 1.4,
        'cp': 919,
    },
    'He': {
        'M': 0.004003,
        'gamma': 1.667,
        'cp': 5193,
    },
    'H2': {
        'M': 0.002016,
        'gamma': 1.41,
        'cp': 14307,
    }
}

def calcular_propriedades(P, V, m, T, gas):
    """Calcula propriedades termodinâmicas para um gás específico"""
    M = GASES[gas]['M']     # kg/mol
    gamma = GASES[gas]['gamma']
    cp = GASES[gas]['cp']   # J/(kg·K)
    cv = cp/gamma           # J/(kg·K)
    R_esp = R/M            # J/(kg·K)

    # Converter massa para número de mols se necessário
    if m is not None:
        n = m/M
    else:
        n = None

    # Equação dos gases ideais: PV = mRT
    if P is None:
        P = (m * R_esp * T) / V
    elif V is None:
        V = (m * R_esp * T) / P
    elif m is None:
        m = (P * V) / (R_esp * T)
        n = m/M
    elif T is None:
        T = (P * V) / (m * R_esp)
    
    # Propriedades intensivas
    v = V/m         # Volume específico (m³/kg)
    u = cv * T      # Energia interna específica (J/kg)
    h = cp * T      # Entalpia específica (J/kg)
    s = cp * np.log(T/273.15) - R_esp * np.log(P/101325)  # Entropia específica (J/kg·K)
    
    # Propriedades extensivas
    U = u * m       # Energia interna total (J)
    H = h * m       # Entalpia total (J)
    S = s * m       # Entropia total (J/K)
    
    return P, V, m, T, v, u, h, s, U, H, S, n

def main():
    st.title("Calculadora de Propriedades Termodinâmicas")
    st.write("Insira os valores no Sistema Internacional (SI)")
    
    # Seleção do gás
    gas = st.selectbox("Selecione o gás", list(GASES.keys()))
    
    col1, col2 = st.columns(2)
    
    with col1:
        P = st.number_input("Pressão (Pa)", value=None, placeholder="Digite a pressão")
        V = st.number_input("Volume (m³)", value=None, placeholder="Digite o volume")
    
    with col2:
        m = st.number_input("Massa (kg)", value=None, placeholder="Digite a massa")
        T = st.number_input("Temperatura (K)", value=None, placeholder="Digite a temperatura")
    
    # Verifica se apenas uma variável está faltando
    valores = [P, V, m, T]
    if valores.count(None) != 1:
        st.warning("Por favor, deixe exatamente uma variável em branco para calcular")
        return
    
    if st.button("Calcular"):
        P, V, m, T, v, u, h, s, U, H, S, n = calcular_propriedades(P, V, m, T, gas)
        
        st.write("### Resultados:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("#### Propriedades Extensivas:")
            st.write(f"Pressão: {P:.2f} Pa")
            st.write(f"Volume: {V:.6f} m³")
            st.write(f"Massa: {m:.6f} kg")
            st.write(f"Número de mols: {n:.6f} mol")
            st.write(f"Temperatura: {T:.2f} K")
        
        with col2:
            st.write("#### Propriedades Intensivas:")
            st.write(f"Volume específico: {v:.6f} m³/kg")
            st.write(f"Energia interna específica: {u:.2f} J/kg")
            st.write(f"Entalpia específica: {h:.2f} J/kg")
            st.write(f"Entropia específica: {s:.2f} J/(kg·K)")
        
        with col3:
            st.write("#### Propriedades Totais:")
            st.write(f"Energia Interna: {U:.2f} J")
            st.write(f"Entalpia: {H:.2f} J")
            st.write(f"Entropia: {S:.2f} J/K")
        
        # Informações adicionais do gás
        st.write("### Propriedades do Gás:")
        st.write(f"Massa Molar: {GASES[gas]['M']:.6f} kg/mol")
        st.write(f"Razão de calores específicos (γ = cp/cv): {GASES[gas]['gamma']:.3f}")
        st.write(f"Calor específico a pressão constante (cp): {GASES[gas]['cp']:.2f} J/(kg·K)")
        st.write(f"Calor específico a volume constante (cv): {GASES[gas]['cp']/GASES[gas]['gamma']:.2f} J/(kg·K)")

if __name__ == "__main__":
    main()
