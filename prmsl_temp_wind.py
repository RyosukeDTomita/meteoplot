# coding: utf-8
"""
Name: prmsl_temp_wind.py

plot pressure reduced to MSL (hpa), 2m temperature (celsius), 10m wind.

example: python3 prmsl_temp_wind.py --file <ncfile>

Author: Ryosuke Tomita
Date: 2021/10/22
"""
import argparse
import re
import numpy as np
from ncmagics import japanmap, readnc


def parse_args() -> dict:
    """parse_args.
    set file path.

    Args:

    Returns:
        dict:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="set ncfile.", type=str)
    p = parser.parse_args()
    args = {"file": p.file}
    return args


def output_name(ncfile):
    """output_name.

    Args:
        ncfile:
    """
    ncfile_has_datetime = re.search('[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}', ncfile)
    if ncfile_has_datetime:
        forecast_time  = ncfile_has_datetime.group()
    else:
        raise Exception("ncfile doesn't have datetime data.")
    outname = (forecast_time + "surface")
    return outname


def main():
    """main.
    1. get argument using parse_args()
    2. Make CalcPhysics's instance and get parameter value.
    3. plot data using japanmap.py
    """
    args = parse_args()

    cal_phys = readnc.CalcPhysics(args["file"])
    lat, lon = cal_phys.get_lat_lon()
    prmsl = cal_phys.get_parameter("prmsl") / 100
    u_wind = cal_phys.get_parameter("u10")
    v_wind = cal_phys.get_parameter("v10")
    surface_temp_c = cal_phys.get_parameter("t2m") - 273.15
    rh = cal_phys.get_parameter("r2")

    # plot
    jp_map = japanmap.JpMap()
    jp_map.contour_plot(lon, lat, prmsl, contour_type="pressure")
    #jp_map.shade_plot(lon, lat, surface_temp_c,
    #    label="2m temperature ($^\circ$C)",
    #    color_bar_label_max=30,
    #    color_bar_label_min=-30,
    #    color_map_type="temperature"
    #)
    jp_map.shade_plot(lon, lat, rh,
        label="relative humidity (%)",
        color_bar_label_max=100,
        color_bar_label_min=0,
        color_map_type="gray",
    )
    jp_map.vector_plot(lon, lat, u_wind, v_wind,
                       vector_interval=8, vector_scale=5)
    outname = output_name(args["file"])
    jp_map.save_fig(outname, "surface")


if __name__ == "__main__":
    main()
