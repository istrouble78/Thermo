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
    },

    'Air': {
        'range': [200, 1000, 6000],
        'low': [3.653116100000000, -0.001337110490000, 0.000003294385580, 
                -0.000000003554381000, 0.000000000001245493530, -1088.457720000000, 2.492667920000000],
        'high': [3.168267100000000, -0.000775064382000, 0.000000218741624, 
                 -0.0000000000268215301, 0.00000000000130309060, -976.086008000000, 5.456618000000000],
        'M': 0.028965000000000  # kg/mol
    },
    'CO2': {
        'range': [200, 1000, 6000],
        'low': [2.356773520000000, 0.008984596770000, -0.000007123562690, 
                0.00000000245919022, -0.000000000000143699548, -48372.783880000000, 9.901052220000000],
        'high': [3.857460290000000, 0.004414370260000, -0.000002214814040, 
                 0.000000000523490188, -0.0000000000000472084164, -48759.229490000000, 2.271638060000000],
        'M': 0.044010000000000  # kg/mol
    },
    'H2O': {
        'range': [200, 1000, 6000],
        'low': [4.198640560000000, -0.002036434100000, 0.000006520402110, 
                -0.00000000548797062, 0.00000000000177197817, -30293.726700000000, -0.849032208000000],
        'high': [3.033992490000000, 0.002176918040000, -0.000000164072518, 
                 -0.0000000000970419870, 0.000000000000168200992, -30004.297100000000, 4.966770100000000],
        'M': 0.018015000000000  # kg/mol
    },
    'CO': {
        'range': [200, 1000, 6000],
        'low': [3.579533470000000, -0.000610353680000, 0.000001016814330, 
                0.000000000907005884, -0.000000000000904424499, -14259.198200000000, 3.508409280000000],
        'high': [3.048485830000000, 0.001351728180000, -0.000000485794087, 
                 0.0000000000788536487, -0.000000000000469807364, -14343.413700000000, 5.083112560000000],
        'M': 0.028010000000000  # kg/mol
    },
    'H2': {
        'range': [200, 1000, 6000],
        'low': [2.344331120000000, 0.007980520750000, -0.000019478151000, 
                0.0000000201572094, -0.00000000000737611761, -917.935173000000, 0.683010238000000],
        'high': [3.337279200000000, -0.000049402473100, 0.000000499456778, 
                 -0.000000000179566394, 0.000000000000200255376, -950.158922000000, -3.205023310000000],
        'M': 0.002016000000000  # kg/mol
    },
    'CH4': {
        'range': [200, 1000, 6000],
        'low': [-0.703029000000000, 0.019699095400000, -0.0000256306321, 
                0.0000000133870761, -0.00000000000267130142, -10246.825700000000, 9.373558000000000],
        'high': [7.485149500000000, -0.000872615223000, 0.000000358016623, 
                 -0.0000000000671705034, 0.000000000000429163416, -10609.668000000000, -5.477997400000000],
        'M': 0.016040000000000  # kg/mol
    },
    'NO': {
        'range': [200, 1000, 6000],
        'low': [4.218598960000000, -0.004639881240000, 0.0000110443049, 
                -0.0000000104797478, 0.00000000000335420634, 992.682217000000, 2.631560530000000],
        'high': [3.260712340000000, 0.001191104430000, -0.000000429131560, 
                 0.0000000000694432917, -0.000000000000403295681, 984.596763000000, 4.961972790000000],
        'M': 0.030010000000000  # kg/mol
    },
    'NH3': {
        'range': [200, 1000, 6000],
        'low': [2.634452100000000, 0.006091338300000, -0.0000013359543, 
                0.0000000024507727, -0.0000000000015011802, -7452.112000000000, 6.076314000000000],
        'high': [4.205974000000000, -4.941406000000000, 0.002760429000000, 
                 -0.000000834112400, 0.000000000108346600, -6524.139000000000, 5.930927000000000],
        'M': 0.017031000000000  # kg/mol
    },
    'Ar': {
        'range': [200, 1000, 6000],
        'low': [2.500000000000000, 0.000000000000000, 0.000000000000000, 
                0.000000000000000, 0.000000000000000, -745.375000000000, 4.379674000000000],
        'high': [2.500000000000000, 0.000000000000000, 0.000000000000000, 
                 0.000000000000000, 0.000000000000000, -745.375000000000, 4.379674000000000],
        'M': 0.039948000000000  # kg/mol
    },
    'SO2': {
        'range': [200, 1000, 6000],
        'low': [4.568396200000000, 0.010942819000000, -0.0000055934091, 
                0.0000000011695911, -0.000000000000095934266, -35500.260000000000, 6.850472600000000],
        'high': [5.290237200000000, -0.000505084120000, 0.00000021100341, 
                 -0.000000000032036097, 0.0000000000017250179, -37870.470000000000, 3.397452200000000],
        'M': 0.064066000000000  # kg/mol
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
    st.image("logo_ufpr.jpg", use_column_width=True)  # Altere para o caminho da imagem ou URL
    st.title("Calculadora de Propriedades Termodinâmicas")
    st.write("Ferramenta desenvolvida pelo Prof. Strobel para a disciplina TMEC005 - Termodinâmica, do curso de Engenharia Mecânica da UFPR (2024)")
    st.caption("Propriedades baseadas no trabalho 'NASA Glenn Coefficients for Thermodynamic Properties of Individual Species', McBride, B. J., & Gordon, S. (1996). NASA Reference Publication 1311. NASA Glenn Research Center, Cleveland, Ohio. Disponível em: [NASA Technical Reports Server (NTRS) https://ntrs.nasa.gov/]")
    
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
