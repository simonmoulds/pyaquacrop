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


def _open_precipitation_stdataarray(config):
    da = open_weather_dataarray(config, 'PREC')
    return Precipitation(da, is_1d, xy_dimname)


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


class ET0_FromFile:
    def __init__(self, config):
        self.eto = _open_weather_stdataarray(config, 'ET0')

    # def initial(self):
    #     self.prec.initial()

    # def select(self, lat, lon):
    #     self.prec.select(lat, lon)

    # @property
    # def values(self):
    #     return self.prec.values


class ET0_PenmanMonteith:
    def __init__(self, config):
        pass


class _NetRadiation:
    def __init__(self, model):
        self.model = model
        self.alpha = 0.23  # albedo, 0.23 [-]
        self.sigma = 4.903e-9  # stephan boltzmann [W m-2 K-4]

    def initial(self):
        self.compute_net_radiation()

    def compute_net_radiation(self):
        Rso = np.maximum(
            0.1,
            ((0.75 + (2 * 0.00005)) * self.model.extraterrestrial_radiation)
        )  # clear sky solar radiation MJ d-1
        Rsin_MJ = 0.086400 * self.model.shortwave_radiation.values
        Rlnet_MJ = (
            - self.sigma
            * ((self.model.tmax.values ** 4 + self.model.tmin.values ** 4) / 2)
            * (0.34 - 0.14 * np.sqrt(np.maximum(0, (self.model.ea_mean / 1000))))
            * (1.35 * np.minimum(1, (Rsin_MJ / Rso)) - 0.35)
        )
        Rlnet_Watt = Rlnet_MJ / 0.086400
        self.model.net_radiation = np.maximum(
            0,
            ((1 - self.alpha) * self.model.shortwave_radiation.values + Rlnet_Watt)
        )

    def dynamic(self):
        self.compute_net_radiation()


class _ExtraterrestrialRadiation:
    def __init__(self, model):
        self.model = model

    def initial(self):
        latitudes = self.model.domain.y
        if self.model.domain.is_2d:
            latitudes = np.broadcast_to(
                self.model.domain.y[:, None],
                (self.model.domain.ny, self.model.domain.nx)
            )

        self.latitudes = latitudes[self.model.domain.mask.values]
        self.compute_extraterrestrial_radiation()

    def compute_extraterrestrial_radiation(self):
        """Compute extraterrestrial radiation (MJ m-2 d-1)"""
        LatRad = self.latitudes * np.pi / 180.0
        declin = 0.4093 * (
            np.sin(((2.0 * np.pi * self.model.time.doy) / 365.) - 1.405)
        )
        arccosInput = (-(np.tan(LatRad)) * (np.tan(declin)))
        arccosInput = np.clip(arccosInput, -1, 1)
        sunangle = np.arccos(arccosInput)
        distsun = 1 + 0.033 * (np.cos((2 * np.pi * self.model.time.doy) / 365.0))
        self.extraterrestrial_radiation = (
            ((24 * 60 * 0.082) / np.pi)
            * distsun
            * (sunangle
               * (np.sin(LatRad))
               * (np.sin(declin))
               + (np.cos(LatRad))
               * (np.cos(declin))
               * (np.sin(sunangle)))
        )
        # TODO convert to xarray


def _compute_extraterrestrial_radiation(model):
    """Compute extraterrestrial radiation (MJ m-2 d-1)"""
    latitude = model.domain.latitude
    if model.domain.is_2d:
        latitude = latitude[:, None] * np.ones(model.domain.nx)  # lat, lon

    days = model.time.days
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
    )  # TODO - check this!!!

    # Now create DataArray
    space_coords = {
        key: (model.domain._data.coords[key].dims, model.domain._data.coords[key].values)
        for key in model.domain._data.coords
    }
    time_coords = {'time': model.time.values}
    coords = {**time_coords, **space_coords}
    dims = ['time'] + [dim for dim in model.domain._data.dims]
    arr = xarray.Dataset(
        data_vars=dict(
            extraterrestrial_radiation=(dims, extraterrestrial_radiation)
        ),
        coords=coords
    )
    return arr


def _compute_saturation_vapour_pressure(model):
    def es(T):
        return (
            610.8 *
            np.exp((17.27 * (T - 273.15)) / ((T - 273.15) + 237.3))
        )
    if 'tmin' in kwargs and 'tmax' in kwargs:
        es_min = es(kwargs['tmin']._data)
        es_max = es(kwargs['tmax']._data)
        es = (es_min + es_max) / 2.
    elif 'tmean' in kwargs:
        es = es(kwargs['tmean']._data)
    return es


# def _fao_equation_17():
#     ea_mean = (
#         (model.es_min * model.max_relative_humidity.values / 100.)
#         + (model.es_max * model.min_relative_humidity.values / 100.)
#     ) / 2

# def _compute_actual_vapour_pressure(model):

# class _ActualVapourPressure(object):
#     def __init__(self, model):
#         self.model = model
#         self.eps = 0.622  # ratio of water vapour/dry air molecular weights [-]

#     def initial(self):
#         if self.can_use_fao_equation_17():
#             self.compute_actual_vapour_pressure_from_relative_humidity()
#         elif self.can_use_fao_equation_18():
#             self.compute_actual_vapour_pressure_from_relative_humidity()
#         elif self.can_use_fao_equation_19():
#             self.compute_actual_vapour_pressure_from_relative_humidity()
#         elif self.model.config.has_specific_humidity:
#             self.compute_actual_vapour_pressure_from_specific_humidity()

#     def compute_actual_vapour_pressure_from_specific_humidity(self):
#         """Compute actual vapour pressure given specific
#         humidity, using equations from Bolton (1980;
#         """
#         def ea(Pres, Q, eps):
#             return (Q * Pres) / ((1 - eps) * Q + eps)

#         self.model.ea = ea(
#             self.model.surface_pressure,
#             self.model.specific_humidity,
#             self.eps
#         )

    # def compute_actual_vapour_pressure_from_relative_humidity(self):
    #     self.model.ea_mean = (
    #         (self.model.es_min * self.model.max_relative_humidity.values / 100.)
    #         + (self.model.es_max * self.model.min_relative_humidity.values / 100.)
    #     ) / 2

    # def compute_actual_vapour_pressure_from_min_max_relative_humidity(self):
    #     self.model.ea_mean = self.model.es_min * self.model.max_relative_humidity.values / 100.

    # def compute_actual_vapour_pressure_from_mean_relative_humidity(self):
    #     self.model.ea_mean = self.model.es_mean * self.model.mean_relative_humidity.values / 100.

    # def can_use_fao_equation_17(self):
    #     return (
    #         self.model.config.has_min_daily_temperature
    #         and self.model.config.has_max_daily_temperature
    #         and self.model.config.has_min_relative_humidity
    #         and self.model.config.has_max_relative_humidity
    #     )

    # def can_use_fao_equation_18(self):
    #     return (
    #         self.model.config.has_min_daily_temperature
    #         and self.model.config.has_max_relative_humidity
    #     )

    # def can_use_fao_equation_19(self):
    #     return (
    #         self.model.config.has_max_daily_temperature
    #         and self.model.config.has_min_daily_temperature
    #         and self.model.config.has_mean_relative_humidity
    #     )


# class VapourPressureDeficit(object):
#     def __init__(self, model):
#         self.model = model

#     def initial(self):
#         self.model.vapour_pressure_deficit = np.zeros((self.model.domain.nxy))

#     def compute_vapour_pressure_deficit(self):
#         self.model.vapour_pressure_deficit = np.clip(
#             self.model.es_mean - self.model.ea_mean,
#             0,
#             None
#         )

#     def dynamic(self):
#         self.compute_vapour_pressure_deficit()


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
        # Computed:
        self.extraterrestrial_radiation = None
        self.es = None
        self.ea = None
        self.net_radiation = None

    def _load_tmin(self):
        self.tmin = _open_weather_dataarray(self.config, 'TMIN')

    def _load_tmax(self):
        self.tmax = _open_weather_dataarray(self.config, 'TMAX')

    def _load_solar_radiation(self):
        """Load or calculate solar radiation"""
        if self.model.config.has_solar_radiation:
            self.shortwave_radiation = _open_weather_dataarray(self.model.config, 'SWDOWN')

    def _load_extrat_radiation(self):
        """Compute extraterrestrial radiation (MJ m-2 d-1)"""
        latitude = self.model.domain.latitude
        if model.domain.is_2d:
            latitude = latitude[:, None] * np.ones(self.model.domain.nx)  # lat, lon

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
        )  # TODO - check this!!!

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

    def _load_wind_speed(self):
        pass

    def _load_es(self):
        pass

    def _load_ea(self):
        if self.can_use_fao_equation_17():
            self.compute_actual_vapour_pressure_from_relative_humidity()
        elif self.can_use_fao_equation_18():
            self.compute_actual_vapour_pressure_from_relative_humidity()
        elif self.can_use_fao_equation_19():
            self.compute_actual_vapour_pressure_from_relative_humidity()
        elif self.model.config.has_specific_humidity:
            self.compute_actual_vapour_pressure_from_specific_humidity()

    def compute_actual_vapour_pressure_from_specific_humidity(self):
        """Compute actual vapour pressure given specific
        humidity, using equations from Bolton (1980);
        """
        def ea(Pres, Q, eps):
            return (Q * Pres) / ((1 - eps) * Q + eps)

        self.ea_mean = ea(
            self.model.surface_pressure,
            self.model.specific_humidity,
            self.eps
        )

    def compute_actual_vapour_pressure_from_relative_humidity(self):
        self.ea_mean = (
            (self.es_min * self.max_relative_humidity.values / 100.)
            + (self.es_max * self.min_relative_humidity.values / 100.)
        ) / 2

    def compute_actual_vapour_pressure_from_min_max_relative_humidity(self):
        self.ea_mean = (
            self.es_min
            * self.max_relative_humidity.values / 100.
        )

    def compute_actual_vapour_pressure_from_mean_relative_humidity(self):
        self.ea_mean = (
            self.es_mean * self.mean_relative_humidity.values / 100.
        )

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

    def _load_net_radiation(self):
        # requirements:
        # extraterrestrial_radiation
        # shortwave_radiation
        # tmin, tmax
        # ea_mean
        alpha = 0.23  # albedo, 0.23 [-]
        sigma = 4.903e-9  # stephan boltzmann [W m-2 K-4]
        Rso = np.maximum(
            0.1,
            ((0.75 + (2 * 0.00005)) * self.extraterrestrial_radiation)
        )  # clear sky solar radiation MJ d-1
        Rsin_MJ = 0.086400 * self.shortwave_radiation.values
        Rlnet_MJ = (
            - sigma
            * ((self.tmax.values ** 4 + self.tmin.values ** 4) / 2)
            * (0.34 - 0.14 * np.sqrt(np.maximum(0, (self.ea_mean / 1000))))
            * (1.35 * np.minimum(1, (Rsin_MJ / Rso)) - 0.35)
        )
        Rlnet_Watt = Rlnet_MJ / 0.086400
        net_radiation = np.maximum(
            0,
            ((1 - alpha) * self.model.shortwave_radiation.values + Rlnet_Watt)
        )


class _ET0_PenmanMonteith:
    def __init__(self, config):
        # Idea here is to have exactly the variables we need, and provide a class for that variable which either reads it directly or computes it from other variables
        pass
        # self.config = config
        # self.tmin = _MinTemperature(config)
        # self.tmax = _MaxTemperature(config)
        # self.swdown = _SolarRadiation(config)
        # self.extrat = _ExtraterrestrialRadiation(config)
        # self.wind_speed = _WindSpeed(config)
        # self.net_radiation = _NetRadiation(config)
        # self.es = _SaturationVapourPressure(config)
        # self.ea = _ActualVapourPressure(config)
        # # self.delta = _SaturationVapourPressureSlope(config)
        # self.soil_heat_flux = _SoilHeatFlux(config)

    def initial(self):
        pass

    def select(self):
        pass

    @property
    def values(self):
        pass


class _ET0_Hargreaves:
    def __init__(self, config):
        pass
        # self.tmin = _MinTemperature(config)
        # self.tmax = _MaxTemperature(config)

    def initial(self):
        pass

    def select(self):
        pass

    @property
    def values(self):
        pass


class _ET0_PriestleyTaylor:
    def __init__(self, config):
        pass
        # self.tmin = _MinTemperature(config)
        # self.tmax = _MaxTemperature(config)

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
