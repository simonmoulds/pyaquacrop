#!/usr/bin/env python3

import os
from constants import (
    AQUACROP_VERSION,
    VALID_SUBKIND,
    VALID_PLANTING,
    VALID_MODECYCLE,
    VALID_PMETHOD,
)


def _format_crop_parameter(number_str, pad_before=6, pad_after=7):
    try:
        whole, frac = number_str.split(".")
    except ValueError:
        whole = number_str.split(".")[0]
        frac = None
    pad_before = pad_before - len(whole)
    whole = " " * (pad_before - len(whole)) + whole
    if frac is None:
        number_str = whole + " " * (pad_after + 1)
    else:
        frac = "." + frac + " " * (pad_after - len(frac))
        number_str = whole + frac
    return number_str


class CropParameters:
    def __init__(self, config):
        self.config = config
        # self.crop_name
        self.Version = AQUACROP_VERSION

    def _load_default_parameter_dict(crop_name, gdd=True):
        # TESTING
        path = os.path.join("data-raw/AquaCropV70No17082022/DATA")
        filename = os.path.join(path, "WheatGDD.CRO")
        with open(filename, "r", errors="replace") as f:
            contents = f.read().splitlines()
        # Skip the first line, which is a header
        contents = contents[1:]
        params, param_descs = [], []
        for ln in contents:
            param = ln.split(None, 1)[0]
            try:
                param_desc = ln.split(":")[1].lstrip()
            except IndexError:
                param_desc = "NO DESCRIPTION AVAILABLE"
            params.append(param)
            param_descs.append(param_desc)

        param_dict = {i: [params[i], param_descs[i]] for i in range(len(contents))}
        return param_dict

    def _set_Version(self):
        self.Version = AQUACROP_VERSION

    def _write_Version(self) -> str:
        value = _format_crop_parameter("{:0.1f}".format(self.Version))
        description = "AquaCrop version"
        return " : ".join(value, description)

    def _set_FileProtected(self) -> str:
        self.FileProtected = 1

    def _write_FileProtected(self) -> str:
        # AC convention is 1 = Unprotected, 0 = Protected
        value = _format_crop_parameter("{:0d}".format(1))
        description = "File not protected"
        return " : ".join(value, description)

    def _set_subkind(self, value: int):
        if value not in VALID_SUBKIND:
            raise ValueError("Invalid crop subkind.")
        self.subkind = value

    def _write_subkind(self) -> str:
        value = _format_crop_parameter("{:0d}".format(self.subkind))
        description = VALID_SUBKIND[self.subkind]
        return " : ".join(value, description)

    def _set_Planting(self, value: int):
        if value not in VALID_PLANTING:
            raise ValueError("Invalid value for `Planting` crop parameter")
        self.Planting = value

    def _write_Planting(self) -> str:
        value = _format_crop_parameter("{:0d}".format(self.Planting))
        if (self.subkind == 4) & (self.Planting in [0, 1]):
            method = VALID_PLANTING[self.Planting]
            description = f"Crop is {method} in 1st year"
        else:
            description = "Crop is regrowth"
        return " : ".join(value, description)

    def _set_ModeCycle(self, value: int):
        if value not in VALID_MODECYCLE:
            raise ValueError("Invalid value for `ModeCycle`")
        self.ModeCycle = value

    def _write_ModeCycle(self) -> str:
        value = _format_crop_parameter("{:0d}".format(self.ModeCycle))
        description = VALID_MODECYCLE[self.ModeCycle]
        return " : ".join(value, description)

    def _set_pMethod(self, value):
        if value not in VALID_PMETHOD:
            raise ValueError("Invalid value for `pMethod`")
        self.pMethod = value

    def _write_pMethod(self, value) -> str:
        description = VALID_PMETHOD[self.pMethod]
        return " : ".join(value, description)

    def _set_Tbase(self, value: float):
        self.Tbase = value

    def _write_Tbase(self) -> str:
        value = _format_crop_parameter(":0.1f".format(self.Tbase))
        description = (
            "Base temperature (degC) below which crop development does not progress"
        )
        return " : ".join(value, description)

    def _set_Tupper(self, value: float):
        self.Tupper = value

    def _write_Tupper(self) -> str:
        value = _format_crop_parameter(":0.1f".format(self.Tupper))
        description = (
            "Upper temperature (degC) above which crop development no longer increases"
            " with an increase in temperature"
        )
        return " : ".join(value, description)

    def _set_GDDaysToHarvest(self, value):
        self.GDDaysToHarvest = value

    def _write_GDDaysToHarvest(self) -> str:
        value = _format_crop_parameter(":0d".format(self.GDDaysToHarvest))
        description = "Total length of crop cycle in growing degree-days"
        return " : ".join(value, description)

    def _set_pLeafDefUL(self, value):
        self.pLeafDefUL = value

    def _write_pLeafDefUL(self) -> str:
        value = _format_crop_parameter(":0.2f".format(self.pLeafDefUL))
        description = (
            "Soil water depletion factor for canopy expansion (p-exp) - Upper threshold"
        )
        return " : ".join(value, description)

    def _set_KsShapeFactor(self, value: float):
        self.KsShapeFactor = value

    def _write_KsShapeFactor(self) -> str:
        value = _format_crop_parameter(":0.2f".format(self.KsShapeFactor))
        description = "Shape factor for water stress coefficient for canopy expansion (0.0 = straight line)"
        return " : ".join(value, description)

    def _set_pdef(self, value: float):
        self.pdef = value

    def _write_pdef(self) -> str:
        value = _format_crop_parameter(":0.1f".format(self.pdef))
        description = "Soil water depletion fraction for stomatal control (p - sto) - Upper threshold"
        return " : ".join(value, description)

    def _set_KsShapeFactorStomata(self, value: float):
        self.KsShapeFactorStomata = value

    def _write_KsShapeFactorStomata(self) -> str:
        value = _format_crop_parameter(":0.2f".format(self.KsShapeFactorStomata))

# import math

# class Parameter:
#     def __init__(self)
#         pass

# class CropParameter:
#     def __init__(self, crop_type):
#         _check_valid_crop_type(...)
#         self.name = None
#         self.description = None
#         self.valid_range = [-math.inf, math.inf]
#         self.str_format = None

#     def _set_crop_type(self, crop_type):
#         if _check_valid_crop(crop_type):
#             self.crop_type = crop_type
#         else:
#             raise ValueError()

#     def _check_valid_crop(self, crop_type):
#         return True

#     def _get_default_value(self):
#         raise NotImplementedError

#     @property
#     def description(self):
#         return self.description

#     @property
#     def valid_range(self):
#         return self.valid_range

#     @property
#     def str_format(self):
#         return self.str_format()

# class KsShapeFactor(Parameter):
#     def __init__(self, crop_type):
#         super(KsShapeFactor, self).__init__(crop_type=crop_type)
#         self.name = "KsShapeFactor"
#         self.description = (
#             "Shape factor for water stress coefficient for canopy expansion (0.0 = straight line)"
#         )
#         self.valid_range = [0, 1]
#         self.str_format = "{0.1f}"

#     def _set_value(self, value):
#         if value >= self.valid_range[0] and value <= self.valid_range[1]:
#             self.value = value
#         else:
#             raise ValueError("Out of range")
