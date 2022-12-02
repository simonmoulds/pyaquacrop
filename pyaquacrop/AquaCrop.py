#!/usr/bin/env python3

import pandas as pd
import xarray

from .Config import load_config
from .Domain import Domain
from .ModelTime import ModelTime
from .Weather import Temperature, Precipitation, ET0

# FIXME implement BMI


class AquaCrop:

    def __init__(self, configfile):
        self.config = load_config(configfile)
        self.set_domain()
        self.set_time()

    def set_domain(self):
        model_grid = self.config['MODEL_GRID']
        use_file = model_grid['use_file']
        if use_file:
            ds = xarray.open_dataset(model_grid['filename'])
        else:
            x = model_grid['x']
            y = model_grid['y']
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
            self.config['MODEL_GRID']['is_1d'] = True
            self.config['MODEL_GRID']['xy_dimname'] = "space"

        self.domain = Domain(
            ds,
            self.config['MODEL_GRID']['is_1d'],
            self.config['MODEL_GRID']['xy_dimname']
        )

    def set_time(self):
        starttime = self.config['MODEL_TIME']['start_time']
        endtime = self.config['MODEL_TIME']['end_time']
        timedelta = pd.Timedelta(1, unit='D')
        self.time = ModelTime(starttime, endtime, timedelta)

    def initial(self):
        pass
        # self.eto = ET0(self)
        # self.temperature = Temperature(self)
        # self.precipitation = Precipitation(self)
        # self.groundwater = Groundwater(self)
        # self.crop_parameters = CropParameters(self)
        # self.irrigation_parameters = IrrigationParameters(self)
        # self.management_parameters

    def dynamic(self):
        for coord in self.domain._coords:
            pass
