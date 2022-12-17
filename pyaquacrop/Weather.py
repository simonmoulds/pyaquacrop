#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import xarray


class SpaceTimeDataArray:
    def __init__(self,
                 dataarray,
                 is_1d=False,
                 xy_dimname=None):

        self._data = dataarray
        self.is_1d = is_1d
        self.xy_dimname = xy_dimname

    def initial(self):
        pass

    def select(self, lat, lon):
        self._data_subset = self._data.sel(lat=lat, lon=lon, method='nearest')

    @property
    def values(self):
        return self._data_subset.values


# Function to create SpaceTimeDataArray from file
def open_stdataarray(filename, varname, is_1d, xy_dimname, factor=1., offset=0.):
    if isinstance(filename, str):
        filename = [filename]

    ds = xarray.open_mfdataset(filename)
    da = ds[varname]
    da = (da * factor) + offset
    return SpaceTimeDataArray(da, is_1d, xy_dimname)


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


# class _Precipitation(SpaceTimeDataArray)
# class _MaxTemperature(SpaceTimeDataArray):
# class _MinTemperature(SpaceTimeDataArray):
# class _DewTemperature(SpaceTimeDataArray):
# class _WindSpeed(SpaceTimeDataArray):
# class _U_WindSpeed(SpaceTimeDataArray):
# class _SolarRadiation(SpaceTimeDataArray):
# class _LongwaveRadiation(SpaceTimeDataArray):
# class _MaxRelativeHumudity(SpaceTimeDataArray):
# class _MinRelativeHumidity(SpaceTimeDataArray):
# class _MeanRelativeHumidity(SpaceTimeDataArray):
# class _SpecificHumidity(SpaceTimeDataArray):
# class _SurfacePressure(SpaceTimeDataArray):

class Precipitation(SpaceTimeDataArray):

    def _write_aquacrop_input(self, filename):
        header = _climate_data_header(pd.Timestamp(self.prec._data_subset.time.values[0]))
        header += "  Total Rain (mm)" + os.linesep
        header += "======================="
        with open(filename, "w") as f:
            np.savetxt(
                f, self.values, fmt="%.2f", delimiter="\t",
                newline=os.linesep, header=header, comments=""
            )
        return None


def _open_weather_dataarray(config, config_section):

    # Retrieve values from config
    filename = vars(config)[config_section].filename,
    varname = vars(config)[config_section].varname,
    is_1d = vars(config)[config_section].is_1d,
    xy_dimname = vars(config)[config_section].xy_dimname,
    factor = vars(config)[config_section].factor,
    offset = vars(config)[config_section].offset

    # Open dataset then select dataarray
    if isinstance(filename, str):
        filename = [filename]
    ds = xarray.open_mfdataset(filename)
    da = ds[varname]

    # Apply factor/offset
    da = (da * factor) + offset
    return da


def _open_spatial_dataarray(config, config_section):
    return _open_weather_dataarray(config, config_section)


# def _open_precipitation_stdataarray(config):
#     da = open_weather_dataarray(config, 'PREC')
#     return Precipitation(da, is_1d, xy_dimname)


def _open_weather_stdataarray(config, config_section):
    da = _open_weather_dataarray(config, config_section)
    return SpaceTimeDataArray(
        da,
        vars(config)[config_section].is_1d,
        vars(config)[config_section].xy_dimname
    )


class Temperature:
    def __init__(self, config):
        self.tmin = _open_weather_stdataarray(config, 'TMIN')
        self.tmax = _open_weather_stdataarray(config, 'TMAX')

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


# class ET0_FromFile:
#     def __init__(self, config):
#         self.eto = _open_weather_stdataarray(config, 'ET0')


class _ET0_InputData:
    def __init__(self, model):
        self.model = model      # This means we can access other variables
        # User-supplied:
        self.tmin = None
        self.tmax = None
        self.shortwave_radiation = None
        self.max_relative_humidity = None
        self.min_relative_humidity = None
        self.mean_relative_humidity = None
        self.surface_pressure = None
        # Computed:
        self.extraterrestrial_radiation = None
        self.saturated_vapour_pressure = None
        self.actual_vapour_pressure = None
        self.net_radiation = None

    def _load_tmin(self):
        self.tmin = _open_weather_dataarray(self.config, 'TMIN')

    def _load_tmax(self):
        self.tmax = _open_weather_dataarray(self.config, 'TMAX')

    def _load_shortwave_radiation(self):
        if self.model.config.has_solar_radiation:
            self.shortwave_radiation = _open_weather_dataarray(self.model.config, 'SWDOWN')

    def _load_max_relative_humidity(self):
        if self.model.config.has_max_relative_humidity:
            self.max_relative_humidity = _open_weather_dataarray(
                self.model.config, 'RHMAX'
            )

    def _load_min_relative_humidity(self):
        if self.model.config.has_min_relative_humidity:
            self.min_relative_humidity = _open_weather_dataarray(
                self.model.config, 'RHMIN'
            )

    def _load_min_relative_humidity(self):
        if self.model.config.has_mean_relative_humidity:
            self.mean_relative_humidity = _open_weather_dataarray(
                self.model.config, 'RHMEAN'
            )

    def _load_wind_speed(self):
        if self.model.config.has_wind:
            if self.model.config.use_wind_components:
                wind_u = _open_weather_dataarray(self.model.config, 'WIND_U')
                wind_v = _open_weather_dataarray(self.model.config, 'WIND_V')
                self.wind = np.sqrt(wind_u ** 2 + wind_v ** 2)
            else:
                self.wind = _open_weather_dataarray(self.model.config, 'WIND')

    def _load_surface_pressure(self):
        if self.model.config.has_surface_pressure:
            self.surface_pressure = _open_weather_dataarray(
                self.model.config, 'PRES'
            )

        elif self.model.config.has_elevation:
            elevation = _open_spatial_dataarray(
                self.model.config, 'ELEV'
            )
            self.surface_pressure = (
                101.3 * ((293. - 0.0065 * elevation) / 293) ** 5.26
            )

    def _compute_penman_monteith_inputs(self):
        self._compute_mean_temperature()
        self._compute_saturated_vapour_pressure()
        self._compute_actual_vapour_pressure()
        self._compute_vapour_pressure_deficit()
        self._compute_extraterrestrial_radiation()
        self._compute_net_radiation()

    def _compute_mean_temperature(self):
        self.tmean = (self.tmin + self.tmax) / 2

    def _compute_extraterrestrial_radiation(self):
        """Compute extraterrestrial radiation (MJ m-2 d-1)"""
        latitude = self.model.domain.latitude
        if model.domain.is_2d:
            # Broadcast to 2D
            latitude = (
                latitude[:, None] *
                np.ones(self.model.domain.nx)  # lat, lon
            )

        days = self.model.time.days
        LatRad = latitude * np.pi / 180.0
        declin = 0.4093 * (
            np.sin(((2.0 * np.pi * days) / 365.) - 1.405)
        )

        # Broadcast so that arccosInput has dims (time, space)
        arccosInput = (-(np.tan(LatRad[None, ...])) * (np.tan(declin[..., None])))
        arccosInput = np.clip(arccosInput, -1, 1)
        sunangle = np.arccos(arccosInput)
        distsun = 1 + 0.033 * (np.cos((2 * np.pi * days) / 365.0))
        extraterrestrial_radiation = (
            ((24 * 60 * 0.082) / np.pi)
            * distsun[..., None]
            * (sunangle
               * (np.sin(LatRad[None, ...]))
               * (np.sin(declin[..., None]))
               + (np.cos(LatRad[None, ...]))
               * (np.cos(declin)[..., None])
               * (np.sin(sunangle)))
        )

        # Now create DataArray
        space_coords = {
            key: (self.model.domain._data.coords[key].dims, model.domain._data.coords[key].values)
            for key in self.model.domain._data.coords
        }
        time_coords = {'time': self.model.time.values}
        coords = {**time_coords, **space_coords}
        dims = ['time'] + [dim for dim in self.model.domain._data.dims]
        self.extraterrestrial_radiation = xarray.Dataset(
            data_vars=dict(
                extraterrestrial_radiation=(dims, extraterrestrial_radiation)
            ),
            coords=coords
        )

    def _compute_vapour_pressure_deficit(self):
        # self._compute_saturated_vapour_pressure()
        # self._compute_actual_vapour_pressure()
        vpd = self.saturated_vapour_pressure - self.actual_vapour_pressure
        vpd = vpd.clip(0, None)
        self.vapour_pressure_deficit = vpd

    def _compute_saturated_vapour_pressure(self):
        es_min = self._fao_equation_11(self.tmin)
        es_max = self._fao_equation_11(self.tmax)
        self.saturated_vapour_pressure = (es_min + es_max) / 2.

    def _compute_actual_vapour_pressure(self):
        if self.can_use_fao_equation_14():
            self.compute_actual_vapour_pressure_from_dewpoint_temperature()
        if self.can_use_fao_equation_17():
            self.compute_actual_vapour_pressure_from_min_max_relative_humidity()
        elif self.can_use_fao_equation_18():
            self.compute_actual_vapour_pressure_from_max_relative_humidity()
        elif self.can_use_fao_equation_19():
            self.compute_actual_vapour_pressure_from_mean_relative_humidity()
        elif self.model.config.has_specific_humidity:
            self.compute_actual_vapour_pressure_from_specific_humidity()

    def _compute_net_radiation(self):
        # requirements:
        # -------------
        # extraterrestrial_radiation
        # shortwave_radiation
        # tmin, tmax
        # actual_vapour_pressure
        #
        # TODO check units
        alpha = 0.23  # albedo, 0.23 [-]
        sigma = 4.903e-9  # stephan boltzmann [W m-2 K-4]

        # Clear sky solar radiation [MJ d-1]
        R_so = np.maximum(
            0.1,
            ((0.75 + (2 * 0.00005)) * self.extraterrestrial_radiation)
        )
        R_ns = (1 - alpha) * self.shortwave_radiation
        R_nl = (
            - sigma
            * ((self.tmax ** 4 + self.tmin ** 4) / 2)
            * (0.34 - 0.14 * np.sqrt(np.maximum(0, (self.actual_vapour_pressure / 1000))))
            * (1.35 * np.minimum(1, (self.shortwave_radiation / R_so)) - 0.35)
        )
        R_n = np.maximum(0, R_ns + R_nl)
        self.net_radiation = R_n

    def _fao_equation_11(T):
        return (
            610.8 *
            np.exp((17.27 * (T - 273.15)) / ((T - 273.15) + 237.3))
        )

    def compute_actual_vapour_pressure_from_dewpoint_temperature(self):
        self.actual_vapour_pressure = self._fao_equation_11(self.tdew)

    def compute_actual_vapour_pressure_from_min_max_relative_humidity(self):
        es_min = self._fao_equation_11(self.tmin)
        es_max = self._fao_equation_11(self.tmax)
        self.actual_vapour_pressure = (
            (es_min * self.max_relative_humidity.values / 100.)
            + (es_max * self.min_relative_humidity.values / 100.)
        ) / 2

    def compute_actual_vapour_pressure_from_max_relative_humidity(self):
        es_min = self._fao_equation_11(self.tmin)
        self.actual_vapour_pressure = (
            self.es_min
            * self.max_relative_humidity.values / 100.
        )

    def compute_actual_vapour_pressure_from_mean_relative_humidity(self):
        self.actual_vapour_pressure = (
            self.saturated_vapour_pressure * self.mean_relative_humidity.values / 100.
        )

    # def compute_actual_vapour_pressure_from_specific_humidity(self):
    #     """Compute actual vapour pressure given specific
    #     humidity, using equations from Bolton (1980);
    #     """
    #     def ea(Pres, Q, eps):
    #         return (Q * Pres) / ((1 - eps) * Q + eps)

    #     eps = 0.622  # ratio of water vapour/dry air molecular weights [-]
    #     self.actual_vapour_pressure = ea(
    #         self.surface_pressure,
    #         self.specific_humidity,
    #         eps
    #     )

    def can_use_fao_equation_14(self):
        return self.model.config.has_dewpoint_temperature

    def can_use_fao_equation_17(self):
        return (
            self.model.config.has_min_daily_temperature
            and self.model.config.has_max_daily_temperature
            and self.model.config.has_min_relative_humidity
            and self.model.config.has_max_relative_humidity
        )

    def can_use_fao_equation_18(self):
        return (
            self.model.config.has_min_daily_temperature
            and self.model.config.has_max_relative_humidity
        )

    def can_use_fao_equation_19(self):
        return (
            self.model.config.has_max_daily_temperature
            and self.model.config.has_min_daily_temperature
            and self.model.config.has_mean_relative_humidity
        )


class _ET0_PenmanMonteith:
    def __init__(self, config, domain):
        self.data = _ET0_InputData(config, domain)
        self.data._compute_penman_monteith_inputs()

    def check_minimum_data_requirements(self, config):
        return True

    def penman_monteith(self):
        """Function implementing the Penman-Monteith
        equation (*NOT* FAO version) - TODO make FAO version

        Data requirements:
        * Tmean
        * vapour pressure deficit
        * surface pressure
        * net radiation
        """
        cp = 0.001013               # specific heat of air 1013 [MJ kg-1 K-1]
        TimeStepSecs = 86400        # timestep in seconds
        rs = 70                     # surface resistance, 70 [s m-1]
        R = 287.058                 # Universal gas constant [J kg-1 K-1]
        # ratio of water vapour/dry air molecular weights [-]
        eps = 0.622

        # Density of air [kg m-3]
        rho = self.data.surface_pressure * (self.data.tmean * R)

        # Latent heat [MJ kg-1]
        latent_heat = (2.501 - (0.002361 * (self.data.tmean - 273.15)))

        # Slope of vapour pressure [kPa K-1]
        deltop = 4098. * \
            (0.6108 * np.exp((17.27 * (self.data.tmean - 273.15)) /
                             ((self.data.tmean - 273.15) + 237.3)))
        delbase = ((self.data.tmean - 273.15) + 237.3) ** 2
        delta = deltop / delbase

        # Psychrometric constant [kPa K-1]
        gamma = (
            cp * (self.data.surface_pressure / 1000) /
            (eps * latent_heat)
        )

        # Aerodynamic resistance [m s-1]
        z = 10  # height of wind speed variable (10 meters above surface)
        Wsp_2 = self.data.wind * 4.87 / (np.log(67.8 * z - 5.42))
        ra = np.divide(208., Wsp_2, out=np.zeros_like(Wsp_2), where=Wsp_2 != 0)

        # Penman-Monteith equation (NB unit conversion)
        PETtop = np.maximum(
            ((delta * 1e3)
             * self.data.net_radiation
             + rho
             * (cp * 1e6)
             * np.divide(
                 self.data.vapour_pressure_deficit,
                 ra,
                 out=np.zeros_like(ra),
                 where=ra != 0)),
            1)

        PETbase = np.maximum(
            ((delta * 1e3)
             + (gamma * 1e3)
             * (1 + np.divide(rs, ra, out=np.zeros_like(ra), where=ra != 0))),
            1)
        PET = np.maximum(PETtop / PETbase, 0)

        PETmm = np.maximum((PET / (latent_heat * 1e6) * TimeStepSecs), 0)
        # self.ETref = PETmm.copy()

    def initial(self):
        pass

    def select(self):
        pass

    @property
    def values(self):
        pass


class _ET0_FromFile:
    def __init__(self, config):
        pass


class ET0(SpaceTimeDataArray):

    VALID_METHODS = ['hargreaves', 'penman_monteith', 'priestley_taylor']
    def __init__(self, config):
        preprocess = bool(config['ET0']['preprocess'])
        if preprocess:
            method = str(config['ET0']['method']).lower()
            if method == "hargreaves":
                eto_obj = _ET0_Hargreaves(config)
            elif method == "penman_monteith":
                eto_obj = _ET0_PenmanMonteith(config)
            elif method == "priestley_taylor":
                eto_obj = _ET0_PriestleyTaylor(config)
            else:
                raise ValueError("Invalid `method` in config: must be one of `hargreaves`, `penman_monteith`, `priestley_taylor`")
        else:
            eto_obj = _open_weather_stdataarray(config, 'ET0')

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


# class _ET0_Hargreaves:
#     def __init__(self, config):
#         pass

#     def initial(self):
#         pass

#     def select(self):
#         pass

#     @property
#     def values(self):
#         pass


# class _ET0_PriestleyTaylor:
#     def __init__(self, config):
#         pass

#     def initial(self):
#         pass

#     def select(self):
#         pass

#     @property
#     def values(self):
#         pass

# class ET0_PenmanMonteith:
#     def __init__(self, config):
#         pass


# class _NetRadiation:
#     def __init__(self, model):
#         self.model = model
#         self.alpha = 0.23  # albedo, 0.23 [-]
#         self.sigma = 4.903e-9  # stephan boltzmann [W m-2 K-4]

#     def initial(self):
#         self.compute_net_radiation()

#     def compute_net_radiation(self):
#         Rso = np.maximum(
#             0.1,
#             ((0.75 + (2 * 0.00005)) * self.model.extraterrestrial_radiation)
#         )  # clear sky solar radiation MJ d-1
#         Rsin_MJ = 0.086400 * self.model.shortwave_radiation.values
#         Rlnet_MJ = (
#             - self.sigma
#             * ((self.model.tmax.values ** 4 + self.model.tmin.values ** 4) / 2)
#             * (0.34 - 0.14 * np.sqrt(np.maximum(0, (self.model.ea_mean / 1000))))
#             * (1.35 * np.minimum(1, (Rsin_MJ / Rso)) - 0.35)
#         )
#         Rlnet_Watt = Rlnet_MJ / 0.086400
#         self.model.net_radiation = np.maximum(
#             0,
#             ((1 - self.alpha) * self.model.shortwave_radiation.values + Rlnet_Watt)
#         )

#     def dynamic(self):
#         self.compute_net_radiation()


# # class _ExtraterrestrialRadiation:
# #     def __init__(self, model):
# #         self.model = model

# #     def initial(self):
# #         latitudes = self.model.domain.y
# #         if self.model.domain.is_2d:
# #             latitudes = np.broadcast_to(
# #                 self.model.domain.y[:, None],
# #                 (self.model.domain.ny, self.model.domain.nx)
# #             )

# #         self.latitudes = latitudes[self.model.domain.mask.values]
# #         self.compute_extraterrestrial_radiation()

# #     def compute_extraterrestrial_radiation(self):
# #         """Compute extraterrestrial radiation (MJ m-2 d-1)"""
# #         LatRad = self.latitudes * np.pi / 180.0
# #         declin = 0.4093 * (
# #             np.sin(((2.0 * np.pi * self.model.time.doy) / 365.) - 1.405)
# #         )
# #         arccosInput = (-(np.tan(LatRad)) * (np.tan(declin)))
# #         arccosInput = np.clip(arccosInput, -1, 1)
# #         sunangle = np.arccos(arccosInput)
# #         distsun = 1 + 0.033 * (np.cos((2 * np.pi * self.model.time.doy) / 365.0))
# #         self.extraterrestrial_radiation = (
# #             ((24 * 60 * 0.082) / np.pi)
# #             * distsun
# #             * (sunangle
# #                * (np.sin(LatRad))
# #                * (np.sin(declin))
# #                + (np.cos(LatRad))
# #                * (np.cos(declin))
# #                * (np.sin(sunangle)))
# #         )
# #         # TODO convert to xarray


# def _compute_extraterrestrial_radiation(model):
#     """Compute extraterrestrial radiation (MJ m-2 d-1)"""
#     latitude = model.domain.latitude
#     if model.domain.is_2d:
#         latitude = latitude[:, None] * np.ones(model.domain.nx)  # lat, lon

#     days = model.time.days
#     LatRad = latitude * np.pi / 180.0
#     declin = 0.4093 * (
#         np.sin(((2.0 * np.pi * days) / 365.) - 1.405)
#     )
#     # Broadcast so that arccosInput has dims (time, space)
#     arccosInput = (-(np.tan(LatRad[None, ...])) * (np.tan(declin[..., None])))
#     arccosInput = np.clip(arccosInput, -1, 1)
#     sunangle = np.arccos(arccosInput)
#     distsun = 1 + 0.033 * (np.cos((2 * np.pi * days) / 365.0))
#     extraterrestrial_radiation = (
#         ((24 * 60 * 0.082) / np.pi)
#         * distsun[..., None]
#         * (sunangle
#            * (np.sin(LatRad[None, ...]))
#            * (np.sin(declin[..., None]))
#            + (np.cos(LatRad[None, ...]))
#            * (np.cos(declin)[..., None])
#            * (np.sin(sunangle)))
#     )  # TODO - check this!!!

#     # Now create DataArray
#     space_coords = {
#         key: (model.domain._data.coords[key].dims, model.domain._data.coords[key].values)
#         for key in model.domain._data.coords
#     }
#     time_coords = {'time': model.time.values}
#     coords = {**time_coords, **space_coords}
#     dims = ['time'] + [dim for dim in model.domain._data.dims]
#     arr = xarray.Dataset(
#         data_vars=dict(
#             extraterrestrial_radiation=(dims, extraterrestrial_radiation)
#         ),
#         coords=coords
#     )
#     return arr


# # def _fao_equation_17():
# #     ea_mean = (
# #         (model.es_min * model.max_relative_humidity.values / 100.)
# #         + (model.es_max * model.min_relative_humidity.values / 100.)
# #     ) / 2

# # def _compute_actual_vapour_pressure(model):

# # class _ActualVapourPressure(object):
# #     def __init__(self, model):
# #         self.model = model
# #         self.eps = 0.622  # ratio of water vapour/dry air molecular weights [-]

# #     def initial(self):
# #         if self.can_use_fao_equation_17():
# #             self.compute_actual_vapour_pressure_from_relative_humidity()
# #         elif self.can_use_fao_equation_18():
# #             self.compute_actual_vapour_pressure_from_relative_humidity()
# #         elif self.can_use_fao_equation_19():
# #             self.compute_actual_vapour_pressure_from_relative_humidity()
# #         elif self.model.config.has_specific_humidity:
# #             self.compute_actual_vapour_pressure_from_specific_humidity()

# #     def compute_actual_vapour_pressure_from_specific_humidity(self):
# #         """Compute actual vapour pressure given specific
# #         humidity, using equations from Bolton (1980;
# #         """
# #         def ea(Pres, Q, eps):
# #             return (Q * Pres) / ((1 - eps) * Q + eps)

# #         self.model.ea = ea(
# #             self.model.surface_pressure,
# #             self.model.specific_humidity,
# #             self.eps
# #         )

#     # def compute_actual_vapour_pressure_from_relative_humidity(self):
#     #     self.model.ea_mean = (
#     #         (self.model.es_min * self.model.max_relative_humidity.values / 100.)
#     #         + (self.model.es_max * self.model.min_relative_humidity.values / 100.)
#     #     ) / 2

#     # def compute_actual_vapour_pressure_from_min_max_relative_humidity(self):
#     #     self.model.ea_mean = self.model.es_min * self.model.max_relative_humidity.values / 100.

#     # def compute_actual_vapour_pressure_from_mean_relative_humidity(self):
#     #     self.model.ea_mean = self.model.es_mean * self.model.mean_relative_humidity.values / 100.

#     # def can_use_fao_equation_17(self):
#     #     return (
#     #         self.model.config.has_min_daily_temperature
#     #         and self.model.config.has_max_daily_temperature
#     #         and self.model.config.has_min_relative_humidity
#     #         and self.model.config.has_max_relative_humidity
#     #     )

#     # def can_use_fao_equation_18(self):
#     #     return (
#     #         self.model.config.has_min_daily_temperature
#     #         and self.model.config.has_max_relative_humidity
#     #     )

#     # def can_use_fao_equation_19(self):
#     #     return (
#     #         self.model.config.has_max_daily_temperature
#     #         and self.model.config.has_min_daily_temperature
#     #         and self.model.config.has_mean_relative_humidity
#     #     )


# # class VapourPressureDeficit(object):
# #     def __init__(self, model):
# #         self.model = model

# #     def initial(self):
# #         self.model.vapour_pressure_deficit = np.zeros((self.model.domain.nxy))

# #     def compute_vapour_pressure_deficit(self):
# #         self.model.vapour_pressure_deficit = np.clip(
# #             self.model.es_mean - self.model.ea_mean,
# #             0,
# #             None
# #         )

# #     def dynamic(self):
# #         self.compute_vapour_pressure_deficit()
