#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from hm.api import open_hmdataarray
# from hm.input import HmInputData


class MaxTemperature:
    def __init__(self, model):
        self.model = model
        self.filename = model.config.weather.tmax["filename"]
        self.nc_varname = model.config.weather.tmax["varname"]
        self.is_1d = model.config.weather.tmax["is_1d"]
        self.xy_dimname = model.config.weather.tmax["xy_dimname"]
        self.factor = model.config.weather.tmax["factor"]
        self.offset = model.config.weather.tmax["offset"]

    def initial(self):
        self.load_data()

    def load_data(self):
        self._data = xarray.open_dataset(self.filename)[self.nc_varname]


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
