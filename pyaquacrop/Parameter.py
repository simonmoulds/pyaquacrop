#!/usr/bin/env python3

from typing import Optional, Union, Any
from abc import ABC, abstractmethod, abstractproperty

from utils import format_parameter

class BaseParameter(ABC):
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


class Parameter(BaseParameter):
    def __init__(
        self,
        name: str,
        datatype: type,
        discrete: bool,
        valid_range: tuple,
        description: Union[dict, tuple, str],
        depends_on: Optional[tuple] = None,
        scale: Optional[int] = 2,
        required: bool = True,
        missing_value: int = -9,
        default_value: Optional[Any] = None
    ):

        # self._value = None
        self.set_default_value(default_value)
        # self._default_value = None
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
        if default_value is None:
            self._default_value = None
            self._value = None
        else:
            # if not isinstance(default_value, self.datatype):
            #     raise ValueError() # FIXME this may be too restrictive
            # default_value = self.datatype(default_value)
            # FIXME this smells
            if self.datatype is int:
                default_value = int(default_value)
            elif self.datatype is float:
                default_value = float(default_value)

            self._default_value = default_value
            self._value = default_value
            # self.set_value_description()

    def set_value_description(self, value_dict: Optional[dict] = None):
        description = self._description
        if self.depends_on is not None:
            try:
                value_dict_keys = list(value_dict.keys())
            except AttributeError:
                raise ValueError("`value_dict` must be a dictionary")

            if not all([key in self.depends_on for key in value_dict_keys]):
                raise ValueError("`value_dict` incomplete")

            if len(self.depends_on) == 2:
                value1, value2 = tuple(
                    [value_dict[key] for key in self.depends_on]
                )
                try:
                    description = description[value1]
                except KeyError:
                    description = description["default"]
                try:
                    description = description[value2]
                except KeyError:
                    description = description["default"]
            else:
                value1 = value_dict[self.depends_on[0]]
                try:
                    description = description[value1]
                except KeyError:
                    description = description["default"]
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
        num = format_parameter(fmt)
        return num


class DiscreteParameter(Parameter):
    def __init__(
        self,
        name: str,
        valid_range: tuple,
        description: dict,
        depends_on: Optional[tuple] = None,
        required: bool = True,
        missing_value: Optional[int] = -9,
    ):

        super(DiscreteParameter, self).__init__(
            name=name,
            datatype=int,
            discrete=True,
            valid_range=valid_range,
            description=description,
            depends_on=depends_on,
            scale=None,
            required=required,
            missing_value=missing_value,
        )

    def check_value(self, value):
        if not float(value).is_integer():
            raise ValueError
        value = int(value)
        if not value in self.valid_range:
            raise ValueError
        self.value = value


class ContinuousParameter(Parameter):
    def __init__(
        self,
        name: str,
        datatype: type,
        valid_range: tuple,
        description: Union[str, tuple],
        depends_on: Optional[tuple] = None,
        scale: Optional[int] = 2,
        required: bool = True,
        missing_value: Optional[int] = -9,
    ):

        super(ContinuousParameter, self).__init__(
            name=name,
            datatype=datatype,
            discrete=False,
            valid_range=valid_range,
            description=description,
            depends_on=depends_on,
            scale=scale,
            required=required,
            missing_value=missing_value,
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

    # def set_description(self, planting=None, subkind=None):
    #     description = self.select_description(planting, subkind)
    #     description = description[self.value]
    #     if self.required and self.value == self.missing_value:
    #         if isinstance(description, tuple):
    #             description = description[1]
    #     return description
