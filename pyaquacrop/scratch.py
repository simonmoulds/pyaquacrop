#!/usr/bin/env python3

import os
import tomli
import requests
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
        "..",
        "daily_mean_total_precipitation",
        "download_daily_mean_total_precipitation_2010_01.nc",
    )
)
T_min = xarray.open_dataarray(
    os.path.join(
        "..",
        "daily_minimum_2m_temperature",
        "download_daily_minimum_2m_temperature_2010_01.nc",
    )
)

T_max = xarray.open_dataarray(
    os.path.join(
        "..",
        "daily_maximum_2m_temperature",
        "download_daily_maximum_2m_temperature_2010_01.nc",
    )
)
T_dew = xarray.open_dataarray(
    os.path.join(
        "..",
        "daily_mean_2m_dewpoint_temperature",
        "download_daily_mean_2m_dewpoint_temperature_2010_01.nc",
    )
)
u_10 = xarray.open_dataarray(
    os.path.join(
        "..",
        "daily_mean_10m_u_component_of_wind",
        "download_daily_mean_10m_u_component_of_wind_2010_01.nc",
    )
)
v_10 = xarray.open_dataarray(
    os.path.join(
        "..",
        "daily_mean_10m_v_component_of_wind",
        "download_daily_mean_10m_v_component_of_wind_2010_01.nc",
    )
)
P = xarray.open_dataarray(
    os.path.join(
        "..",
        "daily_mean_surface_pressure",
        "download_daily_mean_surface_pressure_2010_01.nc",
    )
)
R_s = xarray.open_dataarray(
    os.path.join(
        "..",
        "daily_mean_surface_solar_radiation_downwards",
        "download_daily_mean_surface_solar_radiation_downwards_2010_01.nc",
    )
)

# Unit conversions
Prec = Prec.metpy.convert_units("mm").metpy.dequantify()
# Multiply P by 24 to convert average hourly depth to daily depth
Prec *= 24
T_min = T_min.metpy.convert_units("degC").metpy.dequantify()
T_max = T_max.metpy.convert_units("degC").metpy.dequantify()
T_dew = T_dew.metpy.convert_units("degC").metpy.dequantify()
R_s = R_s.metpy.convert_units("MJ m**-2").metpy.dequantify()
# Multiply R_s by 24 to convert average hourly MJ m-2 to total daily MJ m-2
R_s *= 24

def _fao56_eq8(P):
    return 0.665 * 10 ** -3 * P


def _fao56_eq9(T_min, T_max):
    T_mean = (T_min + T_max) / 2.0
    return T_mean


def _fao56_eq11(T):
    return 0.6108 * np.exp(17.27 * T / (T + 237.3))


def _fao56_eq12(T_min, T_max):
    e_s_min = _fao56_eq11(T_min)
    e_s_max = _fao56_eq11(T_max)
    e_s = (e_s_min + e_s_max) / 2.0
    return e_s


def _fao56_eq13(t2m):
    return 4098.0 * _fao56_eq11(t2m) / ((t2m + 237.3) ** 2)


def _fao56_eq21(Day, Latitude):
    phi = Latitude * np.pi / 180
    delta = 0.409 * np.sin(2 * np.pi * Day / 365 - 1.39)
    d_r = 1 + 0.033 * np.cos(2 * np.pi * Day / 365)
    w_s = np.arccos(-np.tan(phi) * np.tan(delta))
    R_a = (
        24
        * 60
        / np.pi
        * 0.082
        * d_r
        * (
            w_s * np.sin(phi) * np.sin(delta)
            + np.cos(phi) * np.cos(delta) * np.sin(w_s)
        )
    )
    return R_a


def _fao56_eq37(R_a, z_msl):
    R_so = (0.75 + 2 * 10 ** (-5) * z_msl) * R_a
    return R_so


def _fao56_eq38(R_s, albedo=0.23):
    R_ns = (1 - albedo) * R_s
    return R_ns


SB = 4.903 * 10 ** (-9)


def _fao56_eq39(T_min, T_max, e_a, R_s, R_so):
    R_nl = (
        SB
        * (((T_max + 273.16) ** 4 + (T_min + 273.16) ** 4) / 2)
        * (0.34 - 0.14 * e_a ** 0.5)
        * ((1.35 * R_s / R_so) - 0.35)
    )
    return R_nl


def _fao56_eq42():
    return 0.0


def _fao56_eq47(u_z, z_u):
    return u_z * (4.87 / (np.log(67.8 * z_u - 5.42)))


def _fao56_eq6(Delta, R_n, G, gamma, T_mean, u_2, e_s, e_a):
    # Penman Monteith equation
    ETo = (0.408 * Delta * (R_n - G)) + (
        gamma * (900 / (T_mean + 273.0)) * u_2 * (e_s - e_a)
    ) / (Delta + gamma * (1 + 0.34 * u_2))
    ETo = ETo.clip(min=0.0)
    return ETo


# Psychrometric constant [kPa degC**-1]
gamma = _fao56_eq8(P)

# Mean 2m temperature
T_mean = _fao56_eq9(T_min, T_max)

# Vapor pressure
e_s = _fao56_eq12(T_min, T_max)
e_a = _fao56_eq11(T_dew)

# Slope of vapor pressure curve [kPa degC**-1]
Delta = _fao56_eq13(T_mean)

# FOR TESTING:
z_msl = 50.

# Radiation components
Day = T_min["time.dayofyear"]
Latitude = T_min["lat"]
R_a = _fao56_eq21(Day, Latitude)
R_so = _fao56_eq37(R_a, z_msl)
R_ns = _fao56_eq38(R_s)
R_nl = _fao56_eq39(T_min, T_max, e_a, R_s, R_so)
R_n = R_ns - R_nl

# Wind components
u_10 = mpcalc.wind_speed(u_10, v_10).metpy.dequantify()
u_2 = _fao56_eq47(u_10, z_u=10)

# Soil heat flux [MJ m**-2 d**-1] (assume negligible at daily timescale)
G = _fao56_eq42()

# Penman Monteith equation
ETo = _fao56_eq6(Delta, R_n, G, gamma, T_mean, u_2, e_s, e_a)

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

# TODO add test config, create Config class, create MaxTemperature object
configfile = 'tests/testdata/config.toml'
import pyaquacrop.Config
importlib.reload(pyaquacrop.Config)
from pyaquacrop.Config import load_config, Configuration
config = Configuration(configfile)

modelgrid = os.path.join(config['configpath'], config['MODEL_GRID']['filename'])
ds = xarray.open_dataset(modelgrid)
domain = Domain(ds)
pt = (5.15256672, -1.88154445)  # lat, lon

# # TODO create a Tmax object and try to create AquaCrop input
# import re
# fn = config.TMAX['filename']
# if ~os.path.isabs(fn):
#     fn = os.path.join(config.configpath, fn)
# path = os.path.dirname(fn)
# filename = os.path.basename(fn)
# regex = re.compile(str(filename))
# fs = [os.path.join(path, f) for f in os.listdir(path) if regex.match(f)]
# ds = xarray.open_mfdataset(fs)
# # ds.sel(lat=pt[0], lon=pt[1], method='nearest').t2m.values

import pyaquacrop.Weather
importlib.reload(pyaquacrop.Weather)
from pyaquacrop.Weather import Temperature
# tmax = MaxTemperature(config)
# tmax.initial()
# tmax.select(pt[0], pt[1])
temp = Temperature(config)
temp.initial()
temp.select(pt[0], pt[1])
temp._write_aquacrop_input("tmp.txt") # This works!

# TODO repeat for eto and precip

import pyaquacrop.AquaCrop
importlib.reload(pyaquacrop.AquaCrop)
from pyaquacrop.AquaCrop import AquaCrop

import pyaquacrop.ModelTime
importlib.reload(pyaquacrop.ModelTime)
from pyaquacrop.ModelTime import ModelTime

model = AquaCrop(configfile)
# from sklearn.neighbors import BallTree
# from math import radians
# earth_radius = 6371000 # meters in earth
# test_radius = np.inf #1300000 # meters
# test_points = [[32.027240,-81.093190],[41.981876,-87.969982]]
# test_points_rad = np.array([[radians(x[0]), radians(x[1])] for x in test_points ])
# tree = BallTree(test_points_rad, metric = 'haversine')
# ind,results = tree.query_radius(test_points_rad, r=test_radius/earth_radius,
# return_distance  = True)
# print(ind)
# print(results * earth_radius/1000)

# from math import radians, cos, sin, asin, sqrt, degrees, atan2
# X = [32.027240,-81.093190]
# Y = [41.981876,-87.969982]
# # Xrad = [radians(_) for _ in X]
# # Yrad = [radians(_) for _ in Y]
# # from sklearn.metrics.pairwise import haversine_distances
# # dist = haversine_distances([Xrad, Yrad])
# # dist *= 6371000 / 1000
# def distance_haversine(p1, p2):
#     """
#     Calculate the great circle distance between two points
#     on the earth (specified in decimal degrees)
#     Haversine
#     formula:
#         a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
#                         _   ____
#         c = 2 ⋅ atan2( √a, √(1−a) )
#         d = R ⋅ c

#     where   φ is latitude, λ is longitude, R is earth’s radius (mean radius = 6,371km);
#             note that angles need to be in radians to pass to trig functions!
#     """
#     lat1, lon1 = p1
#     lat2, lon2 = p2
#     # for p in [p1, p2]:
#     #     validate_point(p)

#     R = 6371 # km - earths's radius

#     # convert decimal degrees to radians
#     lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

#     # haversine formula
#     dlon = lon2 - lon1
#     dlat = lat2 - lat1

#     a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
#     c = 2 * asin(sqrt(a)) # 2 * atan2(sqrt(a), sqrt(1-a))
#     d = R * c
#     return d

# dist = distance_haversine(X, Y)

# idx = pd.MultiIndex.from_arrays(arrays=[lons, lats], names=["lon", "lat"])
# s = pd.Series(data=data, index=idx)
# da = xarray.DataArray.from_series()



# ds_1d = ds_1d.assign_coords(xy=np.array([i for i in range(len(ds_1d.lon.values))]))
# domain = Domain(ds_1d, is_1d=True, xy_dimname='xy')

# # How to get elevation data?
# # - Have a 0.1 degree product as part of the package [GMTED2010]
# # - Optionally allow the user to supply a list of points +
# #   elevation values [this would be ideal in the case of TAHMO

# # Write AquaCrop input

# # Meteo input: Prec, T_min, T_max, ETref

# def _climate_data_header(start_date: pd.Timestamp) -> str:
#     day, month, year = start_date.day, start_date.month, start_date.year
#     header = (
#         "This is a test - put something more meaningful here"
#         + os.linesep
#         + str(1).rjust(5)
#         + "  : Daily records"
#         + os.linesep
#         + str(day).rjust(5)
#         + "  : First day of record"
#         + os.linesep
#         + str(month).rjust(5)
#         + "  : First month of record"
#         + os.linesep
#         + str(year).rjust(5)
#         + "  : First year of record"
#         + os.linesep
#         + os.linesep
#     )
#     return header


# # class Rainfall:
# def _write_rainfall_input_file(
#     x: xarray.DataArray, latitude: float, longitude: float
# ) -> None:
#     header = _climate_data_header(x.time.values[0])
#     header = header + "  Total Rain (mm)" + LINESEP + "======================="
#     X = x.sel(lat=latitude, lon=longitude, method="nearest")
#     with open(os.path.join(sub_dir, filename), "w") as f:
#         np.savetxt(f, X, fmt="%.2f", newline=LINESEP, header=header, comments="")
#     return None


# sub_dir = "INPUT"
# try:
#     os.makedirs(sub_dir)
# except FileExistsError:
#     pass

# filename = "Prec.PLU"
# latitude = 8.25
# longitude = 0.25
# _write_rainfall_input_file(Prec, latitude, longitude)
