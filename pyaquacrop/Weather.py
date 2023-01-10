#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import xarray
from pint.errors import DimensionalityError
import warnings

from .Domain import get_xr_coordinates
from .constants import allowed_t_dim_names


class SpaceTimeInput:
    def __init__(self,
                 dataarray,
                 model):

        self.model = model
        self._data = self._select(dataarray)

    def initial(self):
        pass

    def _select(self, x):
        x = self._select_domain(x)
        x = self._select_time(x)
        return x

    def _select_domain(self, x):
        coords = get_xr_coordinates(x)
        lats = xarray.DataArray(
            self.model.domain.y,
            dims='xy',
            coords={'xy': self.model.domain.xy}
        )
        lons = xarray.DataArray(
            self.model.domain.x,
            dims='xy',
            coords={'xy': self.model.domain.xy}
        )
        select_dict = {coords['y']: lats, coords['x']: lons}
        return x.sel(select_dict, method='nearest')

    def _select_time(self, x):
        time_dimname = [
            key for key in x.coords.keys()
            if key in allowed_t_dim_names
        ]
        if len(time_dimname) > 0:
            select_dict = {time_dimname[0]: self.model.time.values}
            return x.sel(select_dict, method='nearest')
        else:
            return x

    def _select_point(self, i):
        self._data_subset = self._data.sel(xy=i)

    @property
    def values(self):
        return self._data_subset.values

# # Function to create SpaceTimeDataArray from file
# def open_stdataarray(filename, varname, is_1d, xy_dimname, factor=1., offset=0.):
#     if isinstance(filename, str):
#         filename = [filename]

#     ds = xarray.open_mfdataset(filename)
#     da = ds[varname]
#     da = (da * factor) + offset
#     return SpaceTimeDataArray(da, is_1d, xy_dimname)


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


def _open_dataarray(config, config_section):

    # Retrieve values from config
    filename = vars(config)[config_section].filename
    varname = vars(config)[config_section].varname
    # is_1d = vars(config)[config_section].is_1d
    # xy_dimname = vars(config)[config_section].xy_dimname
    factor = vars(config)[config_section].factor
    offset = vars(config)[config_section].offset

    # Open dataset then select dataarray
    if isinstance(filename, str):
        filename = [filename]
    ds = xarray.open_mfdataset(filename)
    da = ds[varname]

    # Apply factor/offset
    attr_dict = da.attrs
    da = (da * factor) + offset
    da.attrs.update(**attr_dict)
    return da


def open_spacetimeinput(model, config_section, convert_units=False, units=None):
    da = _open_dataarray(model.config, config_section)
    if convert_units:
        try:
            da = da.metpy.convert_units(units).metpy.dequantify()
        except DimensionalityError as e:
            warnings.warn(str(e))
    return SpaceTimeInput(da, model)


class Precipitation(SpaceTimeInput):

    def __init__(self, model):
        self.model = model
        dataarray = _open_dataarray(model.config, 'PREC')
        self._data = self._select(dataarray)

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


class Temperature:
    def __init__(self, model):
        self.tmin = open_spacetimeinput(
            model, 'TMIN',
            convert_units=True, units="degree_Celsius"
        )
        self.tmax = open_spacetimeinput(
            model, 'TMAX',
            convert_units=True, units="degree_Celsius"
        )

    @property
    def values(self):
        return np.column_stack(
            (self.tmin._data_subset.values,
             self.tmax._data_subset.values)
        )

    def _select_point(self, i):
        self.tmin._select_point(i)
        self.tmax._select_point(i)

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


class _ET0_InputData:
    def __init__(self, model):
        self.model = model
        # User-supplied:
        self.tmin = None
        self.tmax = None
        self.shortwave_radiation = None
        self.dewpoint_temperature = None
        self.max_relative_humidity = None
        self.min_relative_humidity = None
        self.mean_relative_humidity = None
        self.surface_pressure = None
        # Computed:
        self.extraterrestrial_radiation = None
        self.saturated_vapour_pressure = None
        self.actual_vapour_pressure = None
        self.net_radiation = None

    def initial(self):
        self._load_tmin()
        self._load_tmax()
        self._load_shortwave_radiation()
        self._load_dewpoint_temperature()
        self._load_max_relative_humidity()
        self._load_min_relative_humidity()
        self._load_mean_relative_humidity()
        self._load_wind_speed()
        self._load_surface_pressure()
        self._compute_penman_monteith_inputs()

    # def _select_domain(self, x):
    #     coords = get_xr_coordinates(x)
    #     lats = xarray.DataArray(
    #         self.model.domain.y,
    #         dims='xy',
    #         coords={'xy': self.model.domain.xy}
    #     )
    #     lons = xarray.DataArray(
    #         self.model.domain.x,
    #         dims='xy',
    #         coords={'xy': self.model.domain.xy}
    #     )
    #     select_dict = {coords['y']: lats, coords['x']: lons}
    #     return x.sel(select_dict, method='nearest')

    # def _select_time(self, x):
    #     time_dimname = [
    #         key for key in x.coords.keys()
    #         if key in allowed_t_dim_names
    #     ]
    #     if len(time_dimname) > 0:
    #         select_dict = {time_dimname[0]: self.model.time.values}
    #         return x.sel(select_dict, method='nearest')
    #     else:
    #         return x

    def _load_tmin(self):
        tmin = open_spacetimeinput(
            self.model, 'TMIN',
            convert_units=True, units="degree_Celsius"
        )
        self.tmin = tmin._data

    def _load_tmax(self):
        tmax = open_spacetimeinput(
            self.model, 'TMAX',
            convert_units=True, units="degree_Celsius"
        )
        self.tmax = tmax._data

    def _load_shortwave_radiation(self):
        self.shortwave_radiation = None
        if self.model.config.has_solar_radiation:
            shortwave_radiation = open_spacetimeinput(
                self.model, 'SWDOWN',
                convert_units=True, units="MJ m**-2"
            )
            self.shortwave_radiation = shortwave_radiation._data

    def _load_dewpoint_temperature(self):
        self.dewpoint_temperature = None
        if self.model.config.has_dewpoint_temperature:
            dewpoint_temperature = open_spacetimeinput(
                self.model, 'TDEW',
                convert_units=True, units="degree_Celsius"
            )
            self.dewpoint_temperature = dewpoint_temperature._data

    def _load_max_relative_humidity(self):
        self.max_relative_humidity = None
        if self.model.config.has_max_relative_humidity:
            max_relative_humidity = open_spacetimeinput(
                self.model, 'RHMAX',
                convert_units=True, units="percent"
            )
            self.max_relative_humidity = max_relative_humidity._data

    def _load_min_relative_humidity(self):
        self.min_relative_humidity = None
        if self.model.config.has_min_relative_humidity:
            min_relative_humidity = open_spacetimeinput(
                self.model, 'RHMIN',
                convert_units=True, units="percent"
            )
            self.min_relative_humidity = min_relative_humidity._data

    def _load_mean_relative_humidity(self):
        self.mean_relative_humidity = None
        if self.model.config.has_mean_relative_humidity:
            mean_relative_humidity = open_spacetimeinput(
                self.model, 'RHMEAN',
                convert_units=True, units="percent"
            )
            self.mean_relative_humidity = mean_relative_humidity._data

    def _load_wind_speed(self):
        if self.model.config.has_wind:
            if self.model.config.use_wind_components:
                wind_u = _open_dataarray(
                    self.model.config, 'WIND_U',
                )
                wind_v = _open_dataarray(
                    self.model.config, 'WIND_V',
                )
                try:
                    wind_u = wind_u.metpy.convert_units("m s**-1").metpy.dequantify()
                    wind_v = wind_v.metpy.convert_units("m s**-1").metpy.dequantify()
                except DimensionalityError as e:
                    warnings.warn(str(e))

                wind = np.sqrt(wind_u ** 2 + wind_v ** 2)
                wind = SpaceTimeInput(wind, self.model)
            else:
                wind = open_spacetimeinput(
                    self.model, 'WIND',
                    convert_units=True, units="m s**-1"
                )
            self.wind = wind._data

    def _load_surface_pressure(self):
        if self.model.config.has_surface_pressure:
            surface_pressure = open_spacetimeinput(
                self.model, 'SP',
                convert_units=True, units="kilopascal"
            )

        elif self.model.config.has_elevation:
            elevation = _open_dataarray(
                self.model, 'ELEV'
            )
            surface_pressure = (
                101.3 * ((293. - 0.0065 * elevation._data) / 293) ** 5.26
            )
            surface_pressure.attrs.update(units='kilopascal')
            surface_pressure = SpaceTimeInput(surface_pressure, self.model)
        self.surface_pressure = surface_pressure._data

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
        latitude = self.model.domain.y
        if self.model.domain.is_2d:
            # Broadcast to 2D
            latitude = (
                latitude[:, None] *
                np.ones(self.model.domain.nx)  # lat, lon
            )

        days = self.model.time.doy
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
            key: (
                self.model.domain._data.coords[key].dims,
                self.model.domain._data.coords[key].values
            )
            for key in self.model.domain._data.coords
        }
        time_coords = {'time': self.model.time.values}
        coords = {**time_coords, **space_coords}
        dims = ['time'] + [dim for dim in self.model.domain._data.dims]
        extraterrestrial_radiation = xarray.DataArray(
            data=extraterrestrial_radiation,
            coords=coords,
            dims=dims,
            name='extraterrestrial_radiation'
        )
        extraterrestrial_radiation.attrs.update(units='MJ m**-2')
        self.extraterrestrial_radiation = extraterrestrial_radiation

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
        R_s = self.shortwave_radiation
        # FIXME this should include elevation
        R_so = (0.75 + (2 * 0.00005)) * self.extraterrestrial_radiation
        R_so = R_so.clip(0.1, None)
        R_ns = (1 - alpha) * self.shortwave_radiation
        ea = self.actual_vapour_pressure
        ea = ea.clip(0, None)
        tmax_K = self.tmax + 273.15
        tmin_K = self.tmin + 273.15
        R_nl = (
            - sigma
            * ((tmax_K ** 4 + tmin_K ** 4) / 2)
            * (0.34 - 0.14 * np.sqrt(ea))
            * (1.35 * np.minimum(1, (R_s / R_so)) - 0.35)
        )
        R_n = np.maximum(0, R_ns + R_nl)
        R_n.attrs = {}
        R_n.attrs.update(
            long_name='net outgoing longwave radiation',
            units='megajoule / meter ** 2',
            standard_name='net_upward_longwave_flux_in_air'
        )
        self.net_radiation = R_n

    @staticmethod
    def _fao_equation_11(T):
        return (
            0.6108 * np.exp((17.27 + T) / (T + 237.3))
        )

    def compute_actual_vapour_pressure_from_dewpoint_temperature(self):
        ea = self._fao_equation_11(self.dewpoint_temperature)
        # print(self.dewpoint_temperature.values)
        # print(ea.values)
        ea.attrs = {}
        ea.attrs.update(
            long_name='actual vapour pressure',
            units='kPa',
            standard_name='water_vapor_partial_pressure_in_air'
        )
        self.actual_vapour_pressure = ea

    def compute_actual_vapour_pressure_from_min_max_relative_humidity(self):
        es_min = self._fao_equation_11(self.tmin)
        es_max = self._fao_equation_11(self.tmax)
        ea = (
            (es_min * self.max_relative_humidity.values / 100.)
            + (es_max * self.min_relative_humidity.values / 100.)
        ) / 2
        ea.attrs = {}
        ea.attrs.update(
            long_name='actual vapour pressure',
            units='kPa',
            standard_name='water_vapor_partial_pressure_in_air'
        )
        self.actual_vapour_pressure = ea

    def compute_actual_vapour_pressure_from_max_relative_humidity(self):
        es_min = self._fao_equation_11(self.tmin)
        ea = (
            es_min
            * self.max_relative_humidity.values / 100.
        )
        ea.attrs = {}
        ea.attrs.update(
            long_name='actual vapour pressure',
            units='kPa',
            standard_name='water_vapor_partial_pressure_in_air'
        )
        self.actual_vapour_pressure = ea

    def compute_actual_vapour_pressure_from_mean_relative_humidity(self):
        ea = (
            self.saturated_vapour_pressure * self.mean_relative_humidity.values / 100.
        )
        ea.attrs = {}
        ea.attrs.update(
            long_name='actual vapour pressure',
            units='kPa',
            standard_name='water_vapor_partial_pressure_in_air'
        )
        self.actual_vapour_pressure = ea

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
    def __init__(self, model):
        self.data = _ET0_InputData(model)
        self.data.initial()
        self.penman_monteith()

    def check_minimum_data_requirements(self):
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

        tmean = self.data.tmean
        surface_pressure = self.data.surface_pressure
        wind = self.data.wind
        vapour_pressure_deficit = self.data.vapour_pressure_deficit
        net_radiation = self.data.net_radiation

        # # For identifying bugs
        # Load eto object in scratch
        # tmean = eto._input_data.tmean
        # surface_pressure = eto._input_data.surface_pressure
        # wind = eto._input_data.wind
        # vapour_pressure_deficit = eto._input_data.vapour_pressure_deficit
        # net_radiation = eto._input_data.net_radiation

        # TODO check units throughout

        cp = 0.001013               # specific heat of air 1013 [MJ kg-1 K-1]
        TimeStepSecs = 86400        # timestep in seconds
        rs = 70                     # surface resistance, 70 [s m-1]
        R = 287.058                 # Universal gas constant [J kg-1 K-1]
        # ratio of water vapour/dry air molecular weights [-]
        eps = 0.622

        # Density of air [kg m-3]
        rho = surface_pressure * (tmean * R)

        # Latent heat [MJ kg-1]
        latent_heat = (2.501 - (0.002361 * (tmean - 273.15)))

        # Slope of vapour pressure [kPa K-1]
        deltop = 4098. * \
            (0.6108 * np.exp((17.27 * tmean) / (tmean + 237.3)))
        delbase = (tmean + 237.3) ** 2
        delta = deltop / delbase

        # Psychrometric constant [kPa K-1]
        gamma = cp * surface_pressure / (eps * latent_heat)

        # Aerodynamic resistance [m s-1]
        z = 10  # height of wind speed variable (10 meters above surface)
        Wsp_2 = wind * 4.87 / (np.log(67.8 * z - 5.42))
        ra = np.divide(
            208.,
            Wsp_2.values,
            out=np.zeros_like(Wsp_2.values),
            where=Wsp_2 != 0
        )

        PETtop = np.maximum(
            ((delta * 1e3)
             * net_radiation
             + rho
             * (cp * 1e6)
             * np.divide(
                 vapour_pressure_deficit.values,
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
        self.eto = PETmm.copy()

    # def initial(self):
    #     pass

    # def select(self):
    #     pass

    # @property
    # def values(self):
    #     pass


class _ET0_FromFile:
    def __init__(self, config):
        pass

# class Precipitation(SpaceTimeInput):

#     def __init__(self, model):
#         self.model = model
#         dataarray = _open_dataarray(model.config, 'PREC')
#         self._data = self._select(dataarray)

#     def _write_aquacrop_input(self, filename):
#         header = _climate_data_header(pd.Timestamp(self.prec._data_subset.time.values[0]))
#         header += "  Total Rain (mm)" + os.linesep
#         header += "======================="
#         with open(filename, "w") as f:
#             np.savetxt(
#                 f, self.values, fmt="%.2f", delimiter="\t",
#                 newline=os.linesep, header=header, comments=""
#             )
#         return None


class ET0(SpaceTimeInput):

    def __init__(self, model):
        self.model = model
        preprocess = bool(model.config.ET0.preprocess)
        if preprocess:
            method = str(model.config.ET0.method).lower()
            if method == "hargreaves":
                eto_obj = _ET0_Hargreaves(model)
            elif method == "penmanmonteith":
                eto_obj = _ET0_PenmanMonteith(model)
            elif method == "priestleytaylor":
                eto_obj = _ET0_PriestleyTaylor(model)
            else:
                raise ValueError("Invalid `method` in config: must be one of `Hargreaves`, `PenmanMonteith`, `PriestleyTaylor`")
        else:
            eto_obj = open_spacetimeinput(model, 'ET0')
        self._input_data = eto_obj.data
        self._data = eto_obj.eto

    def _write_aquacrop_input(self, filename):
        header = _climate_data_header(pd.Timestamp(self._data_subset.time.values[0]))
        header += "  Average ETo (mm/day)" + os.linesep
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
