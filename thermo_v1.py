import streamlit as st
import numpy as np
from scipy.constants import R
from scipy.optimize import fsolve

# Definição dos coeficientes NASA
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
    }

    'Air': {
        'range': [200, 1000, 6000],
        'low': [3.65311610, -1.33711049e-03, 3.29438558e-06, 
                -3.55438100e-09, 1.24549353e-12, -1088.45772, 2.49266792],
        'high': [3.16826710, -7.75064382e-04, 2.18741624e-07, 
                 -2.68215301e-11, 1.30309060e-15, -976.086008, 5.45661800],
        'M': 0.028965  # kg/mol
    },

    'CO2': {
        'range': [200, 1000, 6000],
        'low': [2.35677352, 8.98459677e-03, -7.12356269e-06, 
                2.45919022e-09, -1.43699548e-13, -48372.78388, 9.90105222],
        'high': [3.85746029, 4.41437026e-03, -2.21481404e-06, 
                 5.23490188e-10, -4.72084164e-14, -48759.22949, 2.27163806],
        'M': 0.04401  # kg/mol
    },

    'H2O': {
        'range': [200, 1000, 6000],
        'low': [4.19864056, -2.03643410e-03, 6.52040211e-06, 
                -5.48797062e-09, 1.77197817e-12, -30293.7267, -0.849032208],
        'high': [3.03399249, 2.17691804e-03, -1.64072518e-07, 
                 -9.70419870e-11, 1.68200992e-14, -30004.2971, 4.96677010],
        'M': 0.018015  # kg/mol
    },

    'CO': {
        'range': [200, 1000, 6000],
        'low': [3.57953347, -6.10353680e-04, 1.01681433e-06, 
                9.07005884e-10, -9.04424499e-13, -14259.1982, 3.50840928],
        'high': [3.04848583, 1.35172818e-03, -4.85794087e-07, 
                 7.88536487e-11, -4.69807364e-15, -14343.4137, 5.08311256],
        'M': 0.02801  # kg/mol
    },

    'H2': {
        'range': [200, 1000, 6000],
        'low': [2.34433112, 7.98052075e-03, -1.94781510e-05, 
                2.01572094e-08, -7.37611761e-12, -917.935173, 0.683010238],
        'high': [3.33727920, -4.94024731e-05, 4.99456778e-07, 
                 -1.79566394e-10, 2.00255376e-14, -950.158922, -3.20502331],
        'M': 0.002016  # kg/mol
    },

    'CH4': {
        'range': [200, 1000, 6000],
        'low': [-0.7030290, 1.96990954e-02, -2.56306321e-05, 
                1.33870761e-08, -2.67130142e-12, -10246.8257, 9.3735580],
        'high': [7.48514950, -8.72615223e-04, 3.58016623e-07, 
                 -6.71705034e-11, 4.29163416e-15, -10609.6680, -5.4779974],
        'M': 0.01604  # kg/mol
    },

    'NO': {
        'range': [200, 1000, 6000],
        'low': [4.21859896, -4.63988124e-03, 1.10443049e-05, 
                -1.04797478e-08, 3.35420634e-12, 992.682217, 2.63156053],
        'high': [3.26071234, 1.19110443e-03, -4.29131560e-07, 
                 6.94432917e-11, -4.03295681e-15, 984.596763, 4.96197279],
        'M': 0.03001  # kg/mol
    },

    'NH3': {
        'range': [200, 1000, 6000],
        'low': [2.6344521, 6.0913383e-03, -1.3359543e-06, 
                2.4507727e-09, -1.5011802e-12, -7452.112, 6.076314],
        'high': [4.205974, -4.941406, 2.760429e-03, -8.341124e-07, 
                 1.083466e-10, -6524.139, 5.930927],
        'M': 0.017031  # kg/mol
    },

    'Ar': {
        'range': [200, 1000, 6000],
        'low': [2.5000000, 0.0, 0.0, 0.0, 0.0, -745.375, 4.379674],
        'high': [2.5000000, 0.0, 0.0, 0.0, 0.0, -745.375, 4.379674],
        'M': 0.039948  # kg/mol
    },

    'SO2': {
        'range': [200, 1000, 6000],
        'low': [4.5683962, 1.0942819e-02, -5.5934091e-06, 
                1.1695911e-09, -9.5934266e-14, -35500.26, 6.8504726],
        'high': [5.2902372, -5.0508412e-04, 2.1100341e-07, 
                 -3.2036097e-11, 1.7250179e-15, -37870.47, 3.3974522],
        'M': 0.064066  # kg/mol
    }
}

def calc_propriedades_base(T, P, gas):
    """Calcula as propriedades básicas usando correlações NASA"""
    M = NASA_COEF[gas]['M']
    R_esp = R/M
    
    # Seleciona coeficientes apropriados
    if T < NASA_COEF[gas]['range'][1]:
        coef = NASA_COEF[gas]['low']
    else:
        coef = NASA_COEF[gas]['high']
    
    # Calcula propriedades adimensionais
    cp_R = coef[0] + coef[1]*T + coef[2]*T**2 + coef[3]*T**3 + coef[4]*T**4
    h_RT = coef[0] + coef[1]*T/2 + coef[2]*T**2/3 + coef[3]*T**3/4 + coef[4]*T**4/5 + coef[5]/T
    s_R = coef[0]*np.log(T) + coef[1]*T + coef[2]*T**2/2 + coef[3]*T**3/3 + coef[4]*T**4/4 + coef[6]
    
    # Converte para unidades dimensionais
    cp = cp_R * R/M
    h = h_RT * R * T/M
    s = s_R * R/M - R_esp * np.log(P/101325)
    
    return cp, h, s

def resolver_estado(var1_nome, var1_valor, var2_nome, var2_valor, gas):
    """Resolve o estado termodinâmico dados dois parâmetros"""
    def equacoes(x):
        T, P = x
        cp, h, s = calc_propriedades_base(T, P, gas)
        M = NASA_COEF[gas]['M']
        R_esp = R/M
        v = R_esp*T/P
        
        eq1 = 0
        eq2 = 0
        
        # Define as equações com base nas variáveis conhecidas
        if var1_nome == 'T':
            eq1 = T - var1_valor
        elif var1_nome == 'P':
            eq1 = P - var1_valor
        elif var1_nome == 'h':
            eq1 = h - var1_valor
        elif var1_nome == 's':
            eq1 = s - var1_valor
        elif var1_nome == 'v':
            eq1 = v - var1_valor
            
        if var2_nome == 'T':
            eq2 = T - var2_valor
        elif var2_nome == 'P':
            eq2 = P - var2_valor
        elif var2_nome == 'h':
            eq2 = h - var2_valor
        elif var2_nome == 's':
            eq2 = s - var2_valor
        elif var2_nome == 'v':
            eq2 = v - var2_valor
            
        return [eq1, eq2]
    
    # Estimativa inicial
    x0 = [300, 101325]  # T = 300K, P = 1 atm
    
    try:
        solucao = fsolve(equacoes, x0)
        T, P = solucao
        cp, h, s = calc_propriedades_base(T, P, gas)
        M = NASA_COEF[gas]['M']
        R_esp = R/M
        v = R_esp*T/P
        u = h - P*v
        cv = cp - R_esp
        
        return T, P, v, u, h, s, cp, cv
    except:
        st.error("Não foi possível encontrar uma solução. Verifique os valores de entrada.")
        return None

def main():
    st.title("Calculadora de Propriedades Termodinâmicas")
    st.caption("Ferramenta desenvolvida pelo Prof. Strobel para a disciplina TMEC005 - Termodinâmica, do curso de Engenharia Mecânica da UFPR (2024)")
    st.write("Propriedades baseadas em McBride et al. (2002)")
    
    # Seleção do gás
    gas = st.selectbox("Selecione o gás", list(NASA_COEF.keys()))
    
    # Seleção das variáveis independentes
    variaveis = ['T', 'P', 'v', 'h', 's']
    nomes_variaveis = {
        'T': 'Temperatura [K]',
        'P': 'Pressão [Pa]',
        'v': 'Volume específico [m³/kg]',
        'h': 'Entalpia específica [J/kg]',
        's': 'Entropia específica [J/kg·K]'
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        var1 = st.selectbox("Primeira variável:", variaveis)
        val1 = st.number_input(f"Valor de {nomes_variaveis[var1]}", value=None)
    
    with col2:
        var2 = st.selectbox("Segunda variável:", 
                           [v for v in variaveis if v != var1])
        val2 = st.number_input(f"Valor de {nomes_variaveis[var2]}", value=None)
    
    if st.button("Calcular") and val1 is not None and val2 is not None:
        resultado = resolver_estado(var1, val1, var2, val2, gas)
        
        if resultado is not None:
            T, P, v, u, h, s, cp, cv = resultado
            
            st.write("### Resultados:")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("#### Propriedades do Estado:")
                st.write(f"Temperatura (T): {T:.2f} K")
                st.write(f"Pressão (P): {P:.2f} Pa")
                st.write(f"Volume específico (v): {v:.6f} m³/kg")
                st.write(f"Energia interna (u): {u:.2f} J/kg")
                st.write(f"Entalpia (h): {h:.2f} J/kg")
                st.write(f"Entropia (s): {s:.2f} J/kg·K")
            
            with col2:
                st.write("#### Calores Específicos:")
                st.write(f"cp: {cp:.2f} J/kg·K")
                st.write(f"cv: {cv:.2f} J/kg·K")
                st.write(f"γ (cp/cv): {cp/cv:.3f}")

if __name__ == "__main__":
    main()
