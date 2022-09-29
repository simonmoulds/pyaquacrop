#!/usr/bin/env python3

import os

# OS parameters
LINESEP = os.linesep

# AquaCrop parameters
AQUACROP_VERSION = "7.0"
VALID_CROPS = ["wheat"]

# See documentation in rep_Crop [global.f90]
CROP_PARAMETER_NAMES = [
    "AquaCropVersion",
    "FileProtected",
    "subkind",
    "Planting",
    "ModeCycle",
    "pMethod",
    "Tbase",
    "Tupper",
    "GDDaysToHarvest",
    "pLeafDefUL",
    "pLeafDeLL",
    "KsShapeFactor",
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
    "Senescence",
    "Harvest",
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
]

ONSET_CROP_PARAMETER_NAMES = [
    "GenerateOnset",  # 0 = Onset is fixed on a specific day; 1 = Onset is generated by air temperature criterion
    "OnsetCriterion",  # 12 = Criterion: mean air temperature; 13 = Criterion: growing-degree days
    "OnsetFirstDay",
    "OnsetFirstMonth",
    "OnsetLengthSearchPeriod",
    "OnsetThresholdValue",  # Mean air temperature or growing-degree days
    "OnsetPeriodValue",  # Number of successive days
    "OnsetOccurrence",  # Number of occurrence
    "GenerateEnd",  # 0: End is fixed on a specific day; 1 = End is generated by an air temperature criterion
    "EndCriterion",  # 62 = Criterion: mean air temperature; 63 = Criterion: growing-degree days
    "EndLastDay",
    "EndLastMonth",
    "ExtraYears",
    "EndLengthSearchPeriod",
    "EndThresholdValue",  # Mean air temperature or growing-degree days
    "EndPeriodValue",  # Number of successive days
    "EndOccurrence",  # Number of occurrence
]

IRR_PARAMETER_NAMES = []
MAN_PARAMETER_NAMES = []

SOIL_PARAMETER_NAMES = []
MANAGEMENT_PARAMETER_NAMES = []
