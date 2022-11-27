#!/usr/bin/env python3

import os
import math

from utils import format_parameter


MANAGEMENT_PARAMETER_DICT = {
    # ################################# #
    # Mulches                           #
    # ################################# #
    "Mulch": ContinuousParameter(
        name="Mulch",
        datatype=int,
        valid_range=(0, 100),
        description="Percentage (%) of ground surface covered by mulches in growing period"
    ),
    "EffectMulchInS": ContinuousParameter(
        name="EffectMulchInS",
        datatype=int,
        valid_range=(0, 100),
        description="Effect (%) of mulches on the reduction of soil evaporation"
    ),
    # ################################# #
    # Soil fertility                    #
    # ################################# #
    "FertilityStress": ContinuousParameter(
        name="FertilityStress",
        datatype=int,
        valid_range=(0, 100),
        description="Degree of soil fertility stress (%) - Effect is crop specific"
    ),
    # ################################# #
    # Bunds                             #
    # ################################# #
    "BundHeight": ContinuousParameter(
        name="BundHeight",
        datatype=float,
        valid_range=(0, math.inf),
        description="height (m) of soil bunds",
        scale=2
    ),
    # ################################# #
    # Surface runoff                    #
    # ################################# #
    "RunoffOn": DiscreteParameter(
        name="RunoffOn",
        valid_range=(0, 1),
        description={
            0: "Surface runoff is not affected by field surface practices",
            1: "Surface runoff is affected or completely prevented by field surface practices"
        }
    ),
    "CNcorrection": ContinuousParameter(
        name="CNcorrection",
        datatype=int,
        valid_range=(0, 100),
        description="Percent increase/decrease of soil profile CN value",
    ),
    # ################################# #
    # Weed infestation                  #
    # ################################# #
    "WeedRC": ContinuousParameter(
        name="WeedRC",
        datatype=int,
        valid_range=(0, 100),
        description="Relative cover of weeds at canopy closure"
    ),
    "WeedDeltaRC": ContinuousParameter(
        name="WeedDeltaRC",
        datatype=int,
        valid_range=(0, 100),
        description="Increase (%) of relative cover of weeds in mid-season"
    ),
    "WeedShape": ContinuousParameter(
        name="WeedShape",
        datatype=float,
        valid_range=(-math.inf, math.inf),
        description="Shape factor of the CC expansion function in a weed infested field",
        scale=2
    ),
    "WeedAdj": ContinuousParameter(
        name="WeedAdj",
        datatype=int,
        valid_range=(0, 100),
        description="replacement (%) by weeds of the self-thinned part of the CC - only for perennials"
    ),
    # ################################# #
    # Multiple cuttings
    # ################################# #
    "MultipleCuttings": DiscreteParameter(
        name="MultipleCuttings",
        valid_range=(0, 1),
        description={
            0: "Multiple cuttings are considered",
            1: "Multiple cuttings are not considered"
        }
    ),
    "Cuttings_CCcut": ContinuousParameter(
        name="Cuttings_CCcut",
        datatype=int,
        valid_range=(0, 100),
        description="Canopy cover (%) after cutting"
    ),
    "Cuttings_CGCPlus": ContinuousParameter(
        name="Cuttings_CGCPlus",
        datatype=int,
        valid_range=(0, 100),
        description="Increase (%) of Canopy Growth Coefficient (CGC) after cutting"
    ),
    "Cuttings_Day1": ContinuousParameter(
        name="CuttingsDay1",
        datatype=int,
        valid_range=(0, math.inf),
        description="First day of window for multiple cuttings (1 = start of growth cycle)"
    ),
    "Cuttings_NrDays": ContinuousParameter(
        name="Cuttings_NrDays",
        datatype=int,
        valid_range=(0, math.inf),
        description="Number of days in window for multiple cuttings (-9 = total growth cycle)"
    ),
    "Cuttings_Generate": DiscreteParameter(
        name="Cuttings_Generate",
        valid_range=(0, 1, -9),
        description={
            0: "Harvest events are specified by the user",
            1: "Multiple cuttings are generated by a time criterion",
            -9: "Timing of multiple cuttings - N/A"
        }
    ),
    "Cuttings_Criterion": DiscreteParameter(
        name="Cuttings_Criterion",
        valid_range=(0, 1, 2, 3, 4, 5),
        description={
            0: "Time criterion: N/A",
            1: "Time criterion: Interval in days",
            2: "Time criterion: Interval in growing-degree days",
            3: "Time criterion: Mass (ton/ha) dry above ground biomass",
            4: "Time criterion: Mass (ton/ha) dry crop yield",
            5: "Time criterion: Mass (ton/ha) fresh crop yield"
        }
    ),
    "Cuttings_HarvestEnd": DiscreteParameter(
        name="Cuttings_HarvestEnd",
        valid_range=(0, 1),
        description={
            0: "Final harvest at crop maturity is not considered",
            1: "Final harvest at crop maturity is considered"
        }
    ),
    "Cuttings_FirstDayNr": ContinuousParameter(
        name="Cuttings_FirstDayNr",
        datatype=int,
        valid_range=(0, math.inf),
        description="Day number of the reference day for the harvest calendar"
    )
}


class ManagementParameterSet:

    MANAGEMENT_PARAMETERS = IRRI_PARAMETER_DICT

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
        return self.MANAGEMENT_PARAMETERS[name].str_format

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
