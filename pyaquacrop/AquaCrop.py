#!/usr/bin/env python3

import os
import xarray

from typing import Dict, Optional, Union, Tuple
from abc import ABC, abstractmethod, abstractproperty

from .Config import Configuration
from .Domain import Domain
from .Weather import Temperature, Precipitation, ET0

# FIXME implement BMI


class AquaCrop:

    def __init__(self, configfile):
        self.config = Configuration(configfile)
        self.set_domain()

    def set_domain(self):
        use_file = self.config.model_grid.use_file
        if use_file:
            ds = xarray.open_dataset(self.config.model_grid.filename)
        else:
            x = self.config.model_grid.x
            y = self.config.model_grid.y
            space = [i+1 for i in range(len(x))]
            ds = xarray.Dataset(
                data_vars=dict(
                    x=(["space"], x),
                    y=(["space"], y),
                ),
                coords=dict(
                    space=(["space"], space)
                )
            )
            self.config.model_grid.is_1d = True
            self.config.model_grid.xy_dimname = "space"

        self.domain = Domain(
            self.config.model_grid.filename,
            self.config.model_grid.is_1d,
            self.config.model_grid.xy_dimname
        )


    def initial(self):
        self.eto = ET0(self)
        self.temperature = Temperature(self)
        self.precipitation = Precipitation(self)
        # self.groundwater = Groundwater(self)
        # self.crop_parameters = CropParameters(self)
        # self.irrigation_parameters = IrrigationParameters(self)
        # self.management_parameters

    def dynamic(self):
        for coord in self.domain._coords:
            pass
