#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import numpy as np
import pandas as pd
import xarray
# from hm.api import open_hmdataarray
# from hm.input import HmInputData

class SpaceTimeDataArray:
    def __init__(self,
                 config,
                 filename,
                 varname,
                 # nc_varname,
                 # model_varname,
                 is_1d=False,
                 xy_dimname=None,
                 factor=1.,
                 offset=0.):

        self.config = config
        self._parse_filename(filename)
        self.varname = varname
        self.is_1d = is_1d
        self.xy_dimname = xy_dimname
        self.factor = factor
        self.offset = offset

    def _parse_filename(self, raw_filename):
        path = os.path.dirname(raw_filename)
        filename = os.path.basename(raw_filename)
        if ~os.path.isabs(path):
            path = os.path.join(self.config['configpath'], path)
        regex = re.compile(str(filename))
        filenames = [os.path.join(path, f) for f in os.listdir(path) if regex.match(f)]
        self.filenames = filenames

    def initial(self):
        self._data = xarray.open_mfdataset(self.filenames)

    def select(self, lat, lon):
        self._data_subset = self._data.sel(lat=lat, lon=lon, method='nearest')

    @property
    def values(self):
        return (self._data_subset[self.varname].values * self.factor) + self.offset


def _climate_data_header(start_date: pd.Timestamp) -> str:
    day, month, year = start_date.day, start_date.month, start_date.year
    header = (
        "This is a test - put something more meaningful here"
        + os.linesep
        + str(1).rjust(5)
        + "  : Daily records"
        + os.linesep
        + str(day).rjust(5)
        + "  : First day of record"
        + os.linesep
        + str(month).rjust(5)
        + "  : First month of record"
        + os.linesep
        + str(year).rjust(5)
        + "  : First year of record"
        + os.linesep
        + os.linesep
    )
    return header


class Weather(SpaceTimeDataArray):
    def __init__(self, config, config_section):
        super().__init__(
            config,
            config[config_section]['filename'],
            config[config_section]['varname'],
            config[config_section]['is_1d'],
            config[config_section]['xy_dimname'],
            config[config_section]['factor'],
            config[config_section]['offset']
        )


class MaxTemperature(Weather):
    def __init__(self, config):
        super().__init__(config, 'TMAX')


class MinTemperature(Weather):
    def __init__(self, config):
        super().__init__(config, 'TMIN')


class Temperature:
    def __init__(self, config):
        self.tmin = MaxTemperature(config)
        self.tmax = MaxTemperature(config)

    def initial(self):
        self.tmin.initial()
        self.tmax.initial()

    def select(self, lat, lon):
        self.tmin.select(lat, lon)
        self.tmax.select(lat, lon)

    @property
    def values(self):
        return np.column_stack((self.tmin.values, self.tmax.values))

    def _write_aquacrop_input(self, filename):
        header = _climate_data_header(pd.Timestamp(self.tmin._data_subset.time.values[0]))
        header += "  Tmin (C)   Tmax (C)" + os.linesep
        header += "======================="
        with open(filename, "w") as f:
            np.savetxt(
                f, self.values, fmt="%.2f", delimiter='\t',
                newline=os.linesep, header=header, comments=""
            )
        return None


class Precipitation(Weather):
    def __init__(self, config):
        super().__init__(config, 'PREC')

    def _write_aquacrop_input(self, filename):
        header = _climate_data_header(pd.Timestamp(self._data_subset.time.values[0]))
        header += "  Total Rain (mm)" + os.linesep
        header += "======================="
        with open(filename, "w") as f:
            np.savetxt(
                f, self.values, fmt="%.2f", delimiter="\t",
                newline=os.linesep, header=header, comments=""
            )
        return None


class _DewTemperature(SpaceTimeDataArray):
    def __init__(self, config):
        super().__init__(config, 'TDEW')


class _WindSpeed(SpaceTimeDataArray):
    def __init__(self, config):
        super().__init__(config, 'WIND')


class _U_WindSpeed(SpaceTimeDataArray):
    def __init__(self, config):
        super().__init__(config, 'U_WIND')


class _SolarRadiation(SpaceTimeDataArray):
    def __init__(self, config):
        super().__init__(config, 'SRAD')


# Use this in config function?
def _check_valid_input(config, config_section):
    if config_section not in config.keys():
        return False
    if 'filename' not in config[config_section]:
        return False
    if not os.path.exists(config[config_section]['filename']):
        return False
    return True


class _ET0_PenmanMonteith:
    def __init__(self, config):
        self.tmin = MinTemperature(config)
        self.tmax = MaxTemperature(config)
        # Idea here is to have exactly the variables we need, and provide a class for that variable which either reads it directly or computes it from other variables


class _ET0_Hargreaves:
    def __init__(self, config):
        pass


class _ET0_PriestleyTaylor:
    def __init__(self, config):
        pass


class _ET0_FromFile:
    def __init__(self, config):
        super().__init__(config, 'ET0')


class ET0(SpaceTimeDataArray):
    VALID_METHODS = ['hargreaves', 'penman_monteith', 'priestley_taylor']
    def __init__(self, config):
        preprocess = bool(config['ET0']['preprocess'])
        if preprocess:
            method = str(config['ET0']['method']).lower()
            if method == "hargreaves":
                self.eto = _ET0_Hargreaves(config)
            elif method == "penman_monteith":
                self.eto = _ET0_PenmanMonteith(config)
            elif method == "priestley_taylor":
                self.eto = _ET0_PriestleyTaylor(config)
            else:
                raise ValueError("Invalid `method` in config: must be one of `hargreaves`, `penman_monteith`, `priestley_taylor`")
        else:
            self.eto = _ET0_FromFile(config)

    def initial(self):
        self.eto.initial()

    def select(self, lat, lon):
        self.eto.select(lat, lon)

    @property
    def values(self):
        return self.eto.values

    def _write_aquacrop_input(self, filename):
        header = _climate_data_header(pd.Timestamp(self._data_subset.time.values[0]))
        header += "  Total Rain (mm)" + os.linesep
        header += "======================="
        with open(filename, "w") as f:
            np.savetxt(
                f, self.values, fmt="%.2f", delimiter="\t",
                newline=os.linesep, header=header, comments=""
            )
        return None
