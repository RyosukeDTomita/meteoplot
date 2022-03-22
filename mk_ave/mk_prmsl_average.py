# coding: utf-8
"""
Name: mk_prmsl_average.py

Make average data by two netcdf files.
[Check]: new Netcdf file doesn't use scale_factor and add_offset.

Usage: python3 mk_prmsl_average.py -d <dir>

Author: Ryosuke Tomita
Date: 2021/09/29
"""
import argparse
from datetime import datetime, timedelta
import os
from os.path import abspath, join
import re
from numpy.ma.core import MaskedArray
from netCDF4 import Dataset
import xarray as xr


def parse_args() -> dict:
    """parse_args.
    Set directory path from stdin.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--dir", help="set directory which contained csv files.", type=str)
    prs = parser.parse_args()
    args = {"dir": prs.dir}
    return args


def mk_file_lists(root_dir: str, filter_: str) -> list:
    """mk_file_lists.
    Make ncfile list sorted by datetime order.

    Args:
        root_dir (str): root_dir
        filter_ (str): filter_

    Returns:
        list:
    """
    file_list = sorted([
        ncfile
        for ncfile in map(lambda ncfile: join(root_dir, ncfile) ,os.listdir(root_dir))
        if filter_ in ncfile
    ])
    return file_list


def read_ncfile(ncfile: str, param: str) -> MaskedArray:
    """read_ncfile.
    Return ncfile data sliced by "param".

    Args:
        ncfile (str): ncfile
        param (str): param

    Returns:
        numpy.ma.core.MaskedArray:
    """
    return Dataset(ncfile).variables[param][:]


def mk_6h_ago_ncfile_name(ncfile: str) -> str:
    """mk_6h_ago_ncfile_name.
    Make "ncfile" + 6h ago file name.

    Args:
        ncfile (str): ncfile

    Returns:
        str:
    """

    ncfile_has_datatime = re.search('[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}', ncfile)
    if ncfile_has_datatime:
        ncfile_datetime_part = ncfile_has_datatime.group()
        datetime_6h_ago = datetime.strptime(
            ncfile_datetime_part, "%Y-%m-%d_%H") + timedelta(hours=6)
        ncfile_datetime_part_6h_ago = datetime.strftime(datetime_6h_ago, "%Y-%m-%d_%H")
        ncfile_6h_ago = ncfile.replace(ncfile_datetime_part, ncfile_datetime_part_6h_ago)
    else:
        raise Exception("ncfile name has not have datatime data.")
    return ncfile_6h_ago


def save_netcdf(data, outname: str, rename=False):
    """save_netcdf.
    Save netcdf "data" to netcdf file named by "outname".

    Args:
        data: (numpy.ma.core.MaskedArray): data
        outname (str): outname
        rename: (bool): rename
    """
    data.to_netcdf(outname)
    data.close()
    if rename:
        os.rename(outname, outname.replace("$", ""))


def mk_ave_file(prev_file: str, next_file: str, basic_file: str, param: str) -> str:
    """mk_ave_file.
    Using read_ncfile(), mk_6h_ago_ncfile_name(), save_netcdf(),
    make average file.
    (f(t-6) + f(t+6))/2

    Args:
        prev_file (str): prev_file
        next_file (str): next_file
        basic_file (str): basic_file
        param (str): param

    Returns:
        str:
    """

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
    """main.
    1. Get argument (directory path) and convert to abspath.
    2. Make netcdf file list using mk_file_lists()
    3. Call mk_ave_file() to make average file.
    """
    args = parse_args()
    root_dir = abspath(args["dir"])

    prmsl_file_list = mk_file_lists(root_dir, "prmsl")

    # make prmsl average file.
    for i, ncfile in enumerate(prmsl_file_list):
        if i == 0:
            continue
        ave_prmsl_file = mk_ave_file(
            prmsl_file_list[i-1], prmsl_file_list[i], prmsl_file_list[i-1], "prmsl"
        )
        print(ncfile + "-->" + ave_prmsl_file)


if __name__ == "__main__":
    main()
