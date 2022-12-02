#!/usr/bin/env python3

import pandas as pd
import datetime


class ModelTime(object):

    def __init__(
            self,
            starttime,
            endtime,
            timedelta
    ):
        """Model time.

        Parameters
        ----------
        starttime : pandas.Timestamp
            Start time of the model simulation.
        endtime : pandas.Timestamp
            End time of the simulation.
        timedelta : pandas.Timedelta
            Model time step.
        """
        self._starttime = pd.Timestamp(starttime)
        self._endtime = pd.Timestamp(endtime)
        self._dt = pd.Timedelta(timedelta)
        if (endtime - starttime) % timedelta == datetime.timedelta(0):
            self._n_timesteps = (endtime - starttime) / timedelta
        else:
            raise ValueError(
                'Given endtime is not a multiple of timedelta'
            )
        self._times = pd.date_range(starttime, endtime, periods=self._n_timesteps + 1)
    #     # if show_number_of_timesteps:
    #     #     logger.info("number of time steps: " + str(self._n_timesteps))
    #     self.reset()

    # def reset(self):
    #     self._curr_time = self._times[0]
    #     self._timestep = 0
    #     self._month_index = 0
    #     self._year_index = 0

    # def setStartTime(self, date):
    #     self._startTime = date
    #     self._nrOfTimeSteps = 1 + (self.endTime - self.startTime).days

    # def setEndTime(self, date):
    #     self._endTime = date
    #     self._nrOfTimeSteps = 1 + (self.endTime - self.startTime).days

    # @property
    # def spinUpStatus(self):
    #     return self._spinUpStatus

    @property
    def starttime(self):
        """pandas.Timestamp: Model start time."""
        return self._starttime

    @property
    def endtime(self):
        """pandas.Timestamp: Model end time."""
        return self._endtime

    @property
    def dt(self):
        """pandas.Timedelta: Duration of each timestep."""
        return self._dt

    @property
    def values(self):
        return self._times

    @property
    def dayofyear(self):
        return self._times.dayofyear.values

    @property
    def day_of_year(self):
        return self._times.day_of_year.values

    @property
    def doy(self):
        return self.dayofyear
