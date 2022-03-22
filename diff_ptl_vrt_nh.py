# coding: utf-8
"""
Name: ptl_vrt.py

potential vorticity on the isentropic.

Usage: python3 ptl_vrt.py --file <ncfile> <ncfile2>

Author: Ryosuke Tomita
Date: 2022/2/5
"""
import argparse
import numpy as np
from metpy.units import units
from ncmagics import fetchtime, japanmap_nh, meteotool_nh


def parse_args() -> dict:
    """parse_args.
    set file path.

    Args:

    Returns:
        dict:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="set ncfile.",
                        action='append', type=str)
    p = parser.parse_args()
    args = {"file": p.file}
    return args


def cal_d_thita_dp(meteo_tool: meteotool_nh.MeteoTools, ptl_temp: np.ndarray, height_gpm: np.ndarray, isentropic: int) -> np.ndarray:

    ise_height_gpm_lower = meteo_tool.isentropic_surface_value(ptl_temp, height_gpm, isentropic-5)
    ise_pressure_lower = meteo_tool.gph_to_pressure(ise_height_gpm_lower)
    ise_height_gpm_upper = meteo_tool.isentropic_surface_value(ptl_temp, height_gpm, isentropic+5)
    ise_pressure_upper = meteo_tool.gph_to_pressure(ise_height_gpm_upper)
    return (ise_pressure_upper - ise_pressure_lower) / (10 * units.kelvin)


def pvu_gt_2(ise_ptl_vorticity: np.ndarray):
    return np.where(ise_ptl_vorticity > 2.0, True, np.nan)


def output_name(ncfile_1:str, ncfile_2: str, isentropic: int) -> str:
    """output_name.

    Args:
        ncfile (str): ncfile
        isentropic (int): isentropic

    Returns:
        str:
    """
    date_time_1 = fetchtime.fetch_time(ncfile_1)
    date_time_2 = fetchtime.fetch_time(ncfile_2)
    outname = f"{date_time_1}sub{date_time_2}ptl_vrt{str(isentropic)}"
    return outname


def main():
    """main.
    1. get args.
    2. Make CalcPhysics instance and get lat lon.
    3. read physical value.
    4. calcurate isentropic equivalent potential vorticity.
    5. plot data.
    """
    args = parse_args()

    meteo_tool = meteotool_nh.MeteoTools(args["file"][0])
    lat, lon = meteo_tool.get_lat_lon_xr()
    isentropic = 310

    ise_ptl_vrt_list = []
    for i in range(2):
        temp_k = meteo_tool.get_parameter('t', ncfile=args["file"][i])
        u_wind = meteo_tool.get_parameter('u')
        v_wind = meteo_tool.get_parameter('v')
        height_gpm = meteo_tool.get_parameter('gh')
        surface_pressure = meteo_tool.gph_to_pressure(height_gpm)[0]

        # convert to isentropic value.
        ptl_temp = meteo_tool.cal_potential_temperature(temp_k)
        ise_u_wind = meteo_tool.isentropic_surface_value(ptl_temp, u_wind, isentropic)
        ise_v_wind = meteo_tool.isentropic_surface_value(ptl_temp, v_wind, isentropic)

    # calcurate potential vorticity.
        d_thita_dp = cal_d_thita_dp(meteo_tool, ptl_temp,
                                    height_gpm, isentropic)
        ise_ptl_vorticity = meteo_tool.cal_ptl_vorticity(
                ise_u_wind, ise_v_wind, d_thita_dp, lat, lon)

        ise_ptl_vrt_list.append(ise_ptl_vorticity)

    ise_ptl_vorticity = ise_ptl_vrt_list[1] - ise_ptl_vrt_list[0]
    # plot data
    nh_map = japanmap_nh.NhMap()
    nh_map.shade_plot(lon, lat, ise_ptl_vorticity,
            label="potential vorticity (PVU)",
            color_bar_label_max=3,
            color_bar_label_min=-3,
            color_map_type="temperature",
    )
    outname = output_name(args["file"][1], args["file"][0], isentropic)
    nh_map.save_fig(outname, f'{str(isentropic)} K')


if __name__ == "__main__":
    main()
