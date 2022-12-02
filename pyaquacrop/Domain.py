#!/usr/bin/env python3

import os
import math
import string
import datetime
import netCDF4 as nc
import xarray as xr
import numpy as np
import pandas as pd

# https://github.com/cdgriffith/Box/
from box import Box
from collections import OrderedDict

from .constants import (allowed_xy_dim_names,
                        allowed_x_dim_names,
                        allowed_y_dim_names,
                        allowed_z_dim_names,
                        allowed_t_dim_names)
# from .utils import *

# https://gis.stackexchange.com/a/166900


def get_xr_dimension_names(dataset_or_dataarray, is_1d=False, xy_dimname=None):
    dimnames = OrderedDict()
    for dim in dataset_or_dataarray.dims:
        if is_1d & (dim == xy_dimname):
            dimnames['xy'] = dim
        elif dim in allowed_x_dim_names:
            dimnames['x'] = dim
        elif dim in allowed_y_dim_names:
            dimnames['y'] = dim
        elif dim in allowed_z_dim_names:
            dimnames['z'] = dim
        elif dim in allowed_t_dim_names:
            dimnames['time'] = dim
        else:
            dimnames[dim] = dim

    return Box(dimnames, frozen_box=True)


def get_xr_dimension_axes(dataset_or_dataarray, dimnames):
    axes = OrderedDict()
    for dim, dimname in dimnames.items():
        if dimname is not None:
            axes[dim] = [position for position, value in enumerate(
                dataset_or_dataarray.dims) if value == dimname][0]
    return Box(axes, frozen_box=True)


def get_xr_coordinates(dataset_or_dataarray):
    coordinate_names = [nm for nm in dataset_or_dataarray.coords.keys()]
    coords = OrderedDict()
    # for dim, dimname in dimnames.items():
    #     if dimname is not None:
    #         coords[dim] = dataset_or_dataarray[dimname].values
    for coord in coordinate_names:
        if coord in allowed_xy_dim_names:
            coords['xy'] = coord  #dataset_or_dataarray[coord]
        elif coord in allowed_x_dim_names:
            coords['x'] = coord  #dataset_or_dataarray[coord]
        elif coord in allowed_y_dim_names:
            coords['y'] = coord  #dataset_or_dataarray[coord]
    return Box(coords, frozen_box=False)


class Base(object):

    def __init__(
            self,
            dataarray_or_dataset,
            is_1d=False,
            xy_dimname=None,
            model_is_1d=True,
            has_data=True
    ):
        self._data = dataarray_or_dataset
        if is_1d & (xy_dimname not in self._data.dims):
            raise ValueError(
                'DataArray or Dataset is specified as '
                'one-dimensional, but does not contain the '
                'provided space dimension name: ' + xy_dimname
            )
        self._is_1d = is_1d
        self._xy_dimname = xy_dimname
        self._model_is_1d = model_is_1d
        self._has_data = has_data
        self._in_memory = False
        self._update_metadata()

    def _update_metadata(self):
        # Extract metadata from xarray dataset.
        self._dims = get_xr_dimension_names(
            self._data,
            self._is_1d,
            self._xy_dimname
        )
        self._axes = get_xr_dimension_axes(self._data, self._dims)
        self._coords = get_xr_coordinates(self._data)  #, self._dims)
        self._is_1d = ('xy' in self.dims)
        self._is_2d = (
            (not self._is_1d)
            & ('x' in self.dims)
            & ('y' in self.dims)
        )
        self._is_spatial = self._is_1d | self._is_2d
        self._spatial_extent()

    def _get_2d_spatial_extent(self):
        xres = self.x[1] - self.x[0]
        yres = self.y[1] - self.y[0]
        xmin = np.min(self.x) - (self.x / 2.)
        xmax = np.max(self.x) + (xres / 2.)
        ymin = np.min(self.y) - (yres / 2.)
        ymax = np.max(self.y) + (yres / 2.)
        self._extent = Box(left=xmin, right=xmax, top=ymax, bottom=ymin, frozen_box=True)

    def _get_1d_spatial_extent(self):
        xmin = np.min(self.x)
        xmax = np.max(self.x)
        ymin = np.min(self.y)
        ymax = np.max(self.y)
        self._extent = Box(left=xmin, right=xmax, top=ymax, bottom=ymin, frozen_box=True)

    def _spatial_extent(self):
        # Extract spatial extent from data object.

        # Only relevant for two-dimensional datasets; for
        # one-dimensional datasets the extent is None.
        if self.is_2d:
            self._get_2d_spatial_extent()
        else:
            self._get_1d_spatial_extent()

    @property
    def extent(self):
        """Spatial extent of the object."""
        return self._extent

    @property
    def dims(self):
        """Dimensions of the object."""
        return tuple(self._dims.keys())

    @property
    def coords(self):
        """Coordinates of the object."""
        return self._coords

    @property
    def is_1d(self):
        """bool: Whether the object is one-dimensional."""
        return self._is_1d

    @property
    def is_2d(self):
        """bool: Whether or not the object is two-dimensional."""
        return self._is_2d

    @property
    def is_spatial(self):
        """bool: Whether or not the object is spatial."""
        return self.is_1d | self.is_2d

    # @property
    # def is_temporal(self):
    #     """bool: Whether or not the object is temporal."""
    #     return 'time' in self.dims

    # @property
    # def has_data(self):
    #     """bool: Whether or not the object has data."""
    #     return self._has_data

    # @property
    # def in_memory(self):
    #     """bool: Whether or not the data is stored in memory."""
    #     return self._in_memory

class Domain(Base):
    def __init__(
            self,
            dataarray_or_dataset,
            is_1d=False,
            xy_dimname=None,
            model_is_1d=True,
            has_data=True
    ):
        """Model spatial domain.

        The model spatial domain is the spatial grid over which
        computations are performed.

        To load data, use the ``open_hmdomain`` function.

        Parameters
        ----------
        dataarray_or_dataset: xarray.Dataset or xarray.DataArray
            xarray.Dataset or xarray.DataArray
        is_1d: bool, optional
            Whether the dataset has a one-dimensional
            representation of space (i.e. a set of points). This
            is opposed to a two-dimensional representation which will
            have coordinates to identify the location of each point.
        xy_dimname: str, optional
            If the dataset is one-dimensional, this
            parameter specifies the name of the space dimension, which
            is often non-standard (e.g. 'land').
        model_is_1d: bool, optional
            Whether the model is one-dimensional.
        has_data: bool, optional
            Whether or not the xarray object contains data
        """
        self._data = dataarray_or_dataset
        if is_1d & (xy_dimname not in self._data.dims):
            raise ValueError(
                'DataArray or Dataset is specified as '
                'one-dimensional, but does not contain the '
                'provided space dimension name: ' + xy_dimname
            )
        self._is_1d = is_1d
        self._xy_dimname = xy_dimname
        self._model_is_1d = model_is_1d
        self._has_data = has_data
        self._in_memory = False
        self._update_metadata()
        if self._is_2d:
            self._coords['xy'] = np.where(self._data['mask'])

    def _update_metadata(self):
        # Extract metadata from xarray dataset.
        self._dims = get_xr_dimension_names(
            self._data,
            self._is_1d,
            self._xy_dimname
        )
        self._axes = get_xr_dimension_axes(self._data, self._dims)
        self._coords = get_xr_coordinates(self._data)  #, self._dims)
        self._is_1d = ('xy' in self.dims)
        self._is_2d = (
            (not self._is_1d)
            & ('x' in self.dims)
            & ('y' in self.dims)
        )
        self._is_spatial = self._is_1d | self._is_2d
        self._spatial_extent()

    def _spatial_extent(self):
        # Extract spatial extent from data object.

        # Only relevant for two-dimensional datasets; for
        # one-dimensional datasets the extent is None.
        if self.is_2d:
            self._extent = get_spatial_extent(self._coords)
        else:
            self._extent = None

    @property
    def extent(self):
        """Spatial extent of the object."""
        return self._extent

    @property
    def dims(self):
        """Dimensions of the object."""
        return tuple(self._dims.keys())

    @property
    def coords(self):
        """Coordinates of the object."""
        return self._coords

    @property
    def is_1d(self):
        """bool: Whether the object is one-dimensional."""
        return self._is_1d

    @property
    def is_2d(self):
        """bool: Whether or not the object is two-dimensional."""
        return self._is_2d

    @property
    def is_spatial(self):
        """bool: Whether or not the object is spatial."""
        return self.is_1d | self.is_2d

    # @property
    # def is_temporal(self):
    #     """bool: Whether or not the object is temporal."""
    #     return 'time' in self.dims

    # @property
    # def has_data(self):
    #     """bool: Whether or not the object has data."""
    #     return self._has_data

    # @property
    # def in_memory(self):
    #     """bool: Whether or not the data is stored in memory."""
    #     return self._in_memory

    @property
    def is_latlon(self):
        """bool: Whether or not the domain uses geographical coordinates."""
        return True

    @property
    def y(self):
        """numpy.array: y-coordinates."""
        ycoord = self._coords['y']
        return self._data[ycoord].values
        # return self._coords['y'].values

    @property
    def x(self):
        """numpy.array: x-coordinates."""
        xcoord = self._coords['x']
        return self._data[xcoord].values
        # return self._coords['x'].values

    @property
    def xy(self):
        if self._is_1d:
            xycoord = self._coords['xy']
            return self._data[xycoord].values
        else:
            return None

    @property
    def nx(self):
        """int: Size of model grid in x-direction."""
        return len(self.x)

    @property
    def ny(self):
        """int: Size of model grid in y-direction."""
        return len(self.y)

    @property
    def nxy(self):
        """int: Total number of model grid points."""
        if self._is_1d:
            return len(self.xy)
        elif self._is_2d:
            return (self.nx * self.ny)

    # @property
    # def area(self):
    #     """numpy.array: Area represented by each model grid point."""
    #     return self._data['area']

    @property
    def mask(self):
        """numpy.array: Model spatial mask.

        This is relevant when the model uses a 2D rectangular grid.
        """
        return self._data['mask']

    # # TODO: I don't think these time-related properties should be in HmDomain?
    # @property
    # def starttime(self):
    #     """pandas.Timestamp: Model start time."""
    #     return pd.Timestamp(self._data['time'].values[0])

    # @property
    # def endtime(self):
    #     """pandas.Timestamp: Model end time."""
    #     return pd.Timestamp(self._data['time'].values[-1])

    # @property
    # def n_timestep(self):
    #     """int: Number of time points in model simulation."""
    #     return len(self._coords['time']) - 1

    # @property
    # def dt(self):
    #     """pandas.Timedelta: Duration of each timestep."""
    #     return (self.endtime - self.starttime) / self.n_timestep
