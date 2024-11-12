import streamlit as st
import numpy as np
from scipy.constants import R
from scipy.optimize import fsolve

# [Mantendo o dicionário NASA_COEF anterior...]

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

def calcular_estado(variaveis_conhecidas, valores_conhecidos, gas):
    """
    Calcula todas as propriedades do estado termodinâmico dados dois parâmetros intensivos
    
    Args:
        variaveis_conhecidas: lista com os nomes das variáveis conhecidas
        valores_conhecidos: lista com os valores das variáveis conhecidas
        gas: string com o nome do gás
    """
    
    M = NASA_COEF[gas]['M']  # kg/mol
    R_esp = R/M              # J/(kg·K)
    
    def equacoes_estado(x, variaveis_conhecidas, valores_conhecidos):
        """Sistema de equações para resolver o estado termodinâmico"""
        # x contém as variáveis desconhecidas na ordem [P, T, v, h, s]
        P, T, v, h, s = x
        
        # Calcula propriedades usando correlações NASA
        coef = get_nasa_coef(T, gas)
        cp_R = calc_cp0_R(T, coef)
        h_RT = calc_h0_RT(T, coef)
        s_R = calc_s0_R(T, coef)
        
        # Equações de estado
        eq1 = P*v - R_esp*T  # Equação dos gases ideais
        eq2 = h - (h_RT * R * T/M)  # Definição de entalpia
        eq3 = s - (s_R * R/M - R_esp * np.log(P/101325))  # Definição de entropia
        
        # Substitui as variáveis conhecidas
        for var, val in zip(variaveis_conhecidas, valores_conhecidos):
            if var == 'P':
                eq1 = P - val
            elif var == 'T':
                eq2 = T - val
            elif var == 'v':
                eq3 = v - val
            elif var == 'h':
                eq4 = h - val
            elif var == 's':
                eq5 = s - val
        
        return [eq1, eq2, eq3, eq4, eq5]
    
    # Estimativa inicial
    x0 = [101325.0, 300.0, R_esp*300.0/101325.0, 0.0, 0.0]
    
    # Resolve o sistema de equações
    solucao = fsolve(equacoes_estado, x0, args=(variaveis_conhecidas, valores_conhecidos))
    
    P, T, v, h, s = solucao
    
    # Calcula as outras propriedades
    coef = get_nasa_coef(T, gas)
    cp_R = calc_cp0_R(T, coef)
    cp = cp_R * R/M
    cv = cp - R_esp
    u = h - P*v
    
    return P, T, v, h, s, u, cp, cv

def main():
    st.title("Calculadora de Propriedades Termodinâmicas (Estilo EES)")
    st.write("Propriedades baseadas em McBride et al. (2002)")
    
    # Seleção do gás
    gas = st.selectbox("Selecione o gás", list(NASA_COEF.keys()))
    
    # Seleção das variáveis independentes
    st.write("### Selecione duas variáveis intensivas independentes:")
    
    variaveis_disponiveis = ['P (Pressão)', 'T (Temperatura)', 'v (Volume específico)', 
                            'h (Entalpia específica)', 's (Entropia específica)']
    
    var1 = st.selectbox("Primeira variável:", variaveis_disponiveis)
    var2 = st.selectbox("Segunda variável:", 
                       [v for v in variaveis_disponiveis if v != var1])
    
    col1, col2 = st.columns(2)
    
    with col1:
        val1 = st.number_input(f"Valor de {var1}", value=None)
    
    with col2:
        val2 = st.number_input(f"Valor de {var2}", value=None)
    
    if st.button("Calcular"):
        # Prepara as variáveis para o cálculo
        var_names = [v.split()[0] for v in [var1, var2]]
        valores = [val1, val2]
        
        try:
            P, T, v, h, s, u, cp, cv = calcular_estado(var_names, valores, gas)
            
            st.write("### Resultados:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("#### Propriedades Termodinâmicas:")
                st.write(f"Pressão (P): {P:.2f} Pa")
                st.write(f"Temperatura (T): {T:.2f} K")
                st.write(f"Volume específico (v): {v:.6f} m³/kg")
                st.write(f"Energia interna específica (u): {u:.2f} J/kg")
                st.write(f"Entalpia específica (h): {h:.2f} J/kg")
                st.write(f"Entropia específica (s): {s:.2f} J/(kg·K)")
            
            with col2:
                st.write("#### Calores Específicos:")
                st.write(f"cp: {cp:.2f} J/(kg·K)")
                st.write(f"cv: {cv:.2f} J/(kg·K)")
                st.write(f"γ (cp/cv): {cp/cv:.3f}")
        
        except:
            st.error("Erro no cálculo. Verifique se os valores inseridos são válidos.")

if __name__ == "__main__":
    main()
