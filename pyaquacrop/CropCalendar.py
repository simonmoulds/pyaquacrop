

def _write_crop_calendar_input_file(
    generate_onset: bool,
    generate_temp_onset: str,
    start_search_period_day_nr: int,
    length_search_period: int,
    criterion_nr: int,
):

    # TODO the file contains more information, but it doesn't
    # look as if any parameters beyond those listed are actually
    # read from the file [L3253 global.f90]

    # TODO find out default values for the above values

    # It seems from the Fortran code that this is simply used as a flag: if exceeding 10 then GetOnsetTemp = .true. [L3289]
    if generate_onset & generate_temp_onset:
        if ~criterion_nr in [12, 13]:
            raise ValueError()
    # criterion_nr == 12: TMeanPeriod
    # criterion_nr == 13: GDDPeriod

    # This file is read by LoadCropCalendar() in global.f90 L3253
    # I think some of the parameters are actually specified in CRO file
    # GenerateOn
    # GenerateTempOn
    # Criterion [NB undocumented]
    # StartSearchDayNr
    # StopSearchDayNr
    # LengthSearchPeriod
    crop_calendar = (
        file_description
        + LINESEP
        + "{:12.1f}".format(7)
        + "  : AquaCrop Version"
        + LINESEP
        + "{:10d}".format(int(generate_onset))
        + "    : TODO"
        + LINESEP
        + "{:10d}".format(int(time_window_start))
        + "    : TODO"
        + LINESEP
        + "{:10d}".format(int(time_window_length))
        + "    : TODO"
        + LINESEP
    )
    return None
