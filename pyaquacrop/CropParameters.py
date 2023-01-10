#!/usr/bin/env python3

import os
import pickle
import pkgutil

from .utils import format_parameter
from .constants import (AQUACROP_VERSION,
                        CROP_TYPES,
                        GDD_CROP_TYPES)

from .crop_parameter_dict import (CROP_PARAMETER_DICT,
                                  ONSET_CROP_PARAMETER_DICT,
                                  CROP_PARAMETER_ORDER,
                                  ONSET_CROP_PARAMETER_ORDER)


def _load_default_data():
    res = pkgutil.get_data(__name__, "data/default_crop_parameters.pkl")
    data = pickle.loads(res)
    return data


# This should perhaps inherit dictionary with an additional write method
class CropParameterSet:
    CROP_PARAMETERS = CROP_PARAMETER_DICT
    ONSET_CROP_PARAMETERS = ONSET_CROP_PARAMETER_DICT
    CROP_PARAMETER_ORDER = CROP_PARAMETER_ORDER
    ONSET_CROP_PARAMETER_ORDER = ONSET_CROP_PARAMETER_ORDER
    DEFAULT_CROP_PARAMETERS = _load_default_data()
    VALID_CROP_TYPES = CROP_TYPES + GDD_CROP_TYPES

    # TODO provide some mechanism for users to supply parameter values
    def __init__(self, crop_name):

        # Check crop_name is valid
        self.crop_name = crop_name
        if self.crop_name not in self.VALID_CROP_TYPES:
            raise ValueError()

        self._default_parameter_set = self.DEFAULT_CROP_PARAMETERS[crop_name]
        self.crop_name = crop_name
        self.crop_parameter_names = tuple(self.CROP_PARAMETERS.keys())
        # Now that we have verified the crop type, pull default values
        self.set_default_values()

    def set_default_values(self):
        # Update common crop parameters
        for _, param_obj in self.CROP_PARAMETERS.items():
            param_obj.set_default_value(
                self._default_parameter_set[param_obj.name]
            )

        # Retrieve subkind and planting parameters, as these
        # are used to select the appropriate documentation
        # for other parameters
        self.update_planting()
        self.update_subkind()

        # If forage crop, update onset parameters
        if self.subkind == 4:
            for _, param_obj in self.ONSET_CROP_PARAMETERS.items():
                param_obj.set_default_value(
                    self._default_parameter_set[param_obj.name]
                )

        # Update parameter descriptions
        self.update_value_descriptions()

    def update_value_descriptions(self):
        if self.subkind == 4:
            param_dict = {**self.CROP_PARAMETERS, **self.ONSET_CROP_PARAMETERS}
        else:
            param_dict = self.CROP_PARAMETERS

        for _, param_obj in param_dict.items():
            param_obj.set_value_description(
                value_dict={
                    'Planting': self.planting,
                    'subkind': self.subkind
                }
            )

    def set_value(self, name, value):
        try:
            self.CROP_PARAMETERS[name].set_value(value)
        except KeyError:
            raise ValueError
        self.update_planting()
        self.update_subkind()
        self.update_value_descriptions()

    def update_planting(self):
        self.planting = self.CROP_PARAMETERS["Planting"].value

    def update_subkind(self):
        self.subkind = self.CROP_PARAMETERS["subkind"].value

    def get_str_format(self, name):
        return self.CROP_PARAMETERS[name].str_format

    @property
    def default_header(self):
        return "Crop %s file" % self.crop_name

    @property
    def default_onset_header(self):
        return " Internal crop calendar" + os.linesep + " ======================"

    def _write_aquacrop_input(self, filename, header=None):
        if header is None:
            header = self.default_header
        version = format_parameter(AQUACROP_VERSION)
        protected = format_parameter("0")
        with open(filename, "w") as f:
            f.write(header + os.linesep)
            f.write(version + " : AquaCrop Version" + os.linesep)
            f.write(protected + " : File protected" + os.linesep)
            for param in self.CROP_PARAMETER_ORDER:
                if param is not None:
                    description = self.CROP_PARAMETERS[param].value_description
                    num = self.CROP_PARAMETERS[param].str_format
                else:
                    description = "dummy - no longer applicable"
                    num = format_parameter("-9")
                f.write(num + " : " + description + os.linesep)

            if self.subkind == 4:
                # Add internal crop calendar
                f.write(os.linesep)
                f.write(self.default_onset_header + os.linesep)
                for param in self.ONSET_CROP_PARAMETER_ORDER:
                    if param is not None:
                        description = self.ONSET_CROP_PARAMETERS[
                            param
                        ].value_description
                        num = self.ONSET_CROP_PARAMETERS[param].str_format
                    else:
                        description = "dummy - no longer applicable"
                        num = format_parameter("-9")
                    f.write(num + " : " + description + os.linesep)
