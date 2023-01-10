#!/usr/bin/env python3

import os
import tomli
import netCDF4
import xarray
import metpy
import metpy.calc as mpcalc
import numpy as np
import importlib
import click
from datetime import date
from decimal import Decimal

Prec = xarray.open_dataarray(
    os.path.join(
        "tests/testdata",
        "daily_mean_total_precipitation",
        "download_daily_mean_total_precipitation_2010_01.nc",
    )
)
# Test Domain object
mask = Prec.values[0,]
mask = ~np.isnan(mask) * 1
lat = Prec.lat.values
lon = Prec.lon.values
ds = xarray.Dataset(
    data_vars=dict(
        mask=(["lat", "lon"], mask),
    ),
    coords=dict(
        lat=(["lat"], lat),
        lon=(["lon"], lon)
    )
)

import pyaquacrop.Domain
importlib.reload(pyaquacrop.Domain)
from pyaquacrop.Domain import Domain

ds = ds.sel(lat=slice(8., 10.), lon=slice(-2., 0.))
# We can flatten the dataset as follows:
ds_1d = ds.stack(xy=[...], create_index=False)
ds_1d = ds_1d.assign_coords(xy=("xy", [i+1 for i in range(400)]))
# FIXME - always represent domain as 1D xarray?
domain = Domain(ds_1d, is_1d=True, xy_dimname="xy")

ds.to_netcdf("tests/testdata/ghana.nc")
ds_1d.to_netcdf("tests/testdata/ghana_1d.nc")

configfile = 'tests/testdata/config.toml'
import pyaquacrop.Config
importlib.reload(pyaquacrop.Config)
from pyaquacrop.Config import Configuration
config = Configuration(configfile)

# Eventually this will all be contained in AquaCrop object
import pyaquacrop.AquaCrop
importlib.reload(pyaquacrop.AquaCrop)
from pyaquacrop.AquaCrop import AquaCrop
model = AquaCrop(configfile)

import pyaquacrop.Weather
importlib.reload(pyaquacrop.Weather)
from pyaquacrop.Weather import (Temperature,
                                ET0,
                                Precipitation)

# Check weather objects are created OK
eto = ET0(model)
prec = Precipitation(model)
temp = Temperature(model)

# Write output for the first point in the study region
# Idea is that the model will loop through these automatically
eto._select_point(i=1)
eto._write_aquacrop_input("/tmp/tmp.txt")

prec._select_point(i=1)
prec._write_aquacrop_input("/tmp/tmp.txt")

temp._select_point(i=1)
temp._write_aquacrop_input("/tmp/tmp.txt")

# Crop parameters
import pyaquacrop.CropParameters
importlib.reload(pyaquacrop.CropParameters)
importlib.reload(pyaquacrop.Parameter)
importlib.reload(pyaquacrop.crop_parameter_dict)
importlib.reload(pyaquacrop.constants)
importlib.reload(pyaquacrop)
from pyaquacrop.CropParameters import CropParameterSet

crop_params = CropParameterSet("Wheat")
crop_params._write_aquacrop_input("/tmp/tmp.txt")

# Field management parameters
import pyaquacrop.Management
importlib.reload(pyaquacrop.Management)
from pyaquacrop.Management import ManagementParameterSet

mgmt_params = ManagementParameterSet()

# Irrigation parameters
# Groundwater
# Etc.









# NOT USED:
#
#
# T_min = xarray.open_dataarray(
#     os.path.join(
#         "tests/testdata",
#         "daily_minimum_2m_temperature",
#         "download_daily_minimum_2m_temperature_2010_01.nc",
#     )
# )

# T_max = xarray.open_dataarray(
#     os.path.join(
#         "tests/testdata",
#         "daily_maximum_2m_temperature",
#         "download_daily_maximum_2m_temperature_2010_01.nc",
#     )
# )
# T_dew = xarray.open_dataarray(
#     os.path.join(
#         "tests/testdata",
#         "daily_mean_2m_dewpoint_temperature",
#         "download_daily_mean_2m_dewpoint_temperature_2010_01.nc",
#     )
# )
# u_10 = xarray.open_dataarray(
#     os.path.join(
#         "tests/testdata",
#         "daily_mean_10m_u_component_of_wind",
#         "download_daily_mean_10m_u_component_of_wind_2010_01.nc",
#     )
# )
# v_10 = xarray.open_dataarray(
#     os.path.join(
#         "tests/testdata",
#         "daily_mean_10m_v_component_of_wind",
#         "download_daily_mean_10m_v_component_of_wind_2010_01.nc",
#     )
# )
# P = xarray.open_dataarray(
#     os.path.join(
#         "tests/testdata",
#         "daily_mean_surface_pressure",
#         "download_daily_mean_surface_pressure_2010_01.nc",
#     )
# )
# R_s = xarray.open_dataarray(
#     os.path.join(
#         "tests/testdata",
#         "daily_mean_surface_solar_radiation_downwards",
#         "download_daily_mean_surface_solar_radiation_downwards_2010_01.nc",
#     )
# )

# # Unit conversions
# Prec = Prec.metpy.convert_units("mm").metpy.dequantify()
# # Multiply P by 24 to convert average hourly depth to daily depth
# Prec *= 24
# T_min = T_min.metpy.convert_units("degC").metpy.dequantify()
# T_max = T_max.metpy.convert_units("degC").metpy.dequantify()
# T_dew = T_dew.metpy.convert_units("degC").metpy.dequantify()
# R_s = R_s.metpy.convert_units("MJ m**-2").metpy.dequantify()
# # Multiply R_s by 24 to convert average hourly MJ m-2 to total daily MJ m-2
# R_s *= 24

# def _fao56_eq8(P):
#     return 0.665 * 10 ** -3 * P


# def _fao56_eq9(T_min, T_max):
#     T_mean = (T_min + T_max) / 2.0
#     return T_mean


# def _fao56_eq11(T):
#     return 0.6108 * np.exp(17.27 * T / (T + 237.3))


# def _fao56_eq12(T_min, T_max):
#     e_s_min = _fao56_eq11(T_min)
#     e_s_max = _fao56_eq11(T_max)
#     e_s = (e_s_min + e_s_max) / 2.0
#     return e_s


# def _fao56_eq13(t2m):
#     return 4098.0 * _fao56_eq11(t2m) / ((t2m + 237.3) ** 2)


# def _fao56_eq21(Day, Latitude):
#     phi = Latitude * np.pi / 180
#     delta = 0.409 * np.sin(2 * np.pi * Day / 365 - 1.39)
#     d_r = 1 + 0.033 * np.cos(2 * np.pi * Day / 365)
#     w_s = np.arccos(-np.tan(phi) * np.tan(delta))
#     R_a = (
#         24
#         * 60
#         / np.pi
#         * 0.082
#         * d_r
#         * (
#             w_s * np.sin(phi) * np.sin(delta)
#             + np.cos(phi) * np.cos(delta) * np.sin(w_s)
#         )
#     )
#     return R_a


# def _fao56_eq37(R_a, z_msl):
#     R_so = (0.75 + 2 * 10 ** (-5) * z_msl) * R_a
#     return R_so


# def _fao56_eq38(R_s, albedo=0.23):
#     R_ns = (1 - albedo) * R_s
#     return R_ns


# SB = 4.903 * 10 ** (-9)


# def _fao56_eq39(T_min, T_max, e_a, R_s, R_so):
#     R_nl = (
#         SB
#         * (((T_max + 273.16) ** 4 + (T_min + 273.16) ** 4) / 2)
#         * (0.34 - 0.14 * e_a ** 0.5)
#         * ((1.35 * R_s / R_so) - 0.35)
#     )
#     return R_nl


# def _fao56_eq42():
#     return 0.0


# def _fao56_eq47(u_z, z_u):
#     return u_z * (4.87 / (np.log(67.8 * z_u - 5.42)))


# def _fao56_eq6(Delta, R_n, G, gamma, T_mean, u_2, e_s, e_a):
#     # Penman Monteith equation
#     ETo = (0.408 * Delta * (R_n - G)) + (
#         gamma * (900 / (T_mean + 273.0)) * u_2 * (e_s - e_a)
#     ) / (Delta + gamma * (1 + 0.34 * u_2))
#     ETo = ETo.clip(min=0.0)
#     return ETo


# # Psychrometric constant [kPa degC**-1]
# gamma = _fao56_eq8(P)

# # Mean 2m temperature
# T_mean = _fao56_eq9(T_min, T_max)

# # Vapor pressure
# e_s = _fao56_eq12(T_min, T_max)
# e_a = _fao56_eq11(T_dew)

# # Slope of vapor pressure curve [kPa degC**-1]
# Delta = _fao56_eq13(T_mean)

# # FOR TESTING:
# z_msl = 50.

# # Radiation components
# Day = T_min["time.dayofyear"]
# Latitude = T_min["lat"]
# R_a = _fao56_eq21(Day, Latitude)
# R_so = _fao56_eq37(R_a, z_msl)
# R_ns = _fao56_eq38(R_s)
# R_nl = _fao56_eq39(T_min, T_max, e_a, R_s, R_so)
# R_n = R_ns - R_nl

# # Wind components
# u_10 = mpcalc.wind_speed(u_10, v_10).metpy.dequantify()
# u_2 = _fao56_eq47(u_10, z_u=10)

# # Soil heat flux [MJ m**-2 d**-1] (assume negligible at daily timescale)
# G = _fao56_eq42()

# # Penman Monteith equation
# ETo = _fao56_eq6(Delta, R_n, G, gamma, T_mean, u_2, e_s, e_a)
