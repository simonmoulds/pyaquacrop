#!/usr/bin/env python3

import os
import math

from utils import format_parameter


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
