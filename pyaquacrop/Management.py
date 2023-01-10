#!/usr/bin/env python3

import os
import pickle
import pkgutil

from .utils import format_parameter
from .constants import AQUACROP_VERSION
from .management_parameter_dict import (MANAGEMENT_PARAMETER_DICT,
                                        MANAGEMENT_PARAMETER_ORDER)


def _load_default_data():
    res = pkgutil.get_data(__name__, "data/default_management_parameters.pkl")
    data = pickle.loads(res)
    return data


class ManagementParameterSet:

    MANAGEMENT_PARAMETERS = MANAGEMENT_PARAMETER_DICT
    MANAGEMENT_PARAMETER_ORDER = MANAGEMENT_PARAMETER_ORDER
    DEFAULT_MANAGEMENT_PARAMETERS = _load_default_data()

    def __init__(self):

        # Default is not to provide an irrigation file,
        # in which case rainfed is assumed
        # TODO we need to work out a way for users to provide either a single value or a map of input values [same goes for crop parameters etc.]
        self._default_parameter_set = self.DEFAULT_MANAGEMENT_PARAMETERS
        # self.set_default_values()

    def set_default_values(self):
        for _, param_obj in self.MANAGEMENT_PARAMETERS.items():
            param_obj.set_default_value(
                self._default_parameter_set[param_obj.name]
            )

    def update_value_description(self):
        pass

    def set_value(self):
        pass

    def get_str_format(self, name):
        return self.MANAGEMENT_PARAMETERS[name].str_format

    @property
    def default_header(self):
        pass

    def write(self, filename, header=None):
        if header is None:
            header = self.default_header
        version = format_parameter(AQUACROP_VERSION)
        # protected = format_parameter("0")
        with open(filename, "w") as f:
            f.write(header + os.linesep)
            f.write(version + " : AquaCrop Version" + os.linesep)
            for param in self.MANAGEMENT_PARAMETER_ORDER:
                if param is not None:
                    description = self.MANAGEMENT_PARAMETERS[param].value_description
                    num = self.MANAGEMENT_PARAMETERS[param].str_format
                else:
                    description = "dummy - no longer applicable"
                    num = format_parameter("-9")
                f.write(num + " : " + description + os.linesep)
