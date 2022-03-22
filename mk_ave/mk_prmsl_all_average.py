# coding: utf-8
"""
Name: mk_prmsl_all_average.py

Make all average data by two netcdf files.

Usage: python3 mk_prmsl_all_average.py -d <dir>

Author: Ryosuke Tomita
Date: 2021/11/11
"""
import argparse
from datetime import datetime, timedelta
import os
from os.path import abspath, dirname, join
import re
from netCDF4 import Dataset
import xarray as xr


def parse_args() -> dict:
    """Set directory path from stdin."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--dir", help="set directory which contained csv files.", type=str)
    p = parser.parse_args()
    args = {"dir": p.dir}
    return args


def mk_file_lists(root_dir, filter_) -> list:
    """Make ncfile list sorted by datetime order."""
    file_list = sorted([
        ncfile
        for ncfile in map(lambda ncfile: join(root_dir, ncfile) ,os.listdir(root_dir))
        if filter_ in ncfile
        if not "prmsl" in ncfile
    ])
    return file_list


def read_ncfile(ncfile, param):
    nc = Dataset(ncfile).variables[param][:]
    return nc


def mk_6h_ago_ncfile_name(ncfile):
    ncfile_has_datatime = re.search('[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}', ncfile)
    if ncfile_has_datatime:
        ncfile_datetime_part = ncfile_has_datatime.group()
        datetime_6h_ago = datetime.strptime(ncfile_datetime_part, "%Y-%m-%d_%H") + timedelta(hours=6)
        ncfile_datetime_part_6h_ago = datetime.strftime(datetime_6h_ago, "%Y-%m-%d_%H")
        ncfile_6h_ago = ncfile.replace(ncfile_datetime_part, ncfile_datetime_part_6h_ago)
    else:
        raise Exception("ncfile name has not have datatime data.")
    return ncfile_6h_ago


def save_netcdf(data, outname, rename=False):
    data.to_netcdf(outname)
    data.close()
    if rename:
        os.rename(outname, outname.replace("$", ""))


def mk_ave_file(prev_file, next_file, basic_file, param):
    data = xr.open_dataset(basic_file)
    prev_data_param = read_ncfile(prev_file, param)
    next_data_param = read_ncfile(next_file, param)
    ave_param_data = (prev_data_param + next_data_param) / 2

    #replace data
    data[param] = xr.where((data[param]), ave_param_data, data[param])

    if prev_file == basic_file:
        outname = mk_6h_ago_ncfile_name(prev_file)
        save_netcdf(data, outname)
    else:
        outname = basic_file + "$"
        save_netcdf(data, outname, rename=True)
        outname = basic_file

    return outname


def main():
    args = parse_args()
    root_dir = abspath(args["dir"])

    surface_file_list = mk_file_lists(root_dir, "surface-")

    # make troposphere average file.
    for i in range(len(surface_file_list)):
        if i == 0:
            continue
        print(surface_file_list[i])
        ave_t_file = mk_ave_file(surface_file_list[i-1], surface_file_list[i], surface_file_list[i-1], "u10")
        mk_ave_file(surface_file_list[i-1], surface_file_list[i], ave_t_file, "v10")
        mk_ave_file(surface_file_list[i-1], surface_file_list[i], ave_t_file, "t2m")
        mk_ave_file(surface_file_list[i-1], surface_file_list[i], ave_t_file, "r2")
        mk_ave_file(surface_file_list[i-1], surface_file_list[i], ave_t_file, "prmsl")
        mk_ave_file(surface_file_list[i-1], surface_file_list[i], ave_t_file, "sp")
        mk_ave_file(surface_file_list[i-1], surface_file_list[i], ave_t_file, "lcc")
        mk_ave_file(surface_file_list[i-1], surface_file_list[i], ave_t_file, "mcc")
        mk_ave_file(surface_file_list[i-1], surface_file_list[i], ave_t_file, "hcc")


if __name__ == "__main__":
    main()
