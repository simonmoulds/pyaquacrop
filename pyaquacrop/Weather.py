#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from hm.api import open_hmdataarray
# from hm.input import HmInputData


class MaxTemperature:
    def __init__(self, model):
        self.model = model
        self.filename = model.config.TMAX["filename"]
        self.nc_varname = model.config.TMAX["varname"]
        self.is_1d = model.config.TMAX["is_1d"]
        self.xy_dimname = model.config.TMAX["xy_dimname"]
        self.factor = model.config.TMAX["factor"]
        self.offset = model.config.TMAX["offset"]
        # self.model_varname = 'tmax'
        # self.dataset_varname = 'tmax_dataset'


class MinTemperature:
    def __init__(self, model):
        self.model = model
        self.filename = model.config.TMIN["filename"]
        self.nc_varname = model.config.TMIN["varname"]
        self.is_1d = model.config.TMIN["is_1d"]
        self.xy_dimname = model.config.TMIN["xy_dimname"]
        self.factor = model.config.TMIN["factor"]
        self.offset = model.config.TMIN["offset"]
        # self.model_varname = 'tmin'
        # self.dataset_varname = 'tmin_dataset'


class Temperature:
    def __init__(self, model):
        self.tmin = MinTemperature(model)
        self.tmax = MaxTemperature(model)

    def write_aquacrop_input(self):
        pass


class Precipitation:
    def __init__(self, model):
        self.model = model
        self.filename = model.config.PRECIPITATION["filename"]
        self.nc_varname = model.config.PRECIPITATION["varname"]
        self.is_1d = model.config.PRECIPITATION["is_1d"]
        self.xy_dimname = model.config.PRECIPITATION["xy_dimname"]
        self.factor = model.config.PRECIPITATION["factor"]
        self.offset = model.config.PRECIPITATION["offset"]
        # self.model_varname = 'prec'
        # self.dataset_varname = 'prec_dataset'

    def write_aquacrop_input(self):
        pass


class ETref:
    def __init__(self, model):
        self.model = model
        self.filename = model.config.ETREF["filename"]
        self.nc_varname = model.config.ETREF["varname"]
        self.is_1d = model.config.ETREF["is_1d"]
        self.xy_dimname = model.config.ETREF["xy_dimname"]
        self.factor = model.config.ETREF["factor"]
        self.offset = model.config.ETREF["offset"]
        # self.model_varname = 'etref'
        # self.dataset_varname = 'etref_dataset'

    def write_aquacrop_input(self):
        pass


# class Weather(object):
#     def __init__(self, model):
#         self.model = model
#         self.max_temperature_module = MaxTemperature(model)
#         self.min_temperature_module = MinTemperature(model)
#         self.prec_module = Precipitation(model)
#         self.etref_module = ETref(model)

#     def initial(self):
#         self.max_temperature_module.initial()
#         self.min_temperature_module.initial()
#         self.prec_module.initial()
#         self.etref_module.initial()

#         # # Why are these necessary:
#         # self.model.Tmax = self.model.tmax.values
#         # self.model.Tmin = self.model.tmin.values
#         # self.model.P = self.model.prec.values
#         # self.model.ETref = self.model.etref.values

#     def dynamic(self):
#         self.max_temperature_module.dynamic()
#         self.min_temperature_module.dynamic()
#         self.prec_module.dynamic()
#         self.etref_module.dynamic()
