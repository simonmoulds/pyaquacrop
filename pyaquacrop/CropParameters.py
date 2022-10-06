#!/usr/bin/env python3

import os
import math
import pickle
import pkgutil
from typing import Dict, Optional, Union, Tuple
from abc import ABC, abstractmethod, abstractproperty

from constants import AQUACROP_VERSION


def _format_crop_parameter(number_str, pad_before=6, pad_after=7):
    try:
        whole, frac = number_str.split(".")
    except ValueError:
        whole = number_str.split(".")[0]
        frac = None
    pad_before_adj = max(pad_before - len(whole), 2) # Leave two spaces at a minimum
    whole = " " * pad_before_adj + whole
    pad_after_adj = min(pad_after, (pad_after + pad_before - len(whole)))
    if frac is None:
        number_str = whole + " " * (pad_after_adj + 1)
    else:
        frac = "." + frac + " " * (pad_after_adj - len(frac))
        number_str = whole + frac
    return number_str


def _load_default_data():
    res = pkgutil.get_data(
        __name__, 'data/default_crop_parameters.pkl'
    )
    data = pickle.loads(res)
    return data


class Parameter(ABC):

    @abstractmethod
    def set_value(self):
        pass

    @abstractmethod
    def check_value(self):
        pass

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def description(self):
        pass

    @abstractproperty
    def default_value(self):
        pass

    @abstractproperty
    def valid_range(self):
        pass

    @abstractproperty
    def str_format(self):
        pass

class _CropParameter(Parameter):
    def __init__(self,
                 name: str,
                 datatype: type,
                 discrete: bool,
                 valid_range: tuple,
                 description: Union[dict, tuple, str],
                 depends_on: Optional[tuple] = None,
                 scale: Optional[int] = 2,
                 required: bool = True,
                 missing_value: int = -9):

        self._value = None
        self._default_value = None
        self._name = name
        self._datatype = datatype
        self._discrete = discrete
        self._valid_range = valid_range
        self._description = description
        self._depends_on = depends_on
        self._scale = scale
        self._required = required
        self._missing_value = missing_value

    def set_value(self, value):
        self.check_value(value)
        # self.set_value_description()

    def set_default_value(self, default_value):
        if self.datatype is int:
            default_value = int(default_value)
        else:
            default_value = float(default_value)

        self._default_value = default_value
        self._value = default_value
        # self.set_value_description()

    def set_value_description(self, planting = None, subkind = None):
        planting_subkind = {'Planting' : planting, 'subkind' : subkind}
        description = self._description
        if self.depends_on is not None:
            if len(self.depends_on) == 2:
                value1, value2 = tuple([planting_subkind[key] for key in self.depends_on])
                try:
                    description = description[value1]
                except KeyError:
                    description = description['default']
                try:
                    description = description[value2]
                except KeyError:
                    description = description['default']
            else:
                value1 = planting_subkind[self.depends_on[0]]
                try:
                    description = description[value1]
                except KeyError:
                    description = description['default']
        if self.discrete:
            description = description[self.value]

        if not self.required and isinstance(description, tuple):
            if self.value == self.missing_value:
                description = description[1]
            else:
                description = description[0]
        self._value_description = description

    @property
    def value_description(self):
        return self._value_description

    @property
    def value(self):
        return self._value

    @property
    def name(self):
        return self._name

    @property
    def datatype(self):
        return self._datatype

    @property
    def discrete(self):
        return self._discrete

    @property
    def default_value(self):
        pass

    @property
    def valid_range(self):
        return self._valid_range

    @property
    def description(self):
        return self._description

    @property
    def depends_on(self):
        return self._depends_on

    @property
    def scale(self):
        return self._scale

    @property
    def required(self):
        return self._required

    @property
    def missing_value(self):
        return self._missing_value

    @property
    def str_format(self):
        if self.datatype is int:
            fmt = f"{self.value:d}"
        else:
            fmt = f"{self.value:.{self.scale}f}"
        num = _format_crop_parameter(fmt)
        # return num + ' : ' + self.description
        return num



class _DiscreteCropParameter(_CropParameter):
    def __init__(self,
                 name: str,
                 valid_range: tuple,
                 description: dict,
                 depends_on: Optional[tuple] = None,
                 required: bool = True,
                 missing_value: Optional[int] = -9):

        super(_DiscreteCropParameter, self).__init__(
            name = name,
            datatype = int,
            discrete = True,
            valid_range = valid_range,
            description = description,
            depends_on = depends_on,
            scale = None,
            required = required,
            missing_value = missing_value
        )

    def check_value(self, value):
        if not float(value).is_integer():
            raise ValueError    # TODO add informative error message
        value = int(value)
        if not value in self.valid_range:
            raise ValueError
        self.value = value      # TODO add informative error message

class _ContinuousCropParameter(_CropParameter):
    def __init__(self,
                 name: str,
                 datatype: type,
                 valid_range: tuple,
                 description: Union[str, tuple],
                 depends_on: Optional[tuple] = None,
                 scale: Optional[int] = 2,
                 required: bool = True,
                 missing_value: Optional[int] = -9):

        super(_ContinuousCropParameter, self).__init__(
            name = name,
            datatype = datatype,
            discrete = False,
            valid_range = valid_range,
            description = description,
            depends_on = depends_on,
            scale = scale,
            required = required,
            missing_value = missing_value
        )

    def check_value(self, value):
        # Check that value is (or can be) an integer:
        if self.datatype is int:
            if not float(value).is_integer():
                raise ValueError
            value = int(value)
        else:
            value = float(value)

        # See if value is required
        if not self.required and value == self.missing_value:
            self.value = self.missing_value
        else:
            # Check that value is within the valid range:
            if (value < self.valid_range[0]) | (value > self.valid_range[1]):
                raise ValueError
            self.value = value

    def set_description(self, planting = None, subkind = None):
        description = self.select_description(planting, subkind)
        description = description[self.value]
        if self.required and self.value == self.missing_value:
            if isinstance(description, tuple):
                description = description[1]
        return description

# The idea here is to have a dictionary of all crop parameters which can then be organised properly in a CropParameterDict class
CROP_PARAMETER_DICT = {
    # ################################# #
    # Crop type                         #
    # ################################# #
    "subkind" : _DiscreteCropParameter(
        name = "subkind",
        valid_range = (1, 2, 3, 4),
        description = {
            1: "leafy vegetable crop",
            2: "fruit/grain producing crop",
            3: "root/tuber crop",
            4: "forage_crop"
        }
    ),
    # ################################# #
    # Sown, transplanting or regrowth   #
    # ################################# #
    "Planting" : _DiscreteCropParameter(
        name = "Planting",
        valid_range = (0, 1, -9),
        description = {
            "default" : {
                1: "Crop is sown",
                0: "Crop is transplanted",
                -9: "Crop is regrowth"
            },
            4: {
                1: "Crop is sown in first year",
                0: "Crop is transplanted in first year",
                -9: "Crop is regrowth"
            },
        },
        depends_on = ("Planting",)
    ),
    # ################################# #
    # Mode (description crop cycle)     #
    # ################################# #
    "ModeCycle" : _DiscreteCropParameter(
        name = "ModeCycle",
        valid_range = (0, 1),
        description = {
            0 : "Determination of crop cycle: by growing-degree days",
            1 : "Determination of crop cycle: by calendar days"
        }
    ),
    # ################################# #
    # p correction for ET               #
    # ################################# #
    "pMethod" : _DiscreteCropParameter(
        name = "pMethod",
        valid_range = (0, 1),
        description = {
            0: "No adjustment by ETo of soil water depletion factors (p)",
            1: "Soil water depletion factors (p) are adjusted by ETo",
        }
    ),
    # ################################# #
    # temperatures controlling crop     #
    # development                       #
    # ################################# #
    "Tbase" : _ContinuousCropParameter(
        name = "Tbase",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Base temperature (degC) below which crop development does not progress",
        scale = 1
    ),
    "Tupper" : _ContinuousCropParameter(
        name = "Tupper",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description =  "Upper temperature (degC) above which crop development no longer increases with an increase in temperature",
        scale = 1
    ),
    # ################################# #
    # required growing degree days to   #
    # complete the crop cycle (is       #
    # identical to maturity)            #
    # ################################# #
    "GDDaysToHarvest0": _ContinuousCropParameter(
        name = "GDDaysToHarvest0",
        datatype = int,
        valid_range = [-math.inf, math.inf],
        description = "Total length of crop cycle in growing degree-days"
    ),
    # ################################# #
    # water stress                      #
    # ################################# #
    "pLeafDefUL": _ContinuousCropParameter(
        name = "pLeafDefUL",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Soil water depletion factor for canopy expansion (p-exp) - Upper threshold",
        scale = 2
    ),
    "pLeafDefLL": _ContinuousCropParameter(
        name = "pLeafDefLL",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Soil water depletion factor for canopy expansion (p-exp) - Lower threshold",
        scale = 2
    ),
    "KsShapeFactorLeaf": _ContinuousCropParameter(
        name = "KsShapeFactorLeaf",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Shape factor for water stress coefficient for canopy expansion (0.0 = straight line)",
        scale = 1
    ),
    "pdef" : _ContinuousCropParameter(
        name = "pdef",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Soil water depletion fraction for stomatal control (p - sto) - Upper threshold",
        scale = 2
    ),
    "KsShapeFactorStomata" : _ContinuousCropParameter(
        name = "KsShapeFactorStomata",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Shape factor for water stress coefficient for stomatal control (0.0 = straight line)",
        scale = 1
    ),
    "pSenescence" : _ContinuousCropParameter(
        name = "pSenescence",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Soil water depletion factor for canopy senescence (p - sen) - Upper threshold",
        scale = 2
    ),
    "KsShapeFactorSenescence" : _ContinuousCropParameter(
        name = "KsShapeFactorSenescence",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Shape factor for water stress coefficient for canopy senescence (0.0 = straight line)",
        scale = 1
    ),
    "SumEToDelaySenescence" : _ContinuousCropParameter(
        name = "SumEToDelaySenescence",
        datatype = int,
        valid_range = [-math.inf, math.inf],
        description = "Sum(ETo) during dormant period to be exceeded before crop is permanently wilted"
    ),
    "pPollination" : _ContinuousCropParameter(
        name = "pPollination",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = (
            "Soil water depletion factor for pollination (p - pol) - Upper threshold",
            "Soil water depletion factor for pollination - Not Applicable"
        ),
        scale = 2,
        required = False,
        missing_value = -9
    ),
    "AnaeroPoint" : _ContinuousCropParameter(
        name = "AnaeroPoint",
        datatype = int,
        valid_range = [-math.inf, math.inf],
        description = "Vol% for Anaerobiotic point (* (SAT - [vol%]) at which deficient aeration occurs *)"
    ),
    # ################################# #
    # stress response                   #
    # ################################# #
    "Stress" : _ContinuousCropParameter(
        name = "Stress",
        datatype = int,
        valid_range = [-math.inf, math.inf],
        description = "Considered soil fertility stress for calibration of stress response (%)"
    ),
    "ShapeCGC" : _ContinuousCropParameter(
        name = "ShapeCGC",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = (
            "Shape factor for the response of canopy expansion to soil fertility stress",
            "Response of canopy expansion is not considered"
        ),
        scale = 2,
        required = False
    ),
    "ShapeCCX" : _ContinuousCropParameter(
        name = "ShapeCCX",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = (
            "Shape factor for the response of maximum canopy cover to soil fertility stress",
            "Response of maximum canopy cover is not considered"
        ),
        scale = 2,
        required = False
    ),
    "ShapeWP" : _ContinuousCropParameter(
        name = "ShapeWP",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = (
            "Shape factor for the response of crop Water Productivity to soil fertility stress",
            "Response of crop Water Productivity is not considered"
        ),
        scale = 2,
        required = False
    ),
    "ShapeCDecline" : _ContinuousCropParameter(
        name = "ShapeCDecline",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = (
            "Shape factor for the response of decline of canopy cover to soil fertility stress",
            "Response of decline of canopy cover is not considered"
        ),
        scale = 2,
        required = False
    ),
    # ################################# #
    # temperature stress                #
    # ################################# #
    "Tcold" : _ContinuousCropParameter(
        name = "Tcold",
        datatype = int,
        valid_range = (-math.inf, math.inf),
        description = (
            "Minimum air temperature below which pollination starts to fail (cold stress) (degC)",
            "Cold (air temperature) stress affecting pollination - not considered"
        ),
        required = False,
        missing_value = -9
    ),
    "Theat" : _ContinuousCropParameter(
        name = "Theat",
        datatype = int,
        valid_range = (-math.inf, math.inf),
        description = (
            "Maximum air temperature above which pollination starts to fail (heat stress) (degC)",
            "Heat (air temperature) stress affecting pollination - not considered"
        ),
        required = False,
        missing_value = -9
    ),
    "GDtranspLow" : _ContinuousCropParameter(
        name = "GDtranspLow",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = (
            "Minimum growing degrees required for full crop transpiration (degC - day)",
            "Cold (air temperature) stress on crop transpiration not considered"
        ),
        scale = 1,
        required = False,
        missing_value = -9
    ),
    # ################################# #
    # Salinity stress                   #
    # ################################# #
    "ECemin" : _ContinuousCropParameter(
        name = "ECemin",
        datatype = int,
        valid_range = (-math.inf, math.inf),
        description = "Electrical Conductivity of soil saturation extract at which crop starts to be affected by soil salinity (dS/m)",
    ),
    "ECemax" : _ContinuousCropParameter(
        name = "ECemax",
        datatype = int,
        valid_range = (-math.inf, math.inf),
        description = "Electrical Conductivity of soil saturation extract at which crop can no longer grow (dS/m)",
    ),                          # GOT UP TO HERE!!!
    "CCsaltDistortion" : _ContinuousCropParameter(
        name = "CCsaltDistortion",
        datatype = int,
        valid_range = (0, 100),
        description = "Calibrated distortion (%) of CC due to salinity stress (Range: 0 (none) to +100 (very strong))"
    ),
    "ResponseECsw" : _ContinuousCropParameter(
        name = "ResponseECsw",
        datatype = int,
        valid_range = (0, 200),
        description = "Calibrated response (%) of stomata stress to ECsw (Range: 0 (none) to +200 (extreme))"
    ),
    "KcTop" : _ContinuousCropParameter(
        name = "KcTop",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = "Crop coefficient when canopy is complete but prior to senescence (KcTr,x)",
        scale = 2
    ),
    # ################################# #
    # Evapotranspiration                #
    # ################################# #
    "KcDecline" : _ContinuousCropParameter(
        name = "KcDecline",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = "Decline of crop coefficient (%/day) as a result of ageing, nitrogen deficiency, etc.",
        scale = 3
    ),
    "RootMin" : _ContinuousCropParameter(
        name = "RootMin",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = "Minimum effective rooting depth (m)",
        scale = 2
    ),
    "RootMax" : _ContinuousCropParameter(
        name = "RootMax",
        datatype = float,
        valid_range = (0, math.inf),
        description = "Maximum effective rooting depth (m)",
        scale = 2
    ),
    "RootShape" : _ContinuousCropParameter(
        name = "RootShape",
        datatype = int,
        valid_range = (-math.inf, math.inf),
        description = "Shape factor describing root zone expansion"
    ),
    "SmaxTopQuarter" : _ContinuousCropParameter(
        name = "SmaxTopQuarter",
        datatype = float,
        valid_range = (0, math.inf),
        description = "Maximum root water extraction (m3water/m3soil.day) in top quarter of root zone",
        scale = 3
    ),
    "SmaxBotQuarter" : _ContinuousCropParameter(
        name = "SmaxBotQuarter",
        datatype = float,
        valid_range = (0, math.inf),
        description = "Maximum root water extraction (m3water/m3soil.day) in bottom quarter of root zone",
        scale = 3
    ),
    "CCEffectEvapLate" : _ContinuousCropParameter(
        name = "CCEffectEvapLate",
        datatype = int,
        valid_range = (-math.inf, math.inf),
        description = "Effect of canopy cover in reducing soil evaporation in late season stage"
    ),
    # ################################# #
    # Canopy development                #
    # ################################# #
    "SizeSeedling" : _ContinuousCropParameter(
        name = "SizeSeedling",
        datatype = float,
        valid_range = (0, math.inf),
        description = "Soil surface covered by an individual seedling at 90 % emergence (cm2)",
        scale = 2
    ),
    "SizePlant" : _ContinuousCropParameter(
        name = "SizePlant",
        datatype = float,
        valid_range = (0, math.inf),
        description = "Canopy size of individual plant (re-growth) at 1st day (cm2)",
        scale = 2
    ),
    "PlantingDens" : _ContinuousCropParameter(
        name = "PlantingDens",
        datatype = int,
        valid_range = (0, math.inf),
        description = "Number of plants per hectare"
    ),
    "CGC" : _ContinuousCropParameter(
        name = "CGC",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = "Canopy growth coefficient (CGC): Increase in canopy cover (fraction soil cover per day)",
        scale = 5
    ),
    "YearCCx" : _ContinuousCropParameter(
        name = "YearCCx",
        datatype = int,
        valid_range = (0, math.inf),
        description = (
            "Number of years at which CCx declines to 90 % of its value due to self-thinning - for Perennials",
            "Number of years at which CCx declines to 90 % of its value due to self-thinning - Not Applicable"
        ),
        required = False,
        missing_value = -9
    ),
    "CCxRoot" : _ContinuousCropParameter(
        name = "CCxRoot",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = (
            "Shape factor of the decline of CCx over the years due to self-thinning - for Perennials",
            "Shape factor of the decline of CCx over the years due to self-thinning - Not Applicable"
        ),
        scale = 2,
        required = False,
        missing_value = -9
    ),
    "CCx" : _ContinuousCropParameter(
        name = "CCx",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = "Maximum canopy cover (CCx) in fraction soil cover",
        scale = 2
    ),
    "CDC" : _ContinuousCropParameter(
        name = "CDC",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = "Canopy decline coefficient (CDC): Decrease in canopy cover (in fraction per day)",
        scale = 5
    ),
    "DaysToGermination" : _ContinuousCropParameter(
        name = "DaysToGermination",
        datatype = int,
        valid_range = (0, math.inf),
        description = {
            0: "Calendar Days: from sowing to emergence",
            1: "Calendar Days: from transplanting to recovered transplant",
            -9: "Calendar Days: from regrowth to recovering"
        },
        depends_on = ("Planting",)
    ),
    "DaysToMaxRooting" : _ContinuousCropParameter(
        name = "DaysToMaxRooting",
        datatype = int,
        valid_range = (0, math.inf),
        description = {
            0: "Calendar Days: from sowing to maximum rooting depth", # Sowing
            1: "Calendar Days: from transplanting to maximum rooting depth", # Transplant
            -9: "Calendar Days: from regrowth to maximum rooting depth"       # Regrowth
        },
        depends_on = ("Planting",)
    ),
    "DaysToSenescence" : _ContinuousCropParameter(
        name = "DaysToSenescence",
        datatype = int,
        valid_range = (0, math.inf),
        description = {
            0: "Calendar Days: from sowing to start senescence",
            1: "Calendar Days: from transplanting to start senescence",
            -9: "Calendar Days: from regrowth to start senescence"
        },
        depends_on = ("Planting",)
    ),
    "DaysToHarvest" : _ContinuousCropParameter(
        name = "DaysToHarvest",
        datatype = int,
        valid_range = (0, math.inf),
        description = {
            0: "Calendar Days: from sowing to maturity (length of crop cycle)",
            1: "Calendar Days: from transplanting to maturity",
            -9: "Calendar Days: from regrowth to maturity"
        },
        depends_on = ("Planting",)
    ),
    "DaysToFlowering" : _ContinuousCropParameter(
        name = "DaysToFlowering",
        datatype = int,
        valid_range = (0, math.inf),
        description = {
            0: {
                "default": "Calendar Days: from sowing to flowering",
                3: "Calendar Days: from sowing to start of yield formation"
            },
            1: {
                "default": "Calendar Days: from transplanting to flowering",
                3: "Calendar Days: from transplanting to yield formation"
            },
            -9: {
                "default": "Calendar Days: from regrowth to flowering",
                 3: "Calendar Days: from regrowth to yield formation"
            }
        },
        depends_on = ("Planting", "subkind")
    ),
    "LengthFlowering" : _ContinuousCropParameter(
        name = "LengthFlowering",
        datatype = int,
        valid_range = (0, math.inf),
        description = "Length of the flowering stage (days)"
    ),
    "DeterminancyLinked" : _DiscreteCropParameter(
        name = "DeterminancyLinked",
        valid_range = (0, 1),
        description = {
            0: "Crop determinancy unlinked with flowering",
            1: "Crop determinancy linked with flowering"
        }
    ),
    "fExcess" : _ContinuousCropParameter(
        name = "fExcess",
        datatype = int,
        valid_range = (0, 100),
        description = {
            "default": ("Excess of potential fruits (%)", "Excess of potential fruits - Not Applicable"),
            1: "Parameter NO LONGER required",
            4: "Parameter NO LONGER required"
        },
        depends_on = ("subkind",),
        required = False,
        missing_value = -9
    ),
    "DaysToHIo" : _ContinuousCropParameter(
        name = "DaysToHIo",
        datatype = int,
        valid_range = (0, math.inf),
        description = {
            1: (
                "Building up of Harvest Index starting at sowing/transplanting (days)",
                "Building up of Harvest Index - Not Applicable"
            ),
            2: (
                "Building up of Harvest Index starting at flowering (days)", # Grain
                "Building up of Harvest Index - Not Applicable"
            ),
            3: (
                "Building up of Harvest Index starting at root/tuber enlargement (days)", # Tuber
                "Building up of Harvest Index - Not Applicable"
            ),
            4: (
                "Building up of Harvest Index starting at sowing/transplanting (days)", # Vegetative/forage
                "Building up of Harvest Index - Not Applicable"
            ),
            "default": (
                "Building up of Harvest Index during yield formation (days)",
                "Building up of Harvest Index - Not Applicable"
            )
        },
        depends_on = ("subkind",),
        required = False
    ),
    "WP" : _ContinuousCropParameter(
        name = "WP",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = "Water Productivity normalized for ETo and CO2 (WP*) (gram/m2)",
        scale = 1
    ),
    "WPy" : _ContinuousCropParameter(
        name = "WPy",
        datatype = int,
        valid_range = (-math.inf, math.inf),
        description = "Water Productivity normalized for ETo and CO2 during yield formation (as % WP*)"
    ),
    "AdaptedToCO2" : _ContinuousCropParameter(
        name = "AdaptedToCO2",
        datatype = int,
        valid_range = (0, 100),
        description = "Crop performance under elevated atmospheric CO2 concentration (%)"
    ),
    "HI" : _ContinuousCropParameter(
        name = "HI",
        datatype = int,
        valid_range = (0, 100),
        description = "Reference Harvest Index (HIo) (%)"
    ),
    "HIincrease" : _ContinuousCropParameter(
        name = "HIincrease",
        datatype = int,
        valid_range = (0, 100),
        description = {
            "default" : "Possible increase (%) of HI due to water stress before flowering",
            3: "Possible increase (%) of HI due to water stress before start of yield formation"
        },
        depends_on = ("subkind",)
    ),
    "aCoeff" : _ContinuousCropParameter(
        name = "aCoeff",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = (
            "Coefficient describing positive impact on HI of restricted vegetative growth during yield formation",
            "No impact on HI of restricted vegetative growth during yield formation"
        ),
        scale = 1,
        required = False,
        missing_value = -9
    ),
    "bCoeff" : _ContinuousCropParameter(
        name = "bCoeff",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = (
            "Coefficient describing negative impact on HI of stomatal closure during yield formation",
            "No effect on HI of stomatal closure during yield formation"
        ),
        scale = 1,
        required = False,
        missing_value = -9
    ),
    "DHImax" : _ContinuousCropParameter(
        name = "DHImax",
        datatype = int,
        valid_range = (0, 100),
        description = "Allowable maximum increase (%) of specified HI"
    ),
    "GDDaysToGermination" : _ContinuousCropParameter(
        name = "GDDaysToGermination",
        datatype = int,
        valid_range = (-math.inf, math.inf),
        description = {
            0: "GDDays: from sowing to emergence",
            1: "GDDays: from transplanting to recovered transplant",
            -9: "GDDays: from regrowth to recovering"
        },
        depends_on = ("Planting",),
        required = False,
        missing_value = -9
    ),
    "GDDaysToMaxRooting" : _ContinuousCropParameter(
        name = "GDDaysToMaxRooting",
        datatype = int,
        valid_range = (-math.inf, math.inf),
        description = {
            0: "GDDays: from sowing to maximum rooting depth",
            1: "GDDays: from transplanting to maximum rooting depth",
            -9: "GDDays: from regrowth to maximum rooting depth"
        },
        depends_on = ("Planting",),
        required = False,
        missing_value = -9
    ),
    "GDDaysToSenescence" : _ContinuousCropParameter(
        name = "GDDaysToSenescence",
        datatype = int,
        valid_range = (-math.inf, math.inf),
        description = {
            0: "GDDays: from sowing to start senescence",
            1: "GDDays: from transplanting to start senescence",
            -9: "GDDays: from regrowth to start senescence"
        },
        depends_on = ("Planting",),
        required = False,
        missing_value = -9
    ),
    "GDDaysToHarvest" : _ContinuousCropParameter(
        name = "GDDaysToHarvest",
        datatype = int,
        valid_range = (-math.inf, math.inf),
        description = {
            0: "GDDays: from sowing to maturity (length of crop cycle)",
            1: "GDDays: from transplanting to maturity",
            -9: "GDDays: from regrowth to maturity"
        },
        depends_on = ("Planting",),
        required = False,
        missing_value = -9
    ),
    "GDDaysToFlowering" : _ContinuousCropParameter(
        name = "GDDaysToFlowering",
        datatype = int,
        valid_range = (-math.inf, math.inf),
        description = {
            0: {
                "default": "GDDays: from sowing to flowering",
                3: "GDDays: from sowing to start yield formation",
            },
            1: {
                "default": "GDDays: from transplanting to flowering",
                3: "GDDays: from sowing to start yield formation"
            },
            -9: {
                "default": "GDDays: from regrowth to flowering",
                3: "GDDays: from regrowth to start yield formation"
            }
        },
        depends_on = ("Planting", "subkind"),
        required = False,
        missing_value = -9
    ),
    "GDDLengthFlowering" : _ContinuousCropParameter(
        name = "GDDLengthFlowering",
        datatype = int,
        valid_range = (0, math.inf),
        description = "Length of the flowering stage (growing degree days)",
        required = False,
        missing_value = -9
    ),
    "GDDCGC" : _ContinuousCropParameter(
        name = "GDDCGC",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = "CGC for GGDays: Increase in canopy cover (in fraction soil cover per growing-degree day)",
        scale = 6,
        required = False,
        missing_value = -9
    ),
    "GDDCDC" : _ContinuousCropParameter(
        name = "GDDCDC",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = "CDC for GGDays: Decrease in canopy cover (in fraction per growing-degree day)",
        scale = 6,
        required = False,
        missing_value = -9
    ),
    "GDDaysToHIo" : _ContinuousCropParameter(
        name = "GDDaysToHIo",
        datatype = int,
        valid_range = (0, math.inf),
        description = "GDDays: building-up of Harvest Index during yield formation",
        required = False,
        missing_value = -9
    ),
    "DryMatter" : _ContinuousCropParameter(
        name = "DryMatter",
        datatype = int,
        valid_range = (0, 100),
        description = "dry matter content (%) of fresh yield"
    ),
    "RootMinYear1" : _ContinuousCropParameter(
        name = "RootMinYear1",
        datatype = float,
        valid_range = (0, math.inf),
        description = {
            4: "Minimum effective rooting depth (m) in first year (for perennials)", # Forage
            "default": "Minimum effective rooting depth (m) in first year - required only in case of regrowth"
        },
        scale = 2,
        depends_on = ("subkind",)
    ),
    "SownYear1" : _DiscreteCropParameter(
        name = "SownYear1",
        valid_range = (0, 1),
        description = {
            4: {
                1: "Crop is sown in 1st year (for perennials)",
                0: "Crop is transplanted in 1st year (for perennials)"
            },
            "default": {
                1: "Crop is sown in 1st year - required only in the case of regrowth",
                0: "Crop is transplanted in 1st year - required only in the case of regrowth"
            }
        },
        depends_on = ("subkind",)
    ),
    "Assimilates_On" : _DiscreteCropParameter(
        name = "Assimilates_On",
        valid_range = (0, 1),
        description = {
            0 : "Transfer of assimilates from above ground parts to root system is NOT considered",
            1 : "Transfer of assimilates from above ground parts to root system is considered"
        }
    ),
    "Assimilates_Period" : _DiscreteCropParameter(
        name = "Assimilates_On",
        valid_range = (0, 1),
        description = {
            0 : "Number of days at end of season during which assimilates are stored in root system",
            1 : "Number of days at end of season during which assimilates are stored in root system"
        }
    ),
    "Assimilates_Stored" : _DiscreteCropParameter(
        name = "Assimilates_On",
        valid_range = (0, 1),
        description = {
            0 : "Percentage of assimilates transferred to root system at last day of season",
            1 : "Percentage of assimilates transferred to root system at last day of season"
        }
    ),
    "Assimilates_Mobilized" : _DiscreteCropParameter(
        name = "Assimilates_On",
        valid_range = (0, 1),
        description = {
            0 : "Percentage of stored assimilates transferred to above ground parts in next season",
            1 : "Percentage of stored assimilates transferred to above ground parts in next season"
        }
    )
}

ONSET_CROP_PARAMETER_DICT = {
    "GenerateOnset" : _DiscreteCropParameter(
        name = "GenerateOnset",
        valid_range = (0, 12, 13),
        description = {
            0: "Onset fixed on a specific day",
            12: "Criterion: mean air temperature",
            13: "Criterion: growing-degree days"
        }
    ),
    "OnsetFirstDay" : _ContinuousCropParameter(
        name = "OnsetFirstDay",
        datatype = int,
        valid_range = (0, math.inf),
        description = "First Day for the time window (Restart of growth)"
    ),
    "OnsetFirstMonth" : _ContinuousCropParameter(
        name = "OnsetFirstMonth",
        datatype = int,
        valid_range = (0, math.inf),
        description = "First Month for the time window (Restart of growth)"
    ),
    "OnsetLengthSearchPeriod" : _ContinuousCropParameter(
        name = "OnsetLengthSearchPeriod",
        datatype = int,
        valid_range = (0, math.inf),
        description = "Length (days) of the time window (Restart of growth)"
    ),
    "OnsetThresholdValue" : _ContinuousCropParameter(
        name = "OnsetThresholdValue",
        datatype = float,
        valid_range = (0, math.inf),
        description = "Threshold for the Restart criterion: Growing-degree days",
        scale = 1
    ),
    "OnsetPeriodValue" : _ContinuousCropParameter(
        name = "OnsetPeriodValue",
        datatype = int,
        valid_range = (0, math.inf),
        description = "Number of successive days for the Restart criterion"
    ),
    "OnsetOccurrence" : _ContinuousCropParameter(
        name = "OnsetOccurrence",
        datatype = int,
        valid_range = (0, math.inf),
        description = "Number of occurrences before the Restart criterion applies"
    ),
    "GenerateEnd" : _DiscreteCropParameter(
        name = "GenerateEnd",
        valid_range = (),
        description = {
            0: "End is fixed on a specific day",
            62: "Criterion: mean air temperature",
            63: "Criterion: growing-degree days"
        }
    ),
    "EndLastDay" : _ContinuousCropParameter(
        name = "EndLastDay",
        datatype = int,
        valid_range = (0, math.inf),
        description = "Last Day for the time window (End of growth)"
    ),
    "EndLastMonth" : _ContinuousCropParameter(
        name = "EndLastMonth",
        datatype = int,
        valid_range = (0, math.inf),
        description = "Last Month for the time window (End of growth)"
    ),
    "ExtraYears" : _ContinuousCropParameter(
        name = "ExtraYears",
        datatype = int,
        valid_range = (0, math.inf),
        description = "Number of years to add to the Onset year"
    ),
    "EndLengthSearchPeriod" : _ContinuousCropParameter(
        name = "EndLengthSearchPeriod",
        datatype = int,
        valid_range = (0, math.inf),
        description = "Length (days) of the time window (End of growth)"
    ),
    "EndThresholdValue" : _ContinuousCropParameter(
        name = "EndThresholdValue",
        datatype = int,
        valid_range = (0, math.inf),
        description = "Threshold for the End criterion: Growing-degree days",
        scale = 1
    ),
    "EndPeriodValue" : _ContinuousCropParameter(
        name = "EndPeriodValue",
        datatype = int,
        valid_range = (0, math.inf),
        description = "Number of successive days for the End criterion"
    ),
    "EndOccurrence" : _ContinuousCropParameter(
        name = "EndOccurrence",
        datatype = int,
        valid_range = (0, math.inf),
        description = "Number of occurrences before the End criterion applies"
    )
}

CROP_PARAMETER_ORDER = (
    "subkind",
    "Planting",
    "ModeCycle",
    "pMethod",
    "Tbase",
    "Tupper",
    "GDDaysToHarvest0",
    "pLeafDefUL",
    "pLeafDefLL",
    "KsShapeFactorLeaf",
    "pdef",
    "KsShapeFactorStomata",
    "pSenescence",
    "KsShapeFactorSenescence",
    "SumEToDelaySenescence",
    "pPollination",
    "AnaeroPoint",
    "Stress",
    "ShapeCGC",
    "ShapeCCX",
    "ShapeWP",
    "ShapeCDecline",
    None,
    "Tcold",
    "Theat",
    "GDtranspLow",
    "ECemin",
    "ECemax",
    None,
    "CCsaltDistortion",
    "ResponseECsw",
    "KcTop",
    "KcDecline",
    "RootMin",
    "RootMax",
    "RootShape",
    "SmaxTopQuarter",
    "SmaxBotQuarter",
    "CCEffectEvapLate",
    "SizeSeedling",
    "SizePlant",
    "PlantingDens",
    "CGC",
    "YearCCx",
    "CCxRoot",
    None,
    "CCx",
    "CDC",
    "DaysToGermination",
    "DaysToMaxRooting",
    "DaysToSenescence",
    "DaysToHarvest",
    "DaysToFlowering",
    "LengthFlowering",
    "DeterminancyLinked",
    "fExcess",
    "DaysToHIo",
    "WP",
    "WPy",
    "AdaptedToCO2",
    "HI",
    "HIincrease",
    "aCoeff",
    "bCoeff",
    "DHImax",
    "GDDaysToGermination",
    "GDDaysToMaxRooting",
    "GDDaysToSenescence",
    "GDDaysToHarvest",
    "GDDaysToFlowering",
    "GDDLengthFlowering",
    "GDDCGC",
    "GDDCDC",
    "GDDaysToHIo",
    "DryMatter",
    "RootMinYear1",
    "SownYear1",
    "Assimilates_On",
    "Assimilates_Period",
    "Assimilates_Stored",
    "Assimilates_Mobilized",
)

ONSET_CROP_PARAMETER_ORDER = (
    "GenerateOnset",
    "OnsetFirstDay",
    "OnsetFirstMonth",
    "OnsetLengthSearchPeriod",
    "OnsetThresholdValue",
    "OnsetPeriodValue",
    "OnsetOccurrence",
    "GenerateEnd",
    "EndLastDay",
    "EndLastMonth",
    "ExtraYears",
    "EndLengthSearchPeriod",
    "EndThresholdValue",
    "EndPeriodValue",
    "EndOccurrence"
)

CROP_TYPES = (
    "Barley",
    "Cotton",
    "DryBean",
    "Maize",
    "PaddyRice",
    "Potato",
    "Quinoa",
    "Sorghum",
    "Soybean",
    "SugarBeet",
    "SugarCane",
    "Sunflower",
    "Tef",
    "Tomato",
    "Wheat"
)

GDD_CROP_TYPES = (
    "AlfalfaGDD",
    "BarleyGDD",
    "CottonGDD",
    "DryBeanGDD",
    "MaizeGDD",
    "PaddyRiceGDD",
    "PotatoGDD",
    "SorghumGDD",
    "SoybeanGDD",
    "SugarBeetGDD",
    "SunflowerGDD",
    "TomatoGDD",
    "WheatGDD"
)

# This should perhaps inherit dictionary with an additional write method
class CropParameterSet:
    # Make these constants that exist outside class
    CROP_PARAMETERS = CROP_PARAMETER_DICT
    ONSET_CROP_PARAMETERS = ONSET_CROP_PARAMETER_DICT
    CROP_PARAMETER_ORDER = CROP_PARAMETER_ORDER
    ONSET_CROP_PARAMETER_ORDER = ONSET_CROP_PARAMETER_ORDER
    DEFAULT_CROP_PARAMETERS = _load_default_data()
    VALID_CROP_TYPES = CROP_TYPES + GDD_CROP_TYPES
    def __init__(self,
                 crop_name):

        # Check crop_name is valid
        self.crop_name = crop_name
        if self.crop_name not in self.VALID_CROP_TYPES:
            raise ValueError("Hello, world")

        self._default_parameter_set = self.DEFAULT_CROP_PARAMETERS[crop_name]
        self.crop_name = crop_name
        self.crop_parameter_names = tuple(self.CROP_PARAMETERS.keys())
        # Now that we have verified the crop type, pull default values
        self.set_default_values()
        # self.update_value_descriptions()

    def set_default_values(self):
        for _, param_obj in self.CROP_PARAMETERS.items():
            param_obj.set_default_value(
                self._default_parameter_set[param_obj.name]
            )
        self.update_planting()
        self.update_subkind()

        if self.subkind == 4:
            for _, param_obj in self.ONSET_CROP_PARAMETERS.items():
                param_obj.set_default_value(
                    self._default_parameter_set[param_obj.name]
                )

        self.update_value_descriptions()

    def update_value_descriptions(self):
        if self.subkind == 4:
            param_dict = {**self.CROP_PARAMETERS, **self.ONSET_CROP_PARAMETERS}
        else:
            param_dict = self.CROP_PARAMETERS

        for _, param_obj in param_dict.items():
            # param_obj.set_default_value(
            #     self._default_parameter_set[param_obj.name]
            # )
            param_obj.set_value_description(
                self.planting, self.subkind
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
        self.planting = self.CROP_PARAMETERS['Planting'].value

    def update_subkind(self):
        self.subkind = self.CROP_PARAMETERS['subkind'].value

    def get_str_format(self, name):
        return self.CROP_PARAMETERS[name].str_format

    @property
    def default_header(self):
        return 'Crop %s file' % self.crop_name

    def write(self, filename, header = None):
        if header is None:
            header = self.default_header
        version = _format_crop_parameter(AQUACROP_VERSION)
        protected = _format_crop_parameter('0')
        with open(filename, 'w') as f:
            f.write(header + os.linesep)
            f.write(version + ' : AquaCrop Version' + os.linesep)
            f.write(protected + ' : File protected' + os.linesep)
            for param in self.CROP_PARAMETER_ORDER:
                if param is not None:
                    description = self.CROP_PARAMETERS[param].value_description
                    num = self.CROP_PARAMETERS[param].str_format
                else:
                    description = 'dummy - no longer applicable'
                    num = _format_crop_parameter('-9')
                f.write(num + ' : ' + description + os.linesep)

            if self.subkind == 4:
                # Add internal crop calendar
                f.write(os.linesep)
                f.write(" Internal crop calendar" + os.linesep)
                f.write(" ======================" + os.linesep)
                for param in self.ONSET_CROP_PARAMETER_ORDER:
                    if param is not None:
                        description = self.ONSET_CROP_PARAMETERS[param].value_description
                        num = self.ONSET_CROP_PARAMETERS[param].str_format
                    else:
                        description = 'dummy - no longer applicable'
                        num = _format_crop_parameter('-9')
                    f.write(num + ' : ' + description + os.linesep)
