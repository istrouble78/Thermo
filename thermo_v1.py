import streamlit as st

# Título do aplicativo
st.title('Calculadora de Propriedades Termodinâmicas')

st.write('Todas as entradas e saídas estão em unidades do SI.')

# Constante dos gases ideais (J/(mol·K))
R = 8.314462618

# Seleciona a variável a ser calculada
opcao = st.selectbox('Selecione a variável que deseja calcular:', ('Pressão (P)', 'Volume (V)', 'Temperatura (T)', 'Quantidade de substância (n)'))

if opcao == 'Pressão (P)':
    V = st.number_input('Insira o Volume (V) em metros cúbicos (m³):', min_value=0.0, format="%f")
    n = st.number_input('Insira a Quantidade de Substância (n) em moles (mol):', min_value=0.0, format="%f")
    T = st.number_input('Insira a Temperatura (T) em Kelvin (K):', min_value=0.0, format="%f")
    if st.button('Calcular Pressão'):
        if V > 0:
            P = (n * R * T) / V
            st.write(f'Pressão Calculada (P): {P} Pascals (Pa)')
        else:
            st.write('O Volume deve ser maior que zero.')

elif opcao == 'Volume (V)':
    P = st.number_input('Insira a Pressão (P) em Pascals (Pa):', min_value=0.0, format="%f")
    n = st.number_input('Insira a Quantidade de Substância (n) em moles (mol):', min_value=0.0, format="%f")
    T = st.number_input('Insira a Temperatura (T) em Kelvin (K):', min_value=0.0, format="%f")
    if st.button('Calcular Volume'):
        if P > 0:
            V = (n * R * T) / P
            st.write(f'Volume Calculado (V): {V} metros cúbicos (m³)')
        else:
            st.write('A Pressão deve ser maior que zero.')

elif opcao == 'Temperatura (T)':
    P = st.number_input('Insira a Pressão (P) em Pascals (Pa):', min_value=0.0, format="%f")
    V = st.number_input('Insira o Volume (V) em metros cúbicos (m³):', min_value=0.0, format="%f")
    n = st.number_input('Insira a Quantidade de Substância (n) em moles (mol):', min_value=0.0, format="%f")
    if st.button('Calcular Temperatura'):
        if n > 0:
            T = (P * V) / (n * R)
            st.write(f'Temperatura Calculada (T): {T} Kelvin (K)')
        else:
            st.write('A Quantidade de Substância deve ser maior que zero.')

elif opcao == 'Quantidade de substância (n)':
    P = st.number_input('Insira a Pressão (P) em Pascals (Pa):', min_value=0.0, format="%f")
    V = st.number_input('Insira o Volume (V) em metros cúbicos (m³):', min_value=0.0, format="%f")
    T = st.number_input('Insira a Temperatura (T) em Kelvin (K):', min_value=0.0, format="%f")
    if st.button('Calcular Quantidade de Substância'):
        if T > 0:
            n = (P * V) / (R * T)
            st.write(f'Quantidade de Substância Calculada (n): {n} moles (mol)')
        else:
            st.write('A Temperatura deve ser maior que zero.')
