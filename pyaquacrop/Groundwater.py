#!/usr/bin/env python3

import os
import math
import pickle
import pkgutil
from typing import Dict, Optional, Union, Tuple
from abc import ABC, abstractmethod, abstractproperty

from utils import format_parameter


def _variable_groundwater_header(start_day=1, start_month=1, start_year=1901):

    header = (
        "Variable groundwater depth and salinity"
        + os.linesep
        + format_parameter("7.0", 6, 4)
        + ": AquaCrop Version"
        + os.linesep
        + format_parameter("2", 6, 4)
        + ": variable groundwater table"
        + os.linesep
        + format_parameter(str(int(start_day)), 6, 4)
        + ": first day of observations"
        + os.linesep
        + format_parameter(str(int(start_month)), 6, 4)
        + ": first month of observations"
        + os.linesep
        + format_parameter(str(int(start_year)), 6, 4)
        + ": first year of observations (1901 if not linked to a specific year)"
        + os.linesep
        + os.linesep
    )
    return header


def _constant_groundwater_header(start_day=1, start_month=1, start_year=1901):

    header = (
        "Constant groundwater depth and salinity"
        + os.linesep
        + format_parameter("7.0", 6, 4)
        + ": AquaCrop Version"
        + os.linesep
        + format_parameter("1", 6, 4)
        + ": constant groundwater table"
        + os.linesep
        + os.linesep
    )
    return header


class Groundwater:
    def __init__(self, model):
        self.model = model
        self.filename = model.config.GWT["filename"]
        self.nc_varname = model.config.GWT["varname"]
        self.is_1d = model.config.GWT["is_1d"]
        self.xy_dimname = model.config.GWT["xy_dimname"]
        self.factor = model.config.GWT["factor"]
        self.offset = model.config.GWT["offset"]

    def _write_variable_groundwater_input_file(self, filename):
        header = _variable_groundwater_header()
        with open(filename, 'w') as f:
            f.write(header)
            f.write("  Day    Depth (m)    ECw (dS/m)" + os.linesep)
            f.write("===================================" + os.linesep)

    def _write_constant_groundwater_input_file(self, filename):
        header = _constant_groundwater_header()
        with open(filename, 'w') as f:
            f.write(header)
            f.write("  Day    Depth (m)    ECw (dS/m)" + os.linesep)
            f.write("===================================" + os.linesep)
