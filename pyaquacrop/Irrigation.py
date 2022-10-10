#!/usr/bin/env python3

import os
import math

from utils import format_parameter


# def _irrigation_header(start_day=1, start_month=1, start_year=1901):

#     header = (
#         "Irrigation schedule"
#         + os.linesep
#         + format_parameter("7.0", 6, 4)
#         + ": AquaCrop Version"
#         + os.linesep
#         + format_parameter("2", 6, 4)
#         + ": variable groundwater table"
#         + os.linesep
#         + format_parameter(str(int(start_day)), 6, 4)
#         + ": first day of observations"
#         + os.linesep
#         + format_parameter(str(int(start_month)), 6, 4)
#         + ": first month of observations"
#         + os.linesep
#         + format_parameter(str(int(start_year)), 6, 4)
#         + ": first year of observations (1901 if not linked to a specific year)"
#         + os.linesep
#         + os.linesep
#     )
#     return header

IRRI_PARAMETER_DICT = {
    "IrriMethod": DiscreteParameter(
        name="IrriMethod",
        valid_range=(1, 2, 3, 4, 5),
        description={
            1: "Sprinkler",
            2: "Basin",
            3: "Border",
            4: "Furrow",
            5: "Drip"
        },
    ),
    "IrriFwInSeason": ContinuousParameter(
        name="IrriFwInSeason",
        datatype=int,
        valid_range=(0, 100),
        description="Percentage of soil surface wetted by irrigation"
    ),
    "IrriMode": DiscreteParameter(
        name="IrriMode",
        valid_range=(0, 1, 2, 3),
        description={
            0: "No irrigation",
            1: "Specify irrigation events",
            2: "Generate of an irrigation schedule",
            3: "Determine net irrigation water requirements"
        }
    ),
    # ################################# #
    # Irrigation schedule               #
    # ################################# #
    "IrriFirstDayNr": ContinuousParameter(
        name="IrriFirstDayNr",
        datatype=int,
        valid_range=(0, math.inf),
        description="Day number of reference day"
    ),
    # ################################# #
    # Generate irrigation schedule      #
    # ################################# #
    "GenerateTimeMode": DiscreteParameter(
        name="GenerateTimeMode",
        valid_range=(1, 2, 3, 4, 5),
        description={
            1: "Time criterion: Fixed interval",
            2: "Time criterion: Allowable depletion",
            3: "Time criterion: Allowable depletion",
            4: "Time criterion: Minimum level of surface water between soil bunds"
        }
    ),
    "GenerateDepthMode": DiscreteParameter(
        name="GenerateDepthMode",
        valid_range=(1, 2),
        description={
            1: "Depth criterion: Back to FC",
            2: "Depth criterion: Fixed net application depth"
        }
    ),
    # ################################# #
    # Determine net irrigation reqmt    #
    # ################################# #
    "PercRAW": ContinuousParameter(
        name="PercRAW",
        datatype:int,
        valid_range=(0, 100),
        description="Depletion (% RAW) threshold"
    )
}
