#!/usr/bin/env python3

import os
import math
from typing import Dict, Optional, Union, Tuple
from abc import ABC, abstractmethod, abstractproperty

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


class Parameter(ABC):

    @abstractmethod
    def set_value(self):
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
                 depends_on: Optional[str] = None,
                 scale: Optional[int] = 2,
                 required: bool = True):

        self.value = None
        self.name = name
        self.datatype = datatype
        self.discrete = discrete
        self.valid_range = valid_range
        self.description = description
        self.depends_on = depends_on
        self.scale = scale
        self.required = optional

    def set_value(self, value):
        self.value = value

    @property
    def name(self):
        pass

    @property
    def description(self, **kwargs):
        if discrete:
            return self.description[self.value]
        else:
            return self.description

    @property
    def default_value(self):
        pass

    @property
    def valid_range(self):
        return self.valid_range

    @property
    def str_format(self):
        pass

class _DiscreteCropParameter(_CropParameter):
    def __init__(self,
                 name: str,
                 description: dict,
                 depends_on: Optional[str] = None,
                 required: bool = True):

        super(_DiscreteCropParameter, self).__init__(
            name = name,
            datatype = int,
            discrete = True,
            valid_range = (int(key) for key in description.keys()),
            description = description
            depends_on = depends_on
            required = required
        )

class _ContinuousCropParameter(_CropParameter):
    def __init__(self,
                 name: str,
                 datatype: type,
                 valid_range: list,
                 description: Union[str, tuple],
                 scale: Optional[int] = 2,
                 required = True):

        super(_ContinuousCropParameter, self).__init__(
            name = name,
            datatype = datatype,
            discrete = False,
            valid_range = valid_range,
            description = description,
            depends_on = None,
            scale = scale,
            required = required
        )

class _OptionalContinuousCropParameter(_CropParameter):
    def __init__(self,
                 name: str,
                 datatype: type,
                 valid_range: list,
                 description: Union[str, tuple],
                 scale: Optional[int] = 2):

        super(_ContinuousCropParameter, self).__init__(
            name = name,
            datatype = datatype,
            discrete = False,
            valid_range = valid_range,
            description = description,
            depends_on = None,
            scale = scale,
            required = False
        )
# The idea here is to have a dictionary of all crop parameters which can then be organised properly in a CropParameterDict class

CROP_PARAMETER_DICT = {
    "subkind" : _DiscreteCropParameter(
        name = "subkind",
        description = {
            1: "leafy vegetable crop",
            2: "fruit/grain producing crop",
            3: "root/tuber crop",
            4: "forage_crop"
        }
    ),
    "Planting" : _DiscreteCropParameter(
        name = "Planting",
        description = {
            0: "Crop is sown",
            1: "Crop is transplanted",
            -9: "Crop is regrowth"
        },
    ),
    "ModeCycle" : _DiscreteCropParameter(
        name = "ModeCycle",
        description = {
            0 : "Determination of crop cycle: by growing-degree days",
            1 : "Determination of crop cycle: by calendar days"
        }
    ),
    "pMethod" : _DiscreteCropParameter(
        name = "pMethod",
        description = {
            0: "No adjustment by ETo of soil water depletion factors (p)",
            1: "Soil water depletion factors (p) are adjusted by ETo",
        }
    ),
    "Tbase" : _ContinuousCropParameter(
        name = "Tbase",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Base temperature (degC) below which crop development does not progress",
        scale = 2
    ),
    "Tupper" : _ContinuousCropParameter(
        name = "Tupper",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description =  "Upper temperature (degC) above which crop development no longer increases with an increase in temperature",
        scale = 2
    },
    "GDDaysToHarvest"  = _ContinuousCropParameter(
        name = "GDDaysToHarvest",
        datatype = int,
        valid_range = [-math.inf, math.inf],
        description = "Total length of crop cycle in growing degree-days"
    },
    "pLeafDefUL" = _ContinuousCropParameter(
        name = "pLeafDefUL",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Soil water depletion factor for canopy expansion (p-exp) - Upper threshold",
        scale = 2
    ),
    "pLeafDefLL" : _ContinuousCropParameter(
        name = "pLeafDefLL",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Soil water depletion factor for canopy expansion (p-exp) - Lower threshold",
        scale = 2
    },
    "KsShapeFactorLeaf" : _ContinuousCropParameter(
        name = "KsShapeFactorLeaf",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Shape factor for water stress coefficient for canopy expansion (0.0 = straight line)",
        scale = 1
    },
    "pdef" : _ContinuousCropParameter(
        name = "pdef",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Soil water depletion fraction for stomatal control (p - sto) - Upper threshold",
        scale = 2
    },
    "KsShapeFactorStomata" : _ContinuousCropParameter(
        name = "KsShapeFactorStomata"
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Shape factor for water stress coefficient for stomatal control (0.0 = straight line)",
        scale = 1
    },
    "pSenescence" : _ContinuousCropParameter(
        name = "pSenescence",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Soil water depletion factor for canopy senescence (p - sen) - Upper threshold",
        scale = 2
    },
    "KsShapeFactorSenescence" : _ContinuousCropParameter(
        name = "KsShapeFactorSenescence",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Shape factor for water stress coefficient for canopy senescence (0.0 = straight line)",
        scale = 1
    },
    "SumEToDelaySenescence" : _ContinuousCropParameter(
        name = "SumEToDelaySenescence",
        datatype = int,
        valid_range = [-math.inf, math.inf],
        description = "Sum(ETo) during dormant period to be exceeded before crop is permanently wilted"
    },
    "pPollination" : _ContinuousCropParameter(
        name = "pPollination",
        datatype = float,
        valid_range = [-math.inf, math.inf],
        description = "Soil water depletion factor for pollination (p - pol) - Upper threshold",
        scale = 2
    },
    "AnaeroPoint" : _ContinuousCropParameter(
        name = "AnaeroPoint",
        datatype = int,
        valid_range = [-math.inf, math.inf],
        description = "Vol% for Anaerobiotic point (* (SAT - [vol%]) at which deficient aeration occurs *)"
    ),
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
        "description" = (
            "Shape factor for the response of decline of canopy cover to soil fertility stress",
            "Response of decline of canopy cover is not considered"
        ),
        scale = 2,
        required = False
    ),
    "Tcold" : _ContinuousCropParameter(
        name = "Tcold",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = (
            "Minimum air temperature below which pollination starts to fail (cold stress) (degC)",
            "Cold (air temperature) stress affecting pollination - not considered"
        ),
        scale = 1,              # FAO version has this as integer
        required = False
    ),
    "Theat" : _ContinuousCropParameter(
        name = "Theat",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = (
            "Maximum air temperature above which pollination starts to fail (heat stress) (degC)",
            "Heat (air temperature) stress affecting pollination - not considered"
        ),
        scale = 1,              # FAO version has this as integer
        required = False
    ),
    "GDtranspLow" : _ContinuousCropParameter(
        name = "GDtranspLow",
        datatype = float,
        valid_range = (0., math.inf),
        description = (
            "Minimum growing degrees required for full crop transpiration (degC - day)",
            "Cold (air temperature) stress on crop transpiration not considered"
        ),
        scale = 1,
        required = False
    },
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
    ),
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
        shape = 2
    ),
    "KcDecline" : _ContinuousCropParameter(
        name = "KcDecline",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = "Decline of crop coefficient (%/day) as a result of ageing, nitrogen deficiency, etc.",
        shape = 3
    ),
    "RootMin" : _ContinuousCropParameter(
        name = "RootMin",
        datatype = float,
        valid_range = (-math.inf, math.inf),
        description = "Minimum effective rooting depth (m)",
        shape = 2
    ),
    "RootMax" : _ContinuousCropParameter(
        name = "RootMax",
        datatype = float,
        valid_range : (-math.inf, math.inf),
        description = "Maximum effective rooting depth (m)",
        scale = 2
    ),
    "RootShape" : _ContinuousCropParameter(
        name = "RootShape",
        datatype = int,
        valid_range = (-math.inf, math.inf),
        description = "Shape factor describing root zone expansion"
    ),
    "SmaxTopQuarter" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Maximum root water extraction (m3water/m3soil.day) in top quarter of root zone",
        "format" : "{:0.3f}"
    },
    "SmaxBotQuarter" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Maximum root water extraction (m3water/m3soil.day) in bottom quarter of root zone",
        "format" : "{:0.3f}"
    },
    "CCEffectEvapLate" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Effect of canopy cover in reducing soil evaporation in late season stage",
        "format" : "{:0d}"
    },
    "SizeSeedling" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Soil surface covered by an individual seedling at 90 % emergence (cm2)",
        "format" : "{:0.2f}"
    },
    "SizePlant" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Canopy size of individual plant (re-growth) at 1st day (cm2)",
        "format" : "{:0.2f}"
    },
    "PlantingDens" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Number of plants per hectare",
        "format" : "{:0d}"
    },
    "CGC" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Canopy growth coefficient (CGC): Increase in canopy cover (fraction soil cover per day)",
        "format" : "{:0.5f}"
    },
    "YearCCx" : {
        "type" : 2,
        "required" : True,      # OR some kind of dictionary? e.g. {subkind : [4]}
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Number of years at which CCx declines to 90 % of its value due to self-thinning - for Perennials",
            "Number of years at which CCx declines to 90 % of its value due to self-thinning - Not Applicable"
        ],
        "format" : "{:0d}"
    },
    "CCxRoot" : {
        "type" : 2,
        "required" : True,
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Shape factor of the decline of CCx over the years due to self-thinning - for Perennials",
            "Shape factor of the decline of CCx over the years due to self-thinning - Not Applicable"
        ],
        "format" : "{:0.2f}"
    },
    None,
    "CCx" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Maximum canopy cover (CCx) in fraction soil cover",
        "format" : "{:0.2f}"
    },
    "CDC" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Canopy decline coefficient (CDC): Decrease in canopy cover (in fraction per day)",
        "format" : "{:0.5f}"
    },
    "DaysToGermination" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "valid_range" : [-math.inf, math.inf],
        "type" : ""
        "description" : {
            0: "Calendar Days: from sowing to emergence", # Sowing
            1: "Calendar Days: from transplanting to recovered transplant" # Transplant
            -9: "Calendar Days: from regrowth to recovering"                # Regrowth
        },
        "format" : "{:0d}"
    },
    "DaysToMaxRooting" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "Calendar Days: from sowing to maximum rooting depth", # Sowing
            1: "Calendar Days: from transplanting to maximum rooting depth", # Transplant
            -9: "Calendar Days: from regrowth to maximum rooting depth"       # Regrowth
        },
        "format" : "{:0d}"
    },
    "DaysToSenescence" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "Calendar Days: from sowing to start senescence",
            1: "Calendar Days: from transplanting to start senescence",
            -9: "Calendar Days: from regrowth to start senescence"
        },
        "format" : "{:0d}"
    },
    "DaysToHarvest" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "Calendar Days: from sowing to maturity (length of crop cycle)",
            1: "Calendar Days: from transplanting to maturity",
            -9: "Calendar Days: from regrowth to maturity"
        },
        "format" : "{:0d}"
    },
    "DaysToFlowering" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "Calendar Days: from sowing to flowering (or yield formation if subkind is Tuber)",
            1: "Calendar Days: from transplanting to flowering (or yield formation if subkind is Tuber)",
            -9: "Calendar Days: from regrowth to flowering (or yield formation if subkind is Tuber)"
        },
        "format" : "{:0d}"
    },
    "LengthFlowering" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Length of the flowering stage (days)",
        "format" : "{:0d}"
    },
    "DeterminancyLinked" : {
        "type" : 1,
        "valid_range" : [0, 1],
        "description" : {
            0: "Crop determinancy unlinked with flowering",
            1: "Crop determinancy linked with flowering"
        },
        "format" : "{:0d}"
    },
    "fExcess" : {
        "type" : 2,
        "valid_range" : [0, 100],
        "description" : "Excess of potential fruits (%)",
        "format" : "{:0d}"
    },
    "DaysToHIo" : {
        "type" : 2,
        "valid_range" : [0, math.inf],
        "description" : [
            "Building up of Harvest Index starting at sowing/transplanting (days)", # Vegetative/forage
            "Building up of Harvest Index starting at flowering (days)", # Grain
            "Building up of Harvest Index starting at root/tuber enlargement (days)", # Tuber
            "Building up of Harvest Index during yield formation (days)" # Default
        ],
        "format" : "{:0d}"
    },
    "WP" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Water Productivity normalized for ETo and CO2 (WP*) (gram/m2)",
        "format" : "{:0.1f}"
    },
    "WPy" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Water Productivity normalized for ETo and CO2 during yield formation (as % WP*)",
        "format" : "{:0d}"
    },
    "AdaptedToCO2" : {
        "type" : 2,
        "valid_range" : [0, 100],
        "description" : "Crop performance under elevated atmospheric CO2 concentration (%)",
        "format" : "{:0d}"
    },
    "HI" : {
        "type" : 2,
        "valid_range" : [0, 100],
        "description" : "Reference Harvest Index (HIo) (%)",
        "format" : "{:0d}"
    },
    "HIincrease" : {
        "type" : 2,
        "valid_range" : [0, 100],
        "description" : "Possible increase (%) of HI due to water stress before flowering (or yield formation if subkind is Tuber)",
        "format" : "{:0d}"
    },
    "aCoeff" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Coefficient describing positive impact on HI of restricted vegetative growth during yield formation",
            "No impact on HI of restricted vegetative growth during yield formation"
        ],
        "format" : "{:0.1f}"
    },
    "bCoeff" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Coefficient describing negative impact on HI of stomatal closure during yield formation",
            "No effect on HI of stomatal closure during yield formation"
        ],
        "format" : "{:0.1f}"
    },
    "DHImax" : {
        "type" : 2,
        "valid_range" : [0, 100],
        "description" : "Allowable maximum increase (%) of specified HI",
        "format" : "{:0d}"
    },
    "GDDaysToGermination" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : {
            0: "GDDays: from sowing to emergence",
            1: "GDDays: from transplanting to recovered transplant",
            -9: "GDDays: from regrowth to recovering"
        },
        "format" : "{:0d}"
    },
    "GDDaysToMaxRooting" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "GDDays: from sowing to maximum rooting depth",
            1: "GDDays: from transplanting to maximum rooting depth",
            -9: "GDDays: from regrowth to maximum rooting depth"
        },
        "format" : "{:0d}"
    },
    "Senescence" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "GDDays: from sowing to start senescence",
            1: "GDDays: from transplanting to start senescence",
            -9: "GDDays: from regrowth to start senescence"
        },
        "format" : "{:0d}"
    },
    "Harvest" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "GDDays: from sowing to maturity (length of crop cycle)",
            1: "GDDays: from transplanting to maturity",
            -9: "GDDays: from regrowth to maturity"
        },
        "format" : "{:0d}"
    },
    "GDDaysToFlowering" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "GDDays: from sowing to flowering (or yield formation if subkind is Tuber)",
            1: "GDDays: from transplanting to flowering (or yield formation if subkind is Tuber)",
            -9: "GDDays: from regrowth to flowering (or yield formation if subkind is Tuber)"
        },
        "format" : "{:0d}"
    },
    "GDDLengthFlowering" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Length of the flowering stage (growing degree days)",
        "format" : "{:0d}"
    },
    "GDDCGC" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "CGC for GGDays: Increase in canopy cover (in fraction soil cover per growing-degree day)",
        "format" : "{:0.6f}"
    },
    "GDDCDC" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "CDC for GGDays: Decrease in canopy cover (in fraction per growing-degree day)",
        "format" : "{:0.6f}"
    },
    "GDDaysToHIo" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "GDDays: building-up of Harvest Index during yield formation",
        "format" : "{:0d}"
    },
    "DryMatter" : {
        "type" : 2,
        "valid_range" : [0, 100],
        "description" : "dry matter content (%) of fresh yield",
        "format" : "{:0d}"
    },
    "RootMinYear1" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Minimum effective rooting depth (m) in first year (for perennials)", # Forage
            "Minimum effective rooting depth (m) in first year - required only in case of regrowth" # Regrowth
        ],
        "format" : "{:0.2f}"
    },
    "SownYear1" : {
        "type" : 1,
        "required" : True,
        "valid_range" : [0, 1]
        "description" : {
            1 : [
                "Crop is sown in 1st year (for perennials)",
                "Crop is sown in 1st year - required only in case of regrowth"
            ],
            0 : [
                "Crop is transplanted in 1st year (for perennials)",
                "Crop is transplanted in 1st year - required only in case of regrowth"
            ]
        },
        "format" : "{:0d}"
    },
    "Assimilates_On" : {
        "type" : 1,
        "valid_range" : [0, 1],
        "description" : {
            0 : "Transfer of assimilates from above ground parts to root system is NOT considered",
            1 : "Transfer of assimilates from above ground parts to root system is considered"
        },
        "format" : "{:0d}"
    },
    "Assimilates_Period" : {
        "type" : 1,
        "valid_range" : [0, 1],
        "description" : {
            0 : "Number of days at end of season during which assimilates are stored in root system",
            1 : "Number of days at end of season during which assimilates are stored in root system"
        },
        "format" : "{:0d}"
    },
    "Assimilates_Stored" : {
        "type" : 1,
        "valid_range" : [0, 1],
        "description" : {
            0 : "Percentage of assimilates transferred to root system at last day of season",
            1 : "Percentage of assimilates transferred to root system at last day of season"
        },
        "format" : "{:0d}"
    },
    "Assimilates_Mobilized" : {
        "type" : 1,
        "valid_range" : [0, 1],
        "description" : {
            0 : "Percentage of stored assimilates transferred to above ground parts in next season",
            1 : "Percentage of stored assimilates transferred to above ground parts in next season"
        },
        "format" : "{:0d}"
    }
}

# Define some types which determine how to get default values/descrptions etc.
# 1 - discrete
# 2 - continuous
CROP_PARAMETER_DICT = {
    "subkind" : {
        "datatype" : int,
        "discrete" : True,
        "depends_on" : None,
        "valid_range" : [1, 2, 3, 4],
        "description" : {
            1: "leafy vegetable crop",
            2: "fruit/grain producing crop",
            3: "root/tuber crop",
            4: "forage_crop"
        },
        "format" : "{:0d}"
    },
    "Planting" : {
        "datatype" : int,
        "discrete" : True,
        "depends_on" : None,
        "valid_range" : [0, 1, -9],
        "description" : {
            0: "Crop is sown",
            1: "Crop is transplanted",
            -9: "Crop is regrowth"
        },
        "format" : "{:0d}"
    },
    "ModeCycle" : {
        "datatype" : int,
        "discrete" : True,
        "depends_on" : None,
        "valid_range" : [0, 1],
        "description" : {
            0 : "Determination of crop cycle: by growing-degree days",
            1 : "Determination of crop cycle: by calendar days"
        },
        "format" : "{:0d}"
    },
    "pMethod" : {
        "datatype" : int,
        "discrete" : True,
        "depends_on" : None,
        "valid_range" : [0, 1],
        "description" : {
            0: "No adjustment by ETo of soil water depletion factors (p)",
            1: "Soil water depletion factors (p) are adjusted by ETo",
        },
        "format" : "{:0d}"
    },
    "Tbase" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Base temperature (degC) below which crop development does not progress",
        "format" : "{:0.2f}"
    },
    "Tupper" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Upper temperature (degC) above which crop development no longer increases with an increase in temperature",
        "format" : "{:0.2f}"
    },
    "GDDaysToHarvest" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Total length of crop cycle in growing degree-days",
        "format" : "{:0d}"
    },
    "pLeafDefUL" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Soil water depletion factor for canopy expansion (p-exp) - Upper threshold",
        "format" : "{:0.2f}"
    },
    "pLeafDeLL" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Soil water depletion factor for canopy expansion (p-exp) - Lower threshold",
        "format" : "{:0.2f}"
    },
    "KsShapeFactorLeaf" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Shape factor for water stress coefficient for canopy expansion (0.0 = straight line)"
        "format" : "{:0.1f}"
    },
    "pdef" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Soil water depletion fraction for stomatal control (p - sto) - Upper threshold",
        "format" : "{:0.2f}"
    },
    "KsShapeFactorStomata" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Shape factor for water stress coefficient for stomatal control (0.0 = straight line)",
        "format" : "{:0.1f}"
    },
    "pSenescence" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Soil water depletion factor for canopy senescence (p - sen) - Upper threshold",
        "format" : "{:0.2f}"
    },
    "KsShapeFactorSenescence" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Shape factor for water stress coefficient for canopy senescence (0.0 = straight line)",
        "format" : "{:0.1f}"
    },
    "SumEToDelaySenescence" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Sum(ETo) during dormant period to be exceeded before crop is permanently wilted",
        "format" : "{:0d}"
    },
    "pPollination" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Soil water depletion factor for pollination (p - pol) - Upper threshold",
        "format" : "{:0.2f}"
    },
    "AnaeroPoint" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Vol% for Anaerobiotic point (* (SAT - [vol%]) at which deficient aeration occurs *)",
        "format" : "{:0d}"
    },
    "Stress" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Considered soil fertility stress for calibration of stress response (%)",
        "format" : "{:0d}"
    },
    "ShapeCGC" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "required" : False,
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Shape factor for the response of canopy expansion to soil fertility stress",
            "Response of canopy expansion is not considered"
        ],
        "format" : "{:0.2f}"
    },
    "ShapeCCX" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "required" : False,
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Shape factor for the response of maximum canopy cover to soil fertility stress",
            "Response of maximum canopy cover is not considered"
        ],
        "format" : "{:0.2f}"
    },
    "ShapeWP" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "required" : False,
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Shape factor for the response of crop Water Productivity to soil fertility stress",
            "Response of crop Water Productivity is not considered"
        ],
        "format" : "{:0.2f}"
    },
    "ShapeCDecline" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "required" : False,
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Shape factor for the response of decline of canopy cover to soil fertility stress",
            "Response of decline of canopy cover is not considered"
        ],
        "format" : "{:0.2f}"
    },
    None,
    "Tcold" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "required" : False,
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Minimum air temperature below which pollination starts to fail (cold stress) (degC)",
            "Cold (air temperature) stress affecting pollination - not considered"
        ],
        "format" : "{:0d}"
    },
    "Theat" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "required" : False,
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Maximum air temperature above which pollination starts to fail (heat stress) (degC)",
            "Heat (air temperature) stress affecting pollination - not considered"
        ],
        "format" : "{:0d}"
    },
    "GDtranspLow" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "required" : False,
        "valid_range" : [0., math.inf],
        "description" : [
            "Minimum growing degrees required for full crop transpiration (degC - day)",
            "Cold (air temperature) stress on crop transpiration not considered"
        ],
        "format" : "{:0.1f}"
    },
    "ECemin" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Electrical Conductivity of soil saturation extract at which crop starts to be affected by soil salinity (dS/m)",
        "format" : "{:0d}"
    },
    "ECemax" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Electrical Conductivity of soil saturation extract at which crop can no longer grow (dS/m)",
        "format" : "{:0d}"
    },
    None,
    "CCsaltDistortion" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [0, 100]
        "description" : "Calibrated distortion (%) of CC due to salinity stress (Range: 0 (none) to +100 (very strong))",
        "format" : "{:0d}"
    },
    "ResponseECsw" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [0, 200]
        "description" : "Calibrated response (%) of stomata stress to ECsw (Range: 0 (none) to +200 (extreme))",
        "format" : "{:0d}"
    },
    "KcTop" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Crop coefficient when canopy is complete but prior to senescence (KcTr,x)",
        "format" : "{:0.2f}"
    },
    "KcDecline" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Decline of crop coefficient (%/day) as a result of ageing, nitrogen deficiency, etc.",
        "format" : "{:0.3f}"
    },
    "RootMin" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Minimum effective rooting depth (m)",
        "format" : "{:0.2f}"
    },
    "RootMax" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Maximum effective rooting depth (m)",
        "format" : "{:0.2f}"
    },
    "RootShape" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Shape factor describing root zone expansion",
        "format" : "{:0d}"
    },
    "SmaxTopQuarter" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Maximum root water extraction (m3water/m3soil.day) in top quarter of root zone",
        "format" : "{:0.3f}"
    },
    "SmaxBotQuarter" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Maximum root water extraction (m3water/m3soil.day) in bottom quarter of root zone",
        "format" : "{:0.3f}"
    },
    "CCEffectEvapLate" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Effect of canopy cover in reducing soil evaporation in late season stage",
        "format" : "{:0d}"
    },
    "SizeSeedling" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Soil surface covered by an individual seedling at 90 % emergence (cm2)",
        "format" : "{:0.2f}"
    },
    "SizePlant" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Canopy size of individual plant (re-growth) at 1st day (cm2)",
        "format" : "{:0.2f}"
    },
    "PlantingDens" : {
        "datatype" : float,
        "discrete" : False,
        "depends_on" : None,
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Number of plants per hectare",
        "format" : "{:0d}"
    },
    "CGC" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Canopy growth coefficient (CGC): Increase in canopy cover (fraction soil cover per day)",
        "format" : "{:0.5f}"
    },
    "YearCCx" : {
        "type" : 2,
        "required" : True,      # OR some kind of dictionary? e.g. {subkind : [4]}
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Number of years at which CCx declines to 90 % of its value due to self-thinning - for Perennials",
            "Number of years at which CCx declines to 90 % of its value due to self-thinning - Not Applicable"
        ],
        "format" : "{:0d}"
    },
    "CCxRoot" : {
        "type" : 2,
        "required" : True,
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Shape factor of the decline of CCx over the years due to self-thinning - for Perennials",
            "Shape factor of the decline of CCx over the years due to self-thinning - Not Applicable"
        ],
        "format" : "{:0.2f}"
    },
    None,
    "CCx" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Maximum canopy cover (CCx) in fraction soil cover",
        "format" : "{:0.2f}"
    },
    "CDC" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Canopy decline coefficient (CDC): Decrease in canopy cover (in fraction per day)",
        "format" : "{:0.5f}"
    },
    "DaysToGermination" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "valid_range" : [-math.inf, math.inf],
        "type" : ""
        "description" : {
            0: "Calendar Days: from sowing to emergence", # Sowing
            1: "Calendar Days: from transplanting to recovered transplant" # Transplant
            -9: "Calendar Days: from regrowth to recovering"                # Regrowth
        },
        "format" : "{:0d}"
    },
    "DaysToMaxRooting" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "Calendar Days: from sowing to maximum rooting depth", # Sowing
            1: "Calendar Days: from transplanting to maximum rooting depth", # Transplant
            -9: "Calendar Days: from regrowth to maximum rooting depth"       # Regrowth
        },
        "format" : "{:0d}"
    },
    "DaysToSenescence" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "Calendar Days: from sowing to start senescence",
            1: "Calendar Days: from transplanting to start senescence",
            -9: "Calendar Days: from regrowth to start senescence"
        },
        "format" : "{:0d}"
    },
    "DaysToHarvest" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "Calendar Days: from sowing to maturity (length of crop cycle)",
            1: "Calendar Days: from transplanting to maturity",
            -9: "Calendar Days: from regrowth to maturity"
        },
        "format" : "{:0d}"
    },
    "DaysToFlowering" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "Calendar Days: from sowing to flowering (or yield formation if subkind is Tuber)",
            1: "Calendar Days: from transplanting to flowering (or yield formation if subkind is Tuber)",
            -9: "Calendar Days: from regrowth to flowering (or yield formation if subkind is Tuber)"
        },
        "format" : "{:0d}"
    },
    "LengthFlowering" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Length of the flowering stage (days)",
        "format" : "{:0d}"
    },
    "DeterminancyLinked" : {
        "type" : 1,
        "valid_range" : [0, 1],
        "description" : {
            0: "Crop determinancy unlinked with flowering",
            1: "Crop determinancy linked with flowering"
        },
        "format" : "{:0d}"
    },
    "fExcess" : {
        "type" : 2,
        "valid_range" : [0, 100],
        "description" : "Excess of potential fruits (%)",
        "format" : "{:0d}"
    },
    "DaysToHIo" : {
        "type" : 2,
        "valid_range" : [0, math.inf],
        "description" : [
            "Building up of Harvest Index starting at sowing/transplanting (days)", # Vegetative/forage
            "Building up of Harvest Index starting at flowering (days)", # Grain
            "Building up of Harvest Index starting at root/tuber enlargement (days)", # Tuber
            "Building up of Harvest Index during yield formation (days)" # Default
        ],
        "format" : "{:0d}"
    },
    "WP" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Water Productivity normalized for ETo and CO2 (WP*) (gram/m2)",
        "format" : "{:0.1f}"
    },
    "WPy" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Water Productivity normalized for ETo and CO2 during yield formation (as % WP*)",
        "format" : "{:0d}"
    },
    "AdaptedToCO2" : {
        "type" : 2,
        "valid_range" : [0, 100],
        "description" : "Crop performance under elevated atmospheric CO2 concentration (%)",
        "format" : "{:0d}"
    },
    "HI" : {
        "type" : 2,
        "valid_range" : [0, 100],
        "description" : "Reference Harvest Index (HIo) (%)",
        "format" : "{:0d}"
    },
    "HIincrease" : {
        "type" : 2,
        "valid_range" : [0, 100],
        "description" : "Possible increase (%) of HI due to water stress before flowering (or yield formation if subkind is Tuber)",
        "format" : "{:0d}"
    },
    "aCoeff" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Coefficient describing positive impact on HI of restricted vegetative growth during yield formation",
            "No impact on HI of restricted vegetative growth during yield formation"
        ],
        "format" : "{:0.1f}"
    },
    "bCoeff" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Coefficient describing negative impact on HI of stomatal closure during yield formation",
            "No effect on HI of stomatal closure during yield formation"
        ],
        "format" : "{:0.1f}"
    },
    "DHImax" : {
        "type" : 2,
        "valid_range" : [0, 100],
        "description" : "Allowable maximum increase (%) of specified HI",
        "format" : "{:0d}"
    },
    "GDDaysToGermination" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : {
            0: "GDDays: from sowing to emergence",
            1: "GDDays: from transplanting to recovered transplant",
            -9: "GDDays: from regrowth to recovering"
        },
        "format" : "{:0d}"
    },
    "GDDaysToMaxRooting" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "GDDays: from sowing to maximum rooting depth",
            1: "GDDays: from transplanting to maximum rooting depth",
            -9: "GDDays: from regrowth to maximum rooting depth"
        },
        "format" : "{:0d}"
    },
    "Senescence" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "GDDays: from sowing to start senescence",
            1: "GDDays: from transplanting to start senescence",
            -9: "GDDays: from regrowth to start senescence"
        },
        "format" : "{:0d}"
    },
    "Harvest" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "GDDays: from sowing to maturity (length of crop cycle)",
            1: "GDDays: from transplanting to maturity",
            -9: "GDDays: from regrowth to maturity"
        },
        "format" : "{:0d}"
    },
    "GDDaysToFlowering" : {
        "type" : 2,
        "required" : True,
        "depends_on" : "Planting",
        "description" : {
            0: "GDDays: from sowing to flowering (or yield formation if subkind is Tuber)",
            1: "GDDays: from transplanting to flowering (or yield formation if subkind is Tuber)",
            -9: "GDDays: from regrowth to flowering (or yield formation if subkind is Tuber)"
        },
        "format" : "{:0d}"
    },
    "GDDLengthFlowering" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "Length of the flowering stage (growing degree days)",
        "format" : "{:0d}"
    },
    "GDDCGC" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "CGC for GGDays: Increase in canopy cover (in fraction soil cover per growing-degree day)",
        "format" : "{:0.6f}"
    },
    "GDDCDC" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "CDC for GGDays: Decrease in canopy cover (in fraction per growing-degree day)",
        "format" : "{:0.6f}"
    },
    "GDDaysToHIo" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : "GDDays: building-up of Harvest Index during yield formation",
        "format" : "{:0d}"
    },
    "DryMatter" : {
        "type" : 2,
        "valid_range" : [0, 100],
        "description" : "dry matter content (%) of fresh yield",
        "format" : "{:0d}"
    },
    "RootMinYear1" : {
        "type" : 2,
        "valid_range" : [-math.inf, math.inf],
        "description" : [
            "Minimum effective rooting depth (m) in first year (for perennials)", # Forage
            "Minimum effective rooting depth (m) in first year - required only in case of regrowth" # Regrowth
        ],
        "format" : "{:0.2f}"
    },
    "SownYear1" : {
        "type" : 1,
        "required" : True,
        "valid_range" : [0, 1]
        "description" : {
            1 : [
                "Crop is sown in 1st year (for perennials)",
                "Crop is sown in 1st year - required only in case of regrowth"
            ],
            0 : [
                "Crop is transplanted in 1st year (for perennials)",
                "Crop is transplanted in 1st year - required only in case of regrowth"
            ]
        },
        "format" : "{:0d}"
    },
    "Assimilates_On" : {
        "type" : 1,
        "valid_range" : [0, 1],
        "description" : {
            0 : "Transfer of assimilates from above ground parts to root system is NOT considered",
            1 : "Transfer of assimilates from above ground parts to root system is considered"
        },
        "format" : "{:0d}"
    },
    "Assimilates_Period" : {
        "type" : 1,
        "valid_range" : [0, 1],
        "description" : {
            0 : "Number of days at end of season during which assimilates are stored in root system",
            1 : "Number of days at end of season during which assimilates are stored in root system"
        },
        "format" : "{:0d}"
    },
    "Assimilates_Stored" : {
        "type" : 1,
        "valid_range" : [0, 1],
        "description" : {
            0 : "Percentage of assimilates transferred to root system at last day of season",
            1 : "Percentage of assimilates transferred to root system at last day of season"
        },
        "format" : "{:0d}"
    },
    "Assimilates_Mobilized" : {
        "type" : 1,
        "valid_range" : [0, 1],
        "description" : {
            0 : "Percentage of stored assimilates transferred to above ground parts in next season",
            1 : "Percentage of stored assimilates transferred to above ground parts in next season"
        },
        "format" : "{:0d}"
    }
}

class CropParameter(Parameter):
    def __init__(self, crop_type: str, parameter_name: str):
        self._set_crop_type(crop_type)
        self._set_parameter_name(name)
        self._set_description()
        self._set_default_value()
        self.set_valid_range()
        self.set_str_format()

    def _set_parameter_name(self, name):
        # TODO check against valid parameter names
        self.name = name

    def _set_crop_type(self, crop_type):
        # TODO check against valid crop types
        self.crop_type = crop_type

    def _set_description(self):
        pass

    def _set_default_value(self):
        pass

    def _set_valid_range(self):
        pass

    def _set_str_format(self):
        pass

    @property
    def name(self):
        return self.name

    @property
    def description(self):
        return self.description

    @property
    def default_value(self):
        return self.default_value

    @property
    def valid_range(self):
        return self.valid_range

    @property
    def str_format(self):
        return self.str_format

# No need for separate
# class KsShapeFactor(CropParameter):
#     def __init__(self, crop_type):
#         super(KsShapeFactor, self).__init__(crop_type=crop_type)
#         self.value = self.default_value

#     def set_value(self, value):
#         if value >= self.valid_range[0] and value <= self.valid_range[1]:
#             self.value = value
#         else:
#             raise ValueError("Out of range")

#     @property
#     def name(self):
#         return "KsShapeFactor"

#     @property
#     def description(self):
#         return "Shape factor for water stress coefficient for canopy expansion (0.0 = straight line)"

#     @property
#     def default_value(self):
#         return 1

#     @property
#     def valid_range(self):
#         return [0, 1]

#     @property
#     def str_format(self):
#         value = _format_crop_parameter("{:0.2f}".format(self.value))
#         return " : ".join([value, self.description])
