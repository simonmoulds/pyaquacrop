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
        default_value = int(1)
    ),
    "IrriFwInSeason": ContinuousParameter(
        name="IrriFwInSeason",
        datatype=int,
        valid_range=(0, 100),
        description="Percentage of soil surface wetted by irrigation",
        default_value=int(100)
    ),
    "IrriMode": DiscreteParameter(
        name="IrriMode",
        valid_range=(0, 1, 2, 3),
        description={
            0: "No irrigation",
            1: "Specify irrigation events",
            2: "Generate of an irrigation schedule",
            3: "Determine net irrigation water requirements"
        },
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
        datatype=int,
        valid_range=(0, 100),
        description="Depletion (% RAW) threshold"
    )
}


class IrrigationParameterSet:

    IRRIGATION_PARAMETERS = IRRI_PARAMETER_DICT

    def __init__(self,
                 config):

        # Default is not to provide an irrigation file,
        # in which case rainfed is assumed
        # TODO we need to work out a way for users to provide either a single value or a map of input values [same goes for crop parameters etc.]
        pass

    def set_default_values(self):
        pass

    def update_value_description(self):
        pass

    def set_value(self):
        pass

    def get_str_format(self, name):
        return self.IRRIGATION_PARAMETERS[name].str_format

    @property
    def default_header(self):
        pass

    def write(self, filename, header=None):
        if header is None:
            header = self.default_header
        version = format_parameter(AQUACROP_VERSION)
        protected = format_parameter("0")
        with open(filename, "w") as f:
            f.write(header + os.linesep)
            f.write(version + " : AquaCrop Version" + os.linesep)
            # FIXME - parameters to include depends on type of irrigation
            #
            # for param in self.CROP_PARAMETER_ORDER:
            #     if param is not None:
            #         description = self.CROP_PARAMETERS[param].value_description
            #         num = self.CROP_PARAMETERS[param].str_format
            #     else:
            #         description = "dummy - no longer applicable"
            #         num = format_parameter("-9")
            #     f.write(num + " : " + description + os.linesep)

            # if self.subkind == 4:
            #     # Add internal crop calendar
            #     f.write(os.linesep)
            #     f.write(self.default_onset_header + os.linesep)
            #     for param in self.ONSET_CROP_PARAMETER_ORDER:
            #         if param is not None:
            #             description = self.ONSET_CROP_PARAMETERS[
            #                 param
            #             ].value_description
            #             num = self.ONSET_CROP_PARAMETERS[param].str_format
            #         else:
            #             description = "dummy - no longer applicable"
            #             num = format_parameter("-9")
            #         f.write(num + " : " + description + os.linesep)
