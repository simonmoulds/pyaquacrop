#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import netCDF4 as nc
import sqlite3
from importlib_resources import path

# from hm.api import open_hmdataarray
# from .utils import read_parameter_from_sqlite
# from . import data
# import aquacrop_fc

# # Soil input

# # TESTING
# dz = [4.0]  # m
# th_sat = [41.0]  # %
# th_fc = [22.0]  # %
# th_wp = [10.0]  # %
# k_sat = [1200.0]  # mm/day
# penetrability = [100.0]  # %
# gravel = [0.0]  # %
# CRa = [-0.3232]  # ???
# CRb = [0.219363]  # ???
# description = ["sandy loam"]  # ???

# # Crop calendar input
def _soil_data_header():
    header = (
        "This is a test - put something more meaningful here"
        + LINESEP
        + "7.0".rjust(5)
        + "  : AquaCrop Version"
        + LINESEP
        + str(int(curve_number)).rjust(5)
        + "  : CN (Curve Number)"
        + LINESEP
        + str(int(readily_evaporable_water)).rjust(5)
        + "  : Readily evaporable water from top layer (mm)"
        + LINESEP
        + str(int(n_horizon)).rjust(5)
        + "  : Number of soil horizons"
        + LINESEP
        + "-9".rjust(5)
        + "  : N/a"
        + LINESEP
        + LINESEP
    )

def _write_soil_profile_input_file():
    # This file is read by LoadProfile() in global.f90 L7550
    # L7617 read(fhandle, *) thickness_temp, SAT_temp, FC_temp, WP_temp, &
    #                        infrate_temp, penetrability_temp, &
    #                        gravelm_temp, cra_temp, crb_temp, &
    #                        description_temp
    # See https://stackoverflow.com/a/1126064 for an explanation of
    # Fortran read() statements
    header = _soil_data_header()
    header = (
        header
        + "  Thickness  Sat   FC    WP     Ksat   Penetrability  Gravel  CRa       CRb           description"
        + LINESEP
        + "  ---(m)-   ----(vol %)-----  (mm/day)      (%)        (%)    -----------------------------------------"
    )

    with open(os.path.join(sub_dir, filename), "w") as f:
        f.write(header)
        for i in range(n_horizon):
            # Add newline
            f.write(LINESEP)
            # Formatting taken from L4005 global.f90
            profile = (
                "{:8.2f}".format(thickness[i])
                + "{:8.1f}".format(th_sat[i])
                + "{:6.1f}".format(th_fc[i])
                + "{:6.1f}".format(th_wp[i])
                + "{:8.1f}".format(k_sat[i])
                + "{:11d}".format(int(penetrability[i]))
                + "{:10d}".format(int(gravel_content[i]))
                + "{:14.6f}".format(CRa[i])
                + "{:10.6f}".format(CRb[i])
                + profile_description[i][:10]
            )
            f.write(profile)
    return None

class Soil:
    def __init__(self, model):
        self.model = model
        # NOT CURRENTLY IMPLEMENTED:
        # self.model.adjustReadilyAvailableWater = \
        #     self.model.config.SOIL_PARAMETERS['adjustReadilyAvailableWater']
        self.model.adjustCurveNumber = self.model.config.SOIL_PARAMETERS[
            "adjustCurveNumber"
        ]
        self.load_soil_parameter_database()

    # def initial(self):
    #     self.read_soil_parameters()

    #     self.model.CNbot = np.zeros((self.model.domain.nxy))
    #     self.model.CNtop = np.zeros((self.model.domain.nxy))
    #     self.model.REW = np.zeros((self.model.domain.nxy))

    #     aquacrop_fc.soil_parameters_w.compute_soil_parameters_w(
    #         self.model.CNbot.T,
    #         self.model.CNtop.T,
    #         self.model.REW.T,
    #         self.model.zGerm.T,
    #         self.model.CN.T,
    #         self.model.th_fc.T,
    #         self.model.th_dry.T,
    #         self.model.EvapZsurf.T,
    #         self.model.zCN.T,
    #         self.model.dz_sum,
    #         self.model.nComp, self.model.nLayer, self.model.domain.nxy
    #     )

    def load_soil_parameter_database(self):
        with path(data, "soil_parameter_database.sqlite3") as db_path:
            try:
                db_path = db_path.resolve()
            except FileNotFoundError:
                pass
            self.model.SoilParameterDatabase = sqlite3.connect(str(db_path))

    def read_soil_parameters(self):
        soil_parameters = [
            "EvapZsurf",
            "EvapZmin",
            "EvapZmax",
            "Kex",
            "fevap",
            "fWrelExp",
            "fwcc",
            "CN",
            "zCN",
            "zGerm",
            "zRes",
            "fshape_cr",
        ]
        for param in soil_parameters:
            # First try to get parameter from config
            # Then from file
            # Last from default parameter database
            pass
            # try:
            #     arr = open_hmdataarray(
            #         self.model.config.SOIL_PARAMETERS['filename'],
            #         param,
            #         self.model.domain,
            #         self.model.config.SOIL_PARAMETERS['is_1d'],
            #         self.model.config.SOIL_PARAMETERS['xy_dimname'],
            #     )
            #     vars(self.model)[param] = np.require(
            #         arr.values,
            #         requirements=['A','O','W','F']
            #     )

            # except:
            #     try:
            #         parameter_value = read_parameter_from_sqlite(
            #             self.model.SoilParameterDatabase,
            #             param
            #         )
            #         parameter_value = np.array(
            #             parameter_value[0],
            #             dtype=np.float64
            #         )
            #         vars(self.model)[param] = np.require(
            #             np.full(self.model.domain.nxy, parameter_value),
            #             requirements=['A','O','W','F']
            #         )
            #     except:
            #         pass

    def dynamic(self):
        pass
