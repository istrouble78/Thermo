import streamlit as st
import numpy as np
from scipy.constants import R

# Coeficientes NASA para diferentes gases (McBride et al. 2002)
# Formato: [Tmin, Tmid, Tmax, [coef. baixa T], [coef. alta T]]
# Coeficientes: [a1, a2, a3, a4, a5, a6, a7] para cada faixa
NASA_COEF = {
    'N2': {
        'range': [200, 1000, 6000],
        'low': [3.53100528, -0.000123660988e-3, -5.02999433e-7, 
                2.43530612e-09, -1.40881235e-12, -1046.976863, 2.96747038],
        'high': [2.95257637, 1.39690040e-03, -4.92631603e-07, 
                 7.86010195e-11, -4.60755204e-15, -923.948688, 5.87188762],
        'M': 0.028014  # kg/mol
    },
    'O2': {
        'range': [200, 1000, 6000],
        'low': [3.78245636, -2.99673415e-03, 9.84730200e-06, 
                -9.68129508e-09, 3.24372836e-12, -1063.94356, 3.65767573],
        'high': [3.66096083, 6.56365523e-04, -1.41149485e-07, 
                 2.05797658e-11, -1.29913248e-15, -1215.97725, 3.41536184],
        'M': 0.032  # kg/mol
    },
    'He': {
        'range': [200, 1000, 6000],
        'low': [2.5, 0.0, 0.0, 0.0, 0.0, -745.375, 0.928723974],
        'high': [2.5, 0.0, 0.0, 0.0, 0.0, -745.375, 0.928723974],
        'M': 0.004003  # kg/mol
    },
    'H2': {
        'range': [200, 1000, 6000],
        'low': [2.34433112, 7.98052075e-03, -1.94781510e-05, 
                2.01572094e-08, -7.37611761e-12, -917.935173, 0.683010238],
        'high': [2.93286579, 8.26607967e-04, -1.46402335e-07, 
                 1.54100359e-11, -6.88804432e-16, -813.065597, -1.02432887],
        'M': 0.002016  # kg/mol
    }
}

def calc_cp0_R(T, coef):
    """Calcula cp0/R usando os coeficientes NASA"""
    return (coef[0] + coef[1]*T + coef[2]*T**2 + coef[3]*T**3 + coef[4]*T**4)

def calc_h0_RT(T, coef):
    """Calcula h0/RT usando os coeficientes NASA"""
    return (coef[0] + coef[1]*T/2 + coef[2]*T**2/3 + coef[3]*T**3/4 + 
            coef[4]*T**4/5 + coef[5]/T)

def calc_s0_R(T, coef):
    """Calcula s0/R usando os coeficientes NASA"""
    return (coef[0]*np.log(T) + coef[1]*T + coef[2]*T**2/2 + coef[3]*T**3/3 + 
            coef[4]*T**4/4 + coef[6])

def get_nasa_coef(T, gas):
    """Retorna os coeficientes NASA apropriados para a temperatura"""
    Tmin, Tmid, Tmax = NASA_COEF[gas]['range']
    if T < Tmid:
        return NASA_COEF[gas]['low']
    else:
        return NASA_COEF[gas]['high']

def calcular_propriedades(P, V, m, T, gas):
    """Calcula propriedades termodinâmicas usando correlações NASA"""
    if T is None or T < NASA_COEF[gas]['range'][0] or T > NASA_COEF[gas]['range'][2]:
        st.error(f"Temperatura deve estar entre {NASA_COEF[gas]['range'][0]} e {NASA_COEF[gas]['range'][2]} K")
        return None
    
    M = NASA_COEF[gas]['M']  # kg/mol
    R_esp = R/M              # J/(kg·K)
    
    # Obter coeficientes NASA para a temperatura atual
    coef = get_nasa_coef(T, gas)
    
    # Calcular cp, h, e s usando correlações NASA
    cp_R = calc_cp0_R(T, coef)
    h_RT = calc_h0_RT(T, coef)
    s_R = calc_s0_R(T, coef)
    
    cp = cp_R * R/M           # J/(kg·K)
    cv = cp - R_esp           # J/(kg·K)
    h = h_RT * R * T/M       # J/kg
    s0 = s_R * R/M           # J/(kg·K)
    
    # Equação dos gases ideais: PV = mRT
    if P is None:
        P = (m * R_esp * T) / V
    elif V is None:
        V = (m * R_esp * T) / P
    elif m is None:
        m = (P * V) / (R_esp * T)
    
    # Propriedades intensivas
    v = V/m                  # Volume específico (m³/kg)
    u = h - R_esp * T       # Energia interna específica (J/kg)
    s = s0 - R_esp * np.log(P/101325)  # Entropia específica (J/kg·K)
    
    # Propriedades extensivas
    U = u * m               # Energia interna total (J)
    H = h * m               # Entalpia total (J)
    S = s * m               # Entropia total (J/K)
    n = m/M                 # Número de mols
    
    return P, V, m, T, v, u, h, s, U, H, S, n, cp, cv

def main():
    st.title("Calculadora de Propriedades Termodinâmicas")
    st.write("Propriedades baseadas em McBride et al. (2002)")
    
    # Seleção do gás
    gas = st.selectbox("Selecione o gás", list(NASA_COEF.keys()))
    
    col1, col2 = st.columns(2)
    
    with col1:
        P = st.number_input("Pressão (Pa)", value=None, placeholder="Digite a pressão")
        V = st.number_input("Volume (m³)", value=None, placeholder="Digite o volume")
    
    with col2:
        m = st.number_input("Massa (kg)", value=None, placeholder="Digite a massa")
        T = st.number_input("Temperatura (K)", value=None, 
                          min_value=float(NASA_COEF[gas]['range'][0]),
                          max_value=float(NASA_COEF[gas]['range'][2]))
    
    # Verifica se apenas uma variável está faltando
    valores = [P, V, m, T]
    if valores.count(None) != 1:
        st.warning("Por favor, deixe exatamente uma variável em branco para calcular")
        return
    
    if st.button("Calcular"):
        resultado = calcular_propriedades(P, V, m, T, gas)
        if resultado is None:
            return
            
        P, V, m, T, v, u, h, s, U, H, S, n, cp, cv = resultado
        
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
            st.write(f"cp: {cp:.2f} J/(kg·K)")
            st.write(f"cv: {cv:.2f} J/(kg·K)")
            st.write(f"γ (cp/cv): {cp/cv:.3f}")

if __name__ == "__main__":
    main()
