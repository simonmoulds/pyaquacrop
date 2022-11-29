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


class MaxTemperature(SpaceTimeDataArray):
    def __init__(self, config):
        filename = config['TMAX']['filename']
        super().__init__(
            config,
            filename,
            config['TMAX']['varname'],
            config['TMAX']['is_1d'],
            config['TMAX']['xy_dimname'],
            config['TMAX']['factor'],
            config['TMAX']['offset']
        )


class MinTemperature(SpaceTimeDataArray):
    def __init__(self, config):
        filename = config['TMAX']['filename']
        super().__init__(
            config,
            filename,
            config['TMIN']['varname'],
            config['TMIN']['is_1d'],
            config['TMIN']['xy_dimname'],
            config['TMIN']['factor'],
            config['TMIN']['offset']
        )


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


class Precipitation(SpaceTimeDataArray):
    def __init__(self, config):
        filename = config['TMAX']['filename']
        super().__init__(
            config,
            filename,
            config['TMIN']['varname'],
            config['TMIN']['is_1d'],
            config['TMIN']['xy_dimname'],
            config['TMIN']['factor'],
            config['TMIN']['offset']
        )

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


class _PenmanMonteith:
    def __init__(self, config):
        pass


class _Hargreaves:
    def __init__(self, config):
        pass


class _PriestleyTaylor:
    def __init__(self, config):
        pass


class ET0:
    VALID_METHODS = ['hargreaves', 'penman_monteith', 'priestley_taylor']
    def __init__(self, config):
        preprocess = bool(config['ET0']['preprocess'])
        if preprocess:
            method = str(config['ET0']['method']).lower()
            if method == "hargreaves":
                _Hargreaves(config)
            elif method == "penman_monteith":
                _PenmanMonteith(config)
            elif method == "priestley_taylor":
                _PriestleyTaylor(config)
            else:
                raise ValueError("Invalid `method` in config: must be one of `hargreaves`, `penman_monteith`, `priestley_taylor`")
        else:
            filename = config['TMAX']['filename']
            super().__init__(
                config,
                filename,
                config['ET0']['varname'],
                config['ET0']['is_1d'],
                config['ET0']['xy_dimname'],
                config['ET0']['factor'],
                config['ET0']['offset']
            )
