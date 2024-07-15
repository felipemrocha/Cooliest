## multiply cp by 1000
import pandas as pd
import numpy as np


def get_fluid_properties_janaf(fluid_name, temp, pressure):
    """Description:
    This function takes in the name of a fluid, temperature, and pressure (default value = 101325 Pa)
    and returns the specific heat capacity, thermal conductivity, Prandtl number, kinematic viscosity,
    and density of the fluid at the given temperature and pressure from a table with the values acquired from JANAF

    Parameters:
    - fluid_name (str): The name of the fluid as a string.
    - temp (float): The temperature of the fluid in Kelvin.
    - pressure (float, optional): The pressure of the fluid in Pascals. Default value is 101325 Pa.

    Returns:
    - cp (float): The specific heat capacity of the fluid in J/(kg*K).
    - k (float): The thermal conductivity of the fluid in W/(m*K).
    - pr (float): The Prandtl number of the fluid.
    - nu_k (float): The kinematic viscosity of the fluid in m^2/s.
    - rho (float): The density of the fluid in kg/m^3.


    """
    if fluid_name == "sf6":
        id = "C2551624"

    url = f"https://webbook.nist.gov/cgi/fluid.cgi?T={temp}&PLow={pressure}&PHigh={pressure}&PInc=0&Digits=5&ID={id}&Action=Load&Type=IsoTherm&TUnit=K&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fmol&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm&RefState=DEF"
    df = pd.read_html(url)
    table = df[0].iloc[0, :]

    cp = table["Cp (J/mol*K)"] * 1000
    k = table["Therm. Cond. (W/m*K)"]
    nu = table["Viscosity (uPa*s)"]
    rho = table["Density (kg/m3)"]
    nu_k = nu / rho
    pr = nu * cp / k

    return cp, k, pr, nu_k, rho
