#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import numpy as np
import pandas as pd
import xarray


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
        # TODO do this in load_config
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


class _MaxTemperature(Weather):
    def __init__(self, config):
        super().__init__(config, 'TMAX')


class _MinTemperature(Weather):
    def __init__(self, config):
        super().__init__(config, 'TMIN')


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
        super().__init__(config, 'SWDOWN')


class _LongwaveRadiation(SpaceTimeDataArray):
    def __init__(self, config):
        super().__init__(config, 'LWDOWN')


class _MaxRelativeHumudity(SpaceTimeDataArray):
    def __init__(self, config):
        super().__init__(config, 'RHMAX')


class _MinRelativeHumidity(SpaceTimeDataArray):
    def __init__(self, config):
        super().__init__(config, 'RHMIN')


class _MeanRelativeHumidity(SpaceTimeDataArray):
    def __init__(self, config):
        super().__init__(config, 'RHMEAN')


class _SpecificHumidity(SpaceTimeDataArray):
    def __init__(self, config):
        super().__init__(config, 'SH')


class _SurfacePressure(SpaceTimeDataArray):
    def __init__(self, config):
        super().__init__(config, 'PRES')


class Temperature:
    def __init__(self, config):
        self.tmin = _MaxTemperature(config)
        self.tmax = _MaxTemperature(config)

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


# Use this in config function?
def _check_valid_input(config, config_section):
    if config_section not in config.keys():
        return False
    if 'filename' not in config[config_section]:
        return False
    if not os.path.exists(config[config_section]['filename']):
        return False
    return True


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


def _compute_actual_vapour_pressure(model):

class _ActualVapourPressure(object):
    def __init__(self, model):
        self.model = model
        self.eps = 0.622  # ratio of water vapour/dry air molecular weights [-]

    def initial(self):
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
        humidity, using equations from Bolton (1980;
        """
        def ea(Pres, Q, eps):
            return (Q * Pres) / ((1 - eps) * Q + eps)

        self.model.ea = ea(
            self.model.surface_pressure,
            self.model.specific_humidity,
            self.eps
        )

    def compute_actual_vapour_pressure_from_relative_humidity(self):
        self.model.ea_mean = (
            (self.model.es_min * self.model.max_relative_humidity.values / 100.)
            + (self.model.es_max * self.model.min_relative_humidity.values / 100.)
        ) / 2

    def compute_actual_vapour_pressure_from_min_max_relative_humidity(self):
        self.model.ea_mean = self.model.es_min * self.model.max_relative_humidity.values / 100.

    def compute_actual_vapour_pressure_from_mean_relative_humidity(self):
        self.model.ea_mean = self.model.es_mean * self.model.mean_relative_humidity.values / 100.

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


class _ET0_PenmanMonteith:
    def __init__(self, config):
        # Idea here is to have exactly the variables we need, and provide a class for that variable which either reads it directly or computes it from other variables
        self.config = config
        self.tmin = _MinTemperature(config)
        self.tmax = _MaxTemperature(config)
        self.swdown = _SolarRadiation(config)
        self.extrat = _ExtraterrestrialRadiation(config)
        self.wind_speed = _WindSpeed(config)
        self.net_radiation = _NetRadiation(config)
        self.es = _SaturationVapourPressure(config)
        self.ea = _ActualVapourPressure(config)
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
        self.tmin = _MinTemperature(config)
        self.tmax = _MaxTemperature(config)

    def initial(self):
        pass

    def select(self):
        pass

    @property
    def values(self):
        pass


class _ET0_PriestleyTaylor:
    def __init__(self, config):
        self.tmin = _MinTemperature(config)
        self.tmax = _MaxTemperature(config)

    def initial(self):
        pass

    def select(self):
        pass

    @property
    def values(self):
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
