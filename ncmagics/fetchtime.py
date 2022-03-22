# codng: utf-8
"""
Name: fetchtime.py

Read netcdf file "time" to make output name.

Usage: This is the module.

Author: Ryosuke Tomita
Date: 2021/12/20
"""
import netCDF4


def fetch_time(ncfile: str) -> str:
    data_set = netCDF4.Dataset(ncfile, 'r')
    time = data_set.variables["time"]
    date_time = str(netCDF4.num2date(time[0], time.units)).replace(" ", "_")[:13]
    return date_time
