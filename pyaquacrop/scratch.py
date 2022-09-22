#!/usr/bin/env python3

import os
import toml
import requests
import netCDF4
import xarray
import click
from datetime import date
from decimal import Decimal

# TESTING
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

# # FOR TESTING:
# z_msl = 50.

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

# How to get elevation data?
# - Have a 0.1 degree product as part of the package [GMTED2010]
# - Optionally allow the user to supply a list of points +
#   elevation values [this would be ideal in the case of TAHMO

# Write AquaCrop input

LINESEP = os.linesep

# Meteo input: Prec, T_min, T_max, ETref


def _climate_data_header(start_date: pd.Timestamp) -> str:
    day, month, year = start_date.day, start_date.month, start_date.year
    header = (
        "This is a test - put something more meaningful here"
        + LINESEP
        + str(1).rjust(5)
        + "  : Daily records"
        + LINESEP
        + str(day).rjust(5)
        + "  : First day of record"
        + LINESEP
        + str(month).rjust(5)
        + "  : First month of record"
        + LINESEP
        + str(year).rjust(5)
        + "  : First year of record"
        + LINESEP
        + LINESEP
    )
    return header


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


# class Rainfall:
def _write_rainfall_input_file(
    x: xarray.DataArray, latitude: float, longitude: float
) -> None:
    header = _climate_data_header(x.time.values[0])
    header = header + "  Total Rain (mm)" + LINESEP + "======================="
    X = x.sel(lat=latitude, lon=longitude, method="nearest")
    with open(os.path.join(sub_dir, filename), "w") as f:
        np.savetxt(f, X, fmt="%.2f", newline=LINESEP, header=header, comments="")
    return None


# class SoilProfile:
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


def _write_crop_calendar_input_file(
    generate_onset: bool,
    generate_temp_onset: str,
    start_search_period_day_nr: int,
    length_search_period: int,
    criterion_nr: int,
):

    # TODO the file contains more information, but it doesn't
    # look as if any parameters beyond those listed are actually
    # read from the file [L3253 global.f90]

    # TODO find out default values for the above values

    # It seems from the Fortran code that this is simply used as a flag: if exceeding 10 then GetOnsetTemp = .true. [L3289]
    if generate_onset & generate_temp_onset:
        if ~criterion_nr in [12, 13]:
            raise ValueError()
    # criterion_nr == 12: TMeanPeriod
    # criterion_nr == 13: GDDPeriod

    # This file is read by LoadCropCalendar() in global.f90 L3253
    # I think some of the parameters are actually specified in CRO file
    # GenerateOn
    # GenerateTempOn
    # Criterion [NB undocumented]
    # StartSearchDayNr
    # StopSearchDayNr
    # LengthSearchPeriod
    crop_calendar = (
        file_description
        + LINESEP
        + "{:12.1f}".format(7)
        + "  : AquaCrop Version"
        + LINESEP
        + "{:10d}".format(int(generate_onset))
        + "    : TODO"
        + LINESEP
        + "{:10d}".format(int(time_window_start))
        + "    : TODO"
        + LINESEP
        + "{:10d}".format(int(time_window_length))
        + "    : TODO"
        + LINESEP
    )
    return None


sub_dir = "INPUT"
try:
    os.makedirs(sub_dir)
except FileExistsError:
    pass

filename = "Prec.PLU"
latitude = 8.25
longitude = 0.25
_write_rainfall_input_file(Prec, latitude, longitude)

# Soil input

# TESTING
dz = [4.0]  # m
th_sat = [41.0]  # %
th_fc = [22.0]  # %
th_wp = [10.0]  # %
k_sat = [1200.0]  # mm/day
penetrability = [100.0]  # %
gravel = [0.0]  # %
CRa = [-0.3232]  # ???
CRb = [0.219363]  # ???
description = ["sandy loam"]  # ???

# Crop calendar input
