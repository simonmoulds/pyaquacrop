#!/usr/bin/env python3

import os
import tomli
import warnings
import logging

logger = logging.getLogger(__name__)

# VALID_NONE_VALUES = ['None', 'NONE', 'none', '']
# DEFAULT_INPUT_FILE_OPTS = {
#     'filename': None,
#     'varname': None,
#     'is_1d': False,
#     'xy_dimname': None,
#     'factor': 1.,
#     'offset': 0.
# }

class Configuration:

    def __init__(
        self,
        configfile,
        # output_directory,
        # debug_mode=False,
        # system_arguments=None,
        **kwargs
    ):
        # Input files should be specified relative to the
        # location of the configuration file
        path = os.path.dirname(configfile)
        if os.path.isabs(path):
            self.configpath = path
        else:
            self.configpath = os.path.join(os.getcwd(), path)

        with open(configfile, 'rb') as f:
            self._toml_dict = tomli.load(f)
        self.parse_config_file()
        self.set_config()

    def parse_config_file(self):
        config_sections = self._toml_dict.keys()
        for section in config_sections:
            vars(self)[section] = {}
            options = self._toml_dict[section].keys()
            for option in options:
                self.__getattribute__(section)[option] = self._toml_dict[section][option]

    def set_config(self, system_arguments=None):

        # self.deterministic = kwargs.get('deterministic', False)
        # self.montecarlo = kwargs.get('montecarlo', False)
        # self.kalmanfilter = kwargs.get('kalmanfilter', False)
        # if self.deterministic:
        #     self.set_deterministic_run_options()
        # else:
        #     if self.montecarlo | self.kalmanfilter:
        #         self.set_montecarlo_run_options()
        #     if self.kalmanfilter:
        #         self.set_kalmanfilter_run_options()
        self.set_model_grid_options()
        self.set_weather_options()
        # self.set_etref_preprocess_options()
        # self.set_pseudo_coord_options()
        self.set_initial_condition_options()
        self.set_groundwater_options()
        self.set_soil_parameter_options()
        self.set_crop_parameter_options()
        self.set_irrigation_options()
        self.set_management_options()
        self.set_reporting_options()

    # def set_deterministic_run_options(self):
    #     pass

    # def set_montecarlo_run_options(self):
    #     pass

    # def set_kalmanfilter_run_options(self):
    #     pass

    # def set_pseudo_coord_options(self):
    #     # make sure that pseudo-coordinates are lists
    #     if 'PSEUDO_COORDS' not in self.config_sections:
    #         self.PSEUDO_COORDS = {}
    #     else:
    #         for key, value in self.PSEUDO_COORDS.items():
    #             if isinstance(value, (int, float)):
    #                 self.PSEUDO_COORDS[key] = [value]
    #             elif isinstance(value, (str)):
    #                 self.PSEUDO_COORDS[key] = eval(value)

    def set_model_grid_options(self):
        pass

    def set_weather_options(self):
        # weather_sections = [
        #     'PRECIPITATION',
        #     'TAVG',
        #     'TMIN',
        #     'TMAX',
        #     'LWDOWN',
        #     'SP',
        #     'SH',
        #     'RHMAX',
        #     'RHMIN',
        #     'RHMEAN',
        #     'SWDOWN',
        #     'WIND',
        #     'ETREF',
        #     'CARBON_DIOXIDE'
        # ]
        # for section in weather_sections:
        #     if section in vars(self):
        #         for opt, default_value in DEFAULT_INPUT_FILE_OPTS.items():
        #             if opt not in vars(self)[section].keys():
        #                 vars(self)[section][opt] = default_value
        #     else:
        #         vars(self)[section] = DEFAULT_INPUT_FILE_OPTS
        pass

    def set_initial_condition_options(self):
        pass

    def set_groundwater_options(self):
        pass

    def set_soil_parameter_options(self):
        pass

    def set_crop_parameter_options(self):
        pass

    def set_irrigation_options(self):
        pass

    def set_management_options(self):
        pass

    def set_reporting_options(self):
        # if 'REPORTING' not in self.config_sections:
        #     self.REPORTING = {}
        # if 'report' not in list(self.REPORTING.keys()):
        #     self.REPORTING['report'] = False
        pass

    # def check_config_file_for_required_entry(
    #         self,
    #         section_name,
    #         entry_name,
    #         allow_none=False,
    #         allow_empty=False
    # ):
    #     if entry_name not in list(vars(self)[section_name].keys()):
    #         raise KeyError(
    #             entry_name + ' in section ' + section_name + ' must be provided'
    #         )
    #     else:
    #         entry = vars(self)[section_name][entry_name]
    #         if not allow_none and (entry in VALID_NONE_VALUES):
    #             raise ValueError(
    #                 entry_name + ' in section ' + section_name + 'cannot by empty or none'
    #             )
    #         else:
    #             pass

# class Configuration(object):
#     def __init__(
#             self,
#             config_filename,
#             output_directory,
#             debug_mode=False,
#             system_arguments=None,
#             **kwargs
#     ):
#         """Model configuration.

#         This class represents the configuration options which are
#         necessary to run `hm` models.

#         Model developers should design model-specific configuration
#         classes which inherit from this base class.

#         Parameters
#         ----------
#         config_filename: str
#             Filename of the configuration file.
#         output_directory: str
#             Intended location of model output
#         debug_mode: bool, optional
#             Should the model be run in debug mode?
#         system_arguments: TODO
#             TODO
#         """
#         if config_filename is None:
#             raise ValueError(
#                 'No configuration file specified'
#             )

#         config_filename = os.path.abspath(config_filename)
#         if not os.path.exists(config_filename):
#             raise ValueError(
#                 'Specified configuration file '
#                 + config_filename + ' does not exist'
#             )
#         self.config_filename = config_filename
#         self.output_directory = output_directory
#         self._timestamp = pd.Timestamp.now()
#         self._debug_mode = debug_mode
#         self.parse_config_file()
#         self.set_config(system_arguments)

#     def parse_config_file(self):
#         # config = ConfigParser(interpolation=ExtendedInterpolation())
#         # config.optionxform = str
#         # config.read(self.config_filename)
#         # self.config_sections = config.sections()
#         # for section in self.config_sections:
#         #     vars(self)[section] = {}
#         #     options = config.options(section)
#         #     for option in options:
#         #         val = config.get(section, option)
#         #         self.__getattribute__(section)[option] = val
#         config = toml.load(self.config_filename)
#         self.config_sections = config.keys()
#         for section in self.config_sections:
#             vars(self)[section] = {}
#             options = config[section].keys()
#             for option in options:
#                 self.__getattribute__(section)[option] = config[section][option]

#     def set_config(self, system_arguments=None):
#         self.check_required_options()
#         self.assign_default_options()
#         self.create_output_directories()
#         self.create_coupling_directories()
#         self.initialize_logging("Default", system_arguments)
#         self.backup_configuration()

#     def initialize_logging(self, log_file_location="Default", system_arguments=None):
#         # Initialize logging. Prints to both the console
#         # and a log file, at configurable levels.
#         logging.getLogger().setLevel(logging.DEBUG)
#         formatter = logging.Formatter(
#             '%(asctime)s %(name)s %(levelname)s %(message)s')
#         log_level_console = self.LOGGING['log_level_console']
#         log_level_file = self.LOGGING['log_level_file']
#         if self._debug_mode == True:
#             log_level_console = "DEBUG"
#             log_level_file = "DEBUG"

#         console_level = getattr(
#             logging, log_level_console.upper(), logging.INFO)
#         if not isinstance(console_level, int):
#             raise ValueError('Invalid log level: %s', log_level_console)

#         console_handler = logging.StreamHandler()
#         console_handler.setFormatter(formatter)
#         console_handler.setLevel(console_level)
#         logging.getLogger().addHandler(console_handler)

#         if log_file_location != "Default":
#             self.logFileDir = log_file_location
#         log_filename = os.path.join(
#             self.logFileDir,
#             os.path.basename(self.config_filename) + '_'
#             + str(self._timestamp.isoformat()).replace(":", ".")
#             + '.log'
#         )
#         file_level = getattr(logging, log_level_file.upper(), logging.DEBUG)
#         if not isinstance(console_level, int):
#             raise ValueError('Invalid log level: %s', log_level_file)

#         file_handler = logging.FileHandler(log_filename)
#         file_handler.setFormatter(formatter)
#         file_handler.setLevel(file_level)
#         logging.getLogger().addHandler(file_handler)

#         dbg_filename = os.path.join(
#             self.logFileDir,
#             os.path.basename(self.config_filename) + '_'
#             + str(self._timestamp.isoformat()).replace(":", ".")
#             + '.dbg'
#         )

#         debug_handler = logging.FileHandler(dbg_filename)
#         debug_handler.setFormatter(formatter)
#         debug_handler.setLevel(logging.DEBUG)
#         logging.getLogger().addHandler(debug_handler)

#         disclaimer.print_disclaimer(with_logger=True)
#         logger.info('Model run started at %s', self._timestamp)
#         logger.info('Logging output to %s', log_filename)
#         logger.info('Debugging output to %s', dbg_filename)

#         if system_arguments != None:
#             logger.info(
#                 'The system arguments given to execute this run: %s',
#                 system_arguments
#             )

#     def backup_configuration(self):
#         # Copy config file to log directory.
#         backup_location = os.path.join(
#             self.logFileDir,
#             os.path.basename(self.config_filename) + '_'
#             + str(self._timestamp.isoformat()).replace(":", ".")
#             + '.ini'
#         )
#         shutil.copy(self.config_filename, backup_location)

#     def create_output_directories(self):
#         # TODO: refactor this section of code, because I don't
#         # think they're all required.
#         try:
#             os.makedirs(self.output_directory)
#         except:
#             pass

#         self.tmpDir = os.path.join(self.output_directory, 'tmp')
#         try:
#             os.makedirs(self.tmpDir)
#         except FileExistsError:
#             pass

#         self.outNCDir = os.path.join(self.output_directory, 'netcdf')
#         try:
#             os.makedirs(self.outNCDir)
#         except FileExistsError:
#             pass

#         self.logFileDir = os.path.join(self.output_directory, 'log')
#         cleanLogDir = True
#         try:
#             os.makedirs(self.logFileDir)
#         except FileExistsError:
#             pass

#         self.endStateDir = os.path.join(self.output_directory, 'states')
#         try:
#             os.makedirs(self.endStateDir)
#         except FileExistsError:
#             pass

#     def create_coupling_directories(self):
#         pass

#     def assign_default_options(self):
#         self.assign_default_logging_options()
#         self.assign_default_file_path_options()

#     def assign_default_logging_options(self):
#         if 'LOGGING' not in self.config_sections:
#             self.LOGGING = {}
#         if 'log_level_console' not in self.LOGGING:
#             self.LOGGING['log_level_console'] = 'INFO'
#         if 'log_level_file' not in self.LOGGING:
#             self.LOGGING['log_level_file'] = 'INFO'

#     def assign_default_file_path_options(self):
#         if 'FILE_PATHS' not in self.config_sections:
#             self.FILE_PATHS = {}
#         if 'in_path' not in self.FILE_PATHS:
#             self.FILE_PATHS['in_path'] = '.'
#         if 'out_path' not in self.FILE_PATHS:
#             self.FILE_PATHS['in_path'] = '.'

#     def assign_default_reporting_options(self):
#         if 'REPORTING' not in self.config_sections:
#             self.REPORTING = {}
#         if 'report' not in self.REPORTING:
#             self.REPORTING['report'] = False

#     def check_required_options(self):
#         default_model_grid_values = {
#             'mask': None,
#             'mask_varname': None,
#             'area_varname': None,
#             'is_1d': False,
#             'xy_dimname': None
#         }
#         for opt, default_value in default_model_grid_values.items():
#             if opt not in self.MODEL_GRID.keys():
#                 self.MODEL_GRID[opt] = default_value
#             # if opt in self.MODEL_GRID.keys():
#             #     self.MODEL_GRID[opt] = interpret_string(self.MODEL_GRID[opt])
#             # else:
#             #     self.MODEL_GRID[opt] = default_value

#         # # MODEL_GRID
#         # self._default_config_check('MODEL_GRID', ['mask'])
#         # if 'mask_varname' not in self.MODEL_GRID:
#         #     self.MODEL_GRID['mask_varname'] = None
#         # if 'area_varname' not in self.MODEL_GRID:
#         #     self.MODEL_GRID['area_varname'] = None
#         # if 'is_1d' not in self.MODEL_GRID:
#         #     self.MODEL_GRID['is_1d'] = False
#         # if 'xy_dimname' not in self.MODEL_GRID:
#         #     self.MODEL_GRID['xy_dimname'] = None

#         # PSEUDO_COORDS
#         if 'PSEUDO_COORDS' not in self.config_sections:
#             self.PSEUDO_COORDS = {}
#         else:
#             # TODO - interpret coordinates
#             pass

#     def _default_config_check(self, section, options):
#         if section not in self.config_sections:
#             raise KeyError(
#                 self.generate_missing_section_message(section)
#             )
#         else:
#             for option in options:
#                 if option not in vars(self)[section]:
#                     raise KeyError(
#                         self.generate_missing_option_message(section, option)
#                     )

#     def generate_missing_section_message(self, section):
#         """Generates message to inform users that a configuration
#         section is missing.
#         """
#         return 'Configuration file ' + self.config_filename \
#             + ' does not contain section ' + section \
#             + ', which must be supplied'

#     def generate_missing_option_message(self, section, option):
#         """Generates message to inform users that a configuration
#         option is missing.
#         """
#         return 'Section ' + section + ' in configuration file ' \
#             + self.config_filename + ' does not contain option ' \
#             + option + ', which must be supplied'
