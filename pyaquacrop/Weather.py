#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import numpy as np
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
            config['TMAX']['xy_dimname']#,
            # config['TMAX']['factor'],
            # config['TMAX']['offset']
        )

    def _write_aquacrop_input(self):
        pass
        # header = _climate_data_header(self._data.time.values[0])
        # header = header + "  Total Rain (mm)" + os.linesep + "======================="
        # # X = x.sel(lat=latitude, lon=longitude, method="nearest")
        # with open(os.path.join(sub_dir, filename), "w") as f:
        #     np.savetxt(f, X, fmt="%.2f", newline=LINESEP, header=header, comments="")
        # return None


class MinTemperature:
    def __init__(self, model):
        self.model = model
        self.filename = model.config.weather.tmin["filename"]
        self.nc_varname = model.config.weather.tmin["varname"]
        self.is_1d = model.config.weather.tmin["is_1d"]
        self.xy_dimname = model.config.weather.tmin["xy_dimname"]
        self.factor = model.config.weather.tmin["factor"]
        self.offset = model.config.weather.tmin["offset"]


class Temperature:
    def __init__(self, model):
        self.tmin = MinTemperature(model)
        self.tmax = MaxTemperature(model)

    def initial(self):
        pass

    def dynamic(self):
        pass

    def write_aquacrop_input(self):
        pass


class Precipitation:
    def __init__(self, model):
        self.model = model
        self.filename = model.config.weather.prec["filename"]
        self.nc_varname = model.config.weather.prec["varname"]
        self.is_1d = model.config.weather.prec["is_1d"]
        self.xy_dimname = model.config.weather.prec["xy_dimname"]
        self.factor = model.config.weather.prec["factor"]
        self.offset = model.config.weather.prec["offset"]

    def initial(self):
        pass

    def dynamic(self):
        pass

    def write_aquacrop_input(self):
        pass


class ET0:
    def __init__(self, model):
        self.model = model
        self.filename = model.config.weather.eto["filename"]
        self.nc_varname = model.config.weather.eto["varname"]
        self.is_1d = model.config.weather.eto["is_1d"]
        self.xy_dimname = model.config.weather.eto["xy_dimname"]
        self.factor = model.config.weather.eto["factor"]
        self.offset = model.config.weather.eto["offset"]

    def initial(self):
        self._data = xarray.open_dataset(self.filename)

    def dynamic(self):
        pass

    def write_aquacrop_input(self):
        pass
