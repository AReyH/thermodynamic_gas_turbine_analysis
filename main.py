import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
#import math


def density(T1, T2):
    T1_SI = (T1 - 32) * (5 / 9) + 273.15
    T2_SI = (T2 - 32) * (5 / 9) + 273.15

    Ta = (T1_SI + T2_SI) / 2
    a0 = 8.78552
    a1 = -7.54226 * (10 ** -2)
    a2 = 2.69671 * (10 ** -4)
    a3 = -3.42800 * (10 ** -7)
    rho = a0 + a1 * Ta + a2 * Ta ** 2 + a3 * Ta ** 3

    rho *= 0.062428

    return rho


def cp(T1, T2):
    T1_SI = (T1 - 32) * (5 / 9) + 273.15
    T2_SI = (T2 - 32) * (5 / 9) + 273.15

    Ta = (T1_SI + T2_SI) / 2
    a0 = 1.1788
    a1 = -2.8765 * (10 ** -3)
    a2 = 1.8105 * (10 ** -5)
    a3 = -5.1000 * (10 ** -8)
    a4 = 5.4000 * (10 ** -11)
    cp = a0 + a1 * Ta + a2 * Ta ** 2 + a3 * Ta ** 3 + a4 * Ta ** 4

    cp = (cp / 4.1868)

    return cp


def new_thermodynamic_efficiency(rho_aire=0.0629, rho_gas=0.056, T_comb_prom=1100, LHV=21213.67, Tdb=90, p2c=218,
                                 f_gas=1800000):
    # Environmental Conditions

    Twb = 88
    Wsamb = 201  # grain/lb

    #Hr = 100 * math.exp((Twb - Tdb) / 28.116) - 17.4935 * (Tdb - Twb) * math.exp(-Tdb / 28.116)

    # Evaporative Cooler Performance

    n_evap = 0.8

    T1 = -n_evap * (Tdb - Twb) / 100 + Tdb

    # Compressor Efficiency & Power Required
    m_aire = rho_aire * 760000 / 60
    gamma_a = 1.4
    gamma_g = 1.33
    nc_asumida = 0.946
    rp = p2c / 14.7
    rpa = (rp ** ((gamma_a - 1) / gamma_a) - 1) / nc_asumida
    rpg = (1 - (1 / (rp ** ((gamma_g - 1) / gamma_g))))
    T2 = (T1 + 460.67) * (1 + rpa)
    T2 = T2 - 460.67

    nc = (((rp ** ((gamma_a - 1) / gamma_a)) - 1) * (T1 + 460.67)) / (T2 - T1)

    Wc = m_aire * 3600 * cp(T1, T2) * (T1 + 460) * (((rp ** ((gamma_a - 1) / gamma_a)) - 1)) / (nc * 3412230)

    # Turbine Efficiency and Power Output
    m_gas = rho_gas * f_gas / (60 * 60)
    pit = 0.98 * p2c

    T3 = (T_comb_prom + 460.67) * (pit / 14.7) ** ((gamma_a - 1) / gamma_a)
    T3 -= 460.67

    f_agua = 500 * 6.309 * 10 ** -5  # GPM
    m_agua = f_agua * 997

    cp_aire = cp(T1, T2)
    cp_gas = 0.56
    cp_agua = 1

    cp_mix = (cp_aire * m_aire + cp_gas * m_gas + cp_agua * m_agua) / (m_aire + m_gas + m_agua)
    cp_comb = (cp_aire * m_aire + cp_gas * m_gas) / (m_aire + m_gas)

    hfg = 1036.91

    T3_c = T3 - m_agua * hfg / ((m_aire + m_gas) * cp_comb)

    nt = (1 - (T_comb_prom + 460.67) / (T3_c + 460.67)) / (1 - (14.7 / pit))

    Pturb = (m_aire + m_gas + m_agua) * 3600 * cp_mix * nt * (3159 + 460.67) * (
    (1 - (14.7 / pit) ** ((gamma_a - 1) / gamma_a))) / (3412230)
    Pt = Pturb - Wc

    n_gen = 0.97

    nth = Pt * n_gen * 100 / (m_gas * 3600 * LHV * 0.29307 / 1000000) + 10

    HR = 3600 * 100 / nth

    SFC = 3600 * (m_aire / m_gas) / (Pt / (m_aire + m_gas + m_agua))

    print(T2)

    return nth, HR, Pt, SFC


def streamlit_code():
    st.title("Thermodynamic Analysis of a Gas Turbine")
    st.markdown('')
    st.markdown('')
    st.markdown('')
    st.markdown('**Ingrese la temperatura de bulbo seco en `F: **')
    T_1 = st.number_input('')
    #f = st.number_input('Ingrese flujo volumetrico del Gas en MBTU/H: ')



    return T_1

def show_plot(nth, HR, Pt, SFC):
    Tdbs = [i for i in np.linspace(60, 100, 41)]
    nth_list = []
    HR_list = []
    Pt_list = []
    SFC_list = []

    for j in Tdbs:
        nth, HR, Pt, SFC = new_thermodynamic_efficiency(Tdb=j)
        nth_list.append(nth)
        HR_list.append(HR)
        Pt_list.append(Pt)
        SFC_list.append(SFC)

    # create figure and axis objects with subplots()
    fig, ax = plt.subplots(figsize=(15, 10))
    # make a plot
    ax.plot(Tdbs, HR_list, color="red", marker="o")
    # set x-axis label
    ax.set_xlabel("Temperatura de Bulbo Seco (°F)", fontsize=14)
    # set y-axis label
    ax.set_ylabel("Heat Rate (BTU/kW)", color="red", fontsize=14)

    # twin object for two different y-axis on the sample plot
    ax2 = ax.twinx()
    # make a plot with different y-axis using second axis object
    ax2.plot(Tdbs, nth_list, color="blue", marker="o")
    ax2.set_ylabel("Eficiencia Térmica (%)", color="blue", fontsize=14)
    st.pyplot(fig)

if __name__ == '__main__':

    T_1= streamlit_code()
    if T_1 > 0:
        nth, HR, Pt, SFC = new_thermodynamic_efficiency(Tdb=T_1)
        st.markdown(f'*La eficiencia termica de la turbina es {round(nth,2)}%*')
        st.markdown(f'*El Heat Rate de la turbina es {round(HR,2)} BTU/kW*')
        st.markdown(f'*La potencia entregada por la turbina es {round(Pt,1)} MW*')
        #st.markdown(SFC)

        show_plot(nth, HR, Pt, SFC)
