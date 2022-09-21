#!/usr/bin/env python3

import os

# OS parameters
LINESEP = os.linesep

# AquaCrop parameters
AQUACROP_VERSION = '7.0'
VALID_CROPS = ['wheat']

# See documentation in rep_Crop [global.f90]
CROP_PARAMETER_NAMES = [
    'AquaCropVersion',          # AquaCrop version
    'FileProtected',            # Whether the file is protected
    'CropType',                 # TODO - undocumented
    'Planting',                 # 1 = sown, 0 = transplanted, -9 = regrowth
    'ModeCycle',                # 0 = Determination of crop cycle : by growing degree-days; 1 = Determination of crop cycle : by calendar days'
    'pMethod',                  # 0 = No adjustment by ETo of soil water depletion factors (p); 1 = Soil water depletion factors (p) are adjusted by ETo
    'Tbase',                    # Base temperature (degC) below which crop development does not progress'
    'Tupper',                   # Upper temperature (degC) above which crop development no longer increases with an increase in temperature
    'GDDaysToHarvest',          # Total length of crop cycle in growing degree-days
    'pLeafDefUL',               # Soil water depletion factor for canopy expansion (p-exp) - Upper threshold
    'pLeafDeLL',                # Soil water depletion factor for canopy expansion (p-exp) - Lower threshold
    'KsShapeFactor',            # Shape factor for water stress coefficient for canopy expansion (0.0 = straight line)
    'pdef',                     # Soil water depletion fraction for stomatal control (p - sto) - Upper threshold
    'KsShapeFactorStomata',     # Shape factor for water stress coefficient for stomatal control (0.0 = straight line)
    'pSenescence',              # Soil water depletion factor for canopy senescence (p - sen) - Upper threshold
    'KsShapeFactorSenescence',  # Shape factor for water stress coefficient for canopy senescence (0.0 = straight line)
    'SumEToDelaySenescence',    # Sum(ETo) during dormant period to be exceeded before crop is permanently wilted
    'pPollination',             # pPollination == -9: Soil water depletion factor for pollination - Not Applicable; 0 <= pPollination <= 1: Soil water depletion factor for pollination (p - pol) - Upper threshold
    'AnaeroPoint',              # Vol% for Anaerobiotic point (* (SAT - [vol%]) at which deficient aeration occurs *)
    'Stress',                   # Considered soil fertility stress for calibration of stress response (%)
    'ShapeCGC',                 # ShapeCGC > 24.9_dp: Response of canopy expansion is not considered; ShapeCGC <= 24.9_dp: Shape factor for the response of canopy expansion to soil fertility stress
    'ShapeCCX',                 # ShapeCCX > 24.9_dp: Response of maximum canopy cover is not considered; ShapeCCX <= 24.9_dp: Shape factor for the response of maximum canopy cover to soil fertility stress
    'ShapeWP',                  # ShapeWP > 24.9_dp: Response of crop Water Productivity is not considered; ShapeWP <= 24.9_dp: Shape factor for the response of crop Water Productivity to soil fertility stress
    'ShapeCDecline',            # ShapeCDecline > 24.9_dp: Response of decline of canopy cover is not considered; ShapeCDecline <= 24.9_dp: Shape factor for the response of decline of canopy cover to soil fertility stress
    None,                       # dummy - Parameter no Longer required
    'Tcold',                    # Tcold == -9: Cold (air temperature) stress affecting pollination - not considered; Tcold != -9: Minimum air temperature below which pollination starts to fail (cold stress) (degC)
    'Theat',                    # Theat == -9: Heat (air temperature) stress affecting pollination - not considered; Theat != -9: Maximum air temperature above which pollination starts to fail (heat stress) (degC)
    'GDtranspLow',              # GDtranspLow == -9: Cold (air temperature) stress on crop transpiration not considered; GDtranspLow != -9: Minimum growing degrees required for full crop transpiration (degC - day)
    'ECemin',                   # Electrical Conductivity of soil saturation extract at which crop starts to be affected by soil salinity (dS/m)
    'ECemax',                   # Electrical Conductivity of soil saturation extract at which crop can no longer grow (dS/m)
    None,                       # Dummy - no longer applicable
    'CCsaltDistortion',         # Calibrated distortion (%) of CC due to salinity stress (Range: 0 (none) to +100 (very strong))
    'ResponseECsw',             # Calibrated response (%) of stomata stress to ECsw (Range: 0 (none) to +200 (extreme))
    'KcTop',                    # Crop coefficient when canopy is complete but prior to senescence (KcTr,x)
    'KcDecline',                # Decline of crop coefficient (%/day) as a result of ageing, nitrogen deficiency, etc.
    'RootMin',                  # Minimum effective rooting depth (m)
    'RootMax',                  # Maximum effective rooting depth (m)
    'RootShape',                # Shape factor describing root zone expansion
    'SmaxTopQuarter',           # Maximum root water extraction (m3water/m3soil.day) in top quarter of root zone
    'SmaxBotQuarter',           # Maximum root water extraction (m3water/m3soil.day) in bottom quarter of root zone
    'CCEffectEvapLate',         # Effect of canopy cover in reducing soil evaporation in late season stage
    'SizeSeedling',             # Soil surface covered by an individual seedling at 90 % emergence (cm2)
    'SizePlant',                # Canopy size of individual plant (re-growth) at 1st day (cm2)
    'PlantingDens',             # Number of plants per hectare
    'CGC',                      # Canopy growth coefficient (CGC): Increase in canopy cover (fraction soil cover per day)
    'YearCCx',                  # YearCCx == -9: Number of years at which CCx declines to 90 % of its value due to self-thinning - Not Applicable; YearCCx != -9: Number of years at which CCx declines to 90 % of its value due to self-thinning - for Perennials
    'CCxRoot',                  # CCxRoot == -9: Shape factor of the decline of CCx over the years due to self-thinning - Not Applicable; CCxRoot != -9: Shape factor of the decline of CCx over the years due to self-thinning - for Perennials
    None,                       # dummy - Parameter no Longer required
    'CCx',                      # Maximum canopy cover (CCx) in fraction soil cover
    'CDC',                      # Canopy decline coefficient (CDC): Decrease in canopy cover (in fraction per day)
    'DaysToGermination',        # These are more complicated - see L3712-3763
    'DaysToMaxRooting',
    'DaysToSenescence',
    'DaysToHarvest',
    'DaysToFlowering',
    'LengthFlowering',          # Length of the flowering stage (days)
    'DeterminancyLinked',       # 0 = Crop determinancy unlinked with flowering; 1 = Crop determinancy linked with flowering
    'fExcess',                  # if subkind is Vegetative or Forage: parameter NO LONGER required; if fExcess == -9: Excess of potential fruits - Not Applicable; if fExcess != -9: Excess of potential fruits (%)
    'DaysToHIo',                # See L3791-3805
    'WP',                       # Water Productivity normalized for ETo and CO2 (WP*) (gram/m2)
    'WPy',                      # Water Productivity normalized for ETo and CO2 during yield formation (as % WP*)
    'AdaptedToCO2',             # Crop performance under elevated atmospheric CO2 concentration (%)
    'HI',                       # Reference Harvest Index (HIo) (%)
    'HIincrease',               # if subkind == Tuber: Possible increase (%) of HI due to water stress before start of yield formation; else: Possible increase (%) of HI due to water stress before flowering
    'aCoeff',                   # if aCoeff == -9: No impact on HI of restricted vegetative growth during yield formation; if aCoeff != -9: Coefficient describing positive impact on HI of restricted vegetative growth during yield formation
    'bCoeff',                   # if bCoeff == -9: No effect on HI of stomatal closure during yield formation; if bCoeff != -9: Coefficient describing negative impact on HI of stomatal closure during yield formation
    'DHImax',                   # Allowable maximum increase (%) of specified HI
    'GDDaysToGermination',      # L3841-
    'GDDaysToMaxRooting',
    'Senescence',
    'Harvest',
    'GDDaysToFlowering',
    'GDDLengthFlowering',       # Length of the flowering stage (growing degree days)
    'GDDCGC',                   # CGC for GGDays: Increase in canopy cover (in fraction soil cover per growing-degree day)
    'GDDCDC',                   # CDC for GGDays: Decrease in canopy cover (in fraction per growing-degree day)
    'GDDaysToHIo',              # GDDays: building-up of Harvest Index during yield formation
    'DryMatter',                # dry matter content (%) of fresh yield
    'RootMinYear1',             # if subkind == Forage: Minimum effective rooting depth (m) in first year (for perennials); else: Minimum effective rooting depth (m) in first year - required only in case of regrowth
    'SownYear1',                # SownYear1 & subkind == Forage: Crop is sown in 1st year (for perennials); else if SownYear1 & subkind != Forage: Crop is sown in 1st year - required only in case of regrowth; else if ~SownYear1 & subkind == Forage: Crop is transplanted in 1st year (for perennials); else if ~SownYear1 & subkind != Forage: Crop is transplanted in 1st year - required only in case of regrowth
    'Assimilates_On',           # 0 = Transfer of assimilates from above ground parts to root system is NOT considered; 1 = Transfer of assimilates from above ground parts to root system is considered
    'Assimilates_Period',       # Number of days at end of season during which assimilates are stored in root system
    'Assimilates_Stored',       # Percentage of assimilates transferred to root system at last day of season
    'Assimilates_Mobilized'     # Percentage of stored assimilates transferred to above ground parts in next season
]

ONSET_CROP_PARAMETER_NAMES = [
    'GenerateOnset',
    'OnsetCriterion',
    'OnsetFirstDay',
    'OnsetFirstMonth' ,
    'OnsetLengthSearchPeriod',
    'OnsetThresholdValue',
    'OnsetPeriodValue',
    'OnsetOccurrence',
    'GenerateEnd',
    'EndCriterion',
    'EndLastDay',
    'EndLastMonth',
    'ExtraYears',
    'EndLengthSearchPeriod',
    'EndThresholdValue',
    'EndPeriodValue',
    'EndOccurrence'
]

IRR_PARAMETER_NAMES = []
MAN_PARAMETER_NAMES = []
