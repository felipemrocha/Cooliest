#!/usr/bin/env python3
# TODO make everything work with error checking (filenames, divide by zero, bla bla bla)

import argparse
import logging
from pathlib import Path

import cantera as ct
import numpy as np
import pandas as pd

from src.model.nist_janaf import get_fluid_properties_janaf


class Segment:
    def __init__(self, w, h, l, t_in, v_dot, q, fluid_name):
        """Initializes the channel segment.

        Inputs:
            w (float): Width of duct (bottom of inlet/outlet) (m)
            h (float): Height of duct (sides of inlet/outlet, not heated surface) (m)
            l (float): Length of channel (runs along heated surface) (m)
            t_in (float): Temperature of inlet fluid (K)
            t_dot (float): Volume flow rate of inlet fluid(m^3/s)
            q (float): Heat applied to bottom wall (W)
            fluid_name (string): Name of fluid

        Parameters:
            t_mid (float): Temperature in the middle of the segment (K)
            t_out (float): Temperature exiting the segment (K)
            t_wall (float): Temperature of heated surface (K)
        """
        # inputs
        self.w = w
        self.h = h
        self.l = l
        self.t_in = t_in
        self.v_dot = v_dot
        self.q = q
        self.fluid_name = fluid_name
        # parameters
        self.t_guess = 0
        self.t_mid = 0
        self.t_out = 0
        self.t_wall = 0

    def __get_properties(self, pressure=101_325):
        """Description:
        This function takes the pressure (default value = 101325 Pa) of the segment
        and returns the specific heat capacity, thermal conductivity, Prandtl number, kinematic viscosity,
        and density of the fluid at the given temperature and pressure.

        Parameters:
        - pressure (float, optional): The pressure of the fluid in Pascals. Default value is 101325 Pa.

        Returns:
        - cp (float): The specific heat capacity of the fluid in J/(kg*K).
        - k (float): The thermal conductivity of the fluid in W/(m*K).
        - pr (float): The Prandtl number of the fluid.
        - nu_k (float): The kinematic viscosity of the fluid in m^2/s.
        - rho (float): The density of the fluid in kg/m^3.

        NOTE: For `fluid_name="air"`, values may be different due to different definitions of
        an air mixture.
        """
        temp = self.t_guess

        if self.fluid_name == "air":
            fluid = ct.Solution(f"{self.fluid_name}.yaml")
            fluid.TP = temp, pressure
            cp = fluid.cp_mass
            rho = fluid.density
            k = fluid.thermal_conductivity
            nu_k = fluid.viscosity / fluid.density
            pr = (nu_k * cp) / k

        else:
            cp, k, pr, nu_k, rho = get_fluid_properties_janaf(
                self.fluid_name, temp, pressure
            )

        return cp, k, pr, nu_k, rho

    def __get_area(self):
        # NOTE assumes rectangular and constant across length
        return self.w * self.h

    def __get_fluid_table(self):
        current_path = Path(__file__).parent
        fluid_table_path = (
            current_path / f"../../data/model/{self.fluid_name}_table.xlsx"
        )
        fluid_table = pd.read_excel(fluid_table_path)
        return fluid_table

    def __get_perimeter(self):
        # NOTE assumes rectangular and constant across length
        return 2 * (self.w + self.h)

    def __get_nusselt(self, Re, Pr):
        # NOTE assumes turbulence begins at inlet
        # laminar
        if Re < 2300:
            return 4.364
        # turbulent
        else:
            return 0.23 * Re**0.8 * Pr**0.4

    def calculate_wall_temp(self):
        """Calculates the temperature of the bottom wall in a rectangular duct,
        where the bottom wall is producing a constant heat flux.
        """
        logging.info("Solving...")
        logging.debug(f"Input parameters: {locals()}")
        # calculate hydraulic diameter
        area = self.__get_area()
        perimeter = self.__get_perimeter()
        diameter_h = 4 * area / perimeter

        # estimate t_mid and t_out
        print_counter = 0
        dt = 0
        tol = 0.01
        self.t_mid = 0
        self.t_guess = self.t_in
        err_old = 10**7
        err_new = 10**6

        while err_new > tol:
            print_counter += 1

            if err_new >= err_old:
                dt = -0.01
            else:
                sign = -1 if (dt < 0) else 1
                if err_new <= 10:
                    dt = 0.01
                elif err_new >= 1000:
                    dt = 1
                else:
                    dt = err_new * 0.001
                dt = dt * sign

            self.t_guess += dt

            cp, k, prandtl, nu_k, rho = self.__get_properties()

            self.t_out = self.q / (rho * self.v_dot * cp) + self.t_in
            self.t_mid = (self.t_in + self.t_out) / 2

            err_old = err_new
            err_new = (self.t_guess - self.t_mid) ** 2

            if print_counter % 1000 == 999:
                logging.debug(
                    f"""---------------------------------------------------------\n
                    Iter: {print_counter}, T_guess: {self.t_guess:0.2f}, Err: {err_new:0.2f}\n
                    ---------------------------------------------------------\n"""
                )

        # calculate Reynold's number
        reynolds = self.v_dot * diameter_h / (area * nu_k)

        # estimate Nusselt number
        nusselt = self.__get_nusselt(reynolds, prandtl)

        # calculate heat coefficient
        h_coeff = nusselt * k / diameter_h

        # calculate wall temperature
        self.t_wall = self.q / (h_coeff * self.w * self.l) + self.t_mid

        logging.debug(f"Wall temperature: {self.t_wall:0.2f} K")


def calculate_parameters(w, h, l_in, l_chip, l_out, t_in, v_dot, q, fluid_name):
    """Creates and combines the segments of the channel to calculate all
    important parameters.

    Inputs:
        w (float): Width of duct (bottom of inlet/outlet) (m)
        h (float): Height of duct (sides of inlet/outlet, not heated surface) (m)
        l_in (float): Length of inlet channel (runs along heated surface) (m)
        l_chip (float): Length of chip channel (runs along heated surface) (m)
        l_out (float): Length of outlet channel (runs along heated surface) (m)
        t_in (float): Temperature of inlet fluid (K)
        t_dot (float): Volume flow rate of inlet fluid(m^3/s)
        q (float): Heat applied to bottom wall of chip segment (W)
        fluid_name (string): Name of fluid

    Parameters:
        t_chip (float): Temperature of heated surface (K)
        t_mid_chip (float): Temperature in the middle of the heated channel segment (K)
        t_out (float): Temperature exiting the channel (K)
    """
    # inlet segment
    q_in = 0.10 * q * l_in / (l_in + l_out)
    inlet = Segment(w, h, l_in, t_in, v_dot, q_in, fluid_name)
    inlet.calculate_wall_temp()

    # chip segment
    q_chip = 0.90 * q
    chip = Segment(w, h, l_chip, inlet.t_out, v_dot, q_chip, fluid_name)
    chip.calculate_wall_temp()

    # outlet segment
    q_out = 0.10 * q * l_out / (l_in + l_out)
    outlet = Segment(w, h, l_out, chip.t_out, v_dot, q_out, fluid_name)
    outlet.calculate_wall_temp()

    # summary
    t_chip = chip.t_wall
    t_mid_chip = chip.t_mid
    t_out = outlet.t_out

    return t_chip, t_mid_chip, t_out


def read_input_file(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
        w = float(lines[3].split()[-1])
        h = float(lines[4].split()[-1])
        l_in = float(lines[5].split()[-1])
        l_chip = float(lines[6].split()[-1])
        l_out = float(lines[7].split()[-1])
        T_in = float(lines[8].split()[-1])
        V_dot = float(lines[9].split()[-1])
        q = float(lines[10].split()[-1])
        fluid_name = lines[11].split()[-1]
    return w, h, l_in, l_chip, l_out, T_in, V_dot, q, fluid_name


def main():
    # ARG PARSING ==========================
    parser = argparse.ArgumentParser(
        description="Team Cooliest's ~ proprietary ~ model."
    )

    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode.")

    subparser = parser.add_subparsers(dest="subparser")

    # Input File ---------------------------
    inputfile = subparser.add_parser("inputfile")
    inputfile.add_argument(
        "-f", "--filename", type=str, required=True, help="Name of the input file."
    )

    # Arguments ----------------------------
    # help strings include SI units
    args = subparser.add_parser("args")
    args.add_argument(
        "--width", type=float, required=True, help="Width of the channel (m)."
    )
    args.add_argument(
        "--height", type=float, required=True, help="Height of the channel (m)."
    )
    args.add_argument(
        "--length-in",
        type=float,
        required=True,
        help="Length of the inlet segment (m).",
    )
    args.add_argument(
        "--length-chip",
        type=float,
        required=True,
        help="Length of the chip segment (m).",
    )
    args.add_argument(
        "--length-out", type=float, required=True, help="Length of the out segment (m)."
    )
    args.add_argument("--Tin", type=float, required=True, help="Inlet temperature (K).")
    args.add_argument(
        "--Vdot", type=float, required=True, help="Volumetric flow rate (m^3/s)."
    )
    args.add_argument(
        "--qChip", type=float, required=True, help="Heat generated by the chip (W)."
    )
    args.add_argument(
        "--fluid",
        type=float,
        required=True,
        help="The fluid flowing through the channel (-).",
    )

    pargs = parser.parse_args()
    if pargs.subparser == "inputfile":
        w, h, l_in, l_chip, l_out, T_in, V_dot, q, fluid_name = read_input_file(
            pargs.filename
        )
    elif pargs.subparser == "args":
        w = pargs.width
        h = pargs.height
        l_in = pargs.length_in
        l_chip = pargs.length_chip
        l_out = pargs.length_out
        T_in = pargs.Tin
        V_dot = pargs.Vdot
        q = pargs.qChip
        fluid_name = pargs.fluid

    if pargs.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # SOLVE ================================
    t_chip, t_mid_chip, t_out = calculate_parameters(
        w, h, l_in, l_chip, l_out, T_in, V_dot, q, fluid_name
    )

    # POST PROCESSING ======================
    logging.info(
        f"Temperature of the Heated Surface = {t_chip:.02f}K or {t_chip - 273.15:.02f}C"
    )


if __name__ == "__main__":
    main()
