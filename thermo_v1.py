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
