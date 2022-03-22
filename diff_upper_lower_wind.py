# coding: utf-8
"""
Name: diff_upper_lower_wind.py

calcurate the difference between upper wind and lower wind.

Usage:

Author: Ryosuke Tomita
Date: 2021/11/25
"""
import argparse
import numpy as np
from ncmagics import fetchtime, japanmap, meteotool


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


def vector_size(u_wind: np.ndarray, v_wind: np.ndarray) -> np.ndarray:
    return (u_wind **2 + v_wind **2) ** 0.5


def output_name(ncfile: str, upper_pressure: int, lower_pressure):
    """output_name.

    Args:
        ncfile (str): ncfile
        upper_pressure (int): upper_pressure
        lower_pressure:
    """
    date_time = fetchtime.fetch_time(ncfile)
    outname = f'{date_time}_wind_{str(upper_pressure)}-{str(lower_pressure)}'
    return outname


def main():
    """main.
    """
    args = parse_args()

    # read ncfile
    meteo_tool = meteotool.MeteoTools(args["file"])
    lat, lon = meteo_tool.get_lat_lon()
    isobaric_surface = (250, 850)

    u_wind_list = []
    v_wind_list = []
    for pressure in isobaric_surface:
        u_wind_list.append(meteo_tool.get_parameter('u', isobaric_surface=pressure))
        v_wind_list.append(meteo_tool.get_parameter('v', isobaric_surface=pressure))

    # sub 850 hPa - 250 hPa wind.
    diff_u_wind = np.array(u_wind_list[0]) - np.array(u_wind_list[1])
    diff_v_wind = np.array(v_wind_list[0]) - np.array(v_wind_list[1])

    diff_wind_size = vector_size(diff_u_wind, diff_v_wind)

    # plot
    jp_map = japanmap.JpMap()
    jp_map.shade_plot(lon, lat, diff_wind_size,
            label="upper-lower wind (m/s)",
            color_bar_label_max=80,
            color_bar_label_min=10,
    )
    jp_map.vector_plot(lon, lat, diff_u_wind, diff_v_wind,
            vector_interval=5, vector_scale=10)
    outname = output_name(args["file"], isobaric_surface[0], isobaric_surface[1])
    jp_map.save_fig(outname, f'{isobaric_surface[0]}-{isobaric_surface[1]} hPa')


if __name__ == "__main__":
    main()
