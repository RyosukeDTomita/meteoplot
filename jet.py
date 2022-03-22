# coding: utf-8
"""
Name: diff_upper_lower_wind.py

Make upper level weather chart.

Usage: python3 upper_air.py --file <ncfile>

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
    """vector_size.

    Args:
        u_wind (np.ndarray): u_wind
        v_wind (np.ndarray): v_wind

    Returns:
        np.ndarray:
    """
    return (u_wind ** 2 + v_wind ** 2) ** 0.5


def output_name(ncfile: str, isobaric_surface: int) -> str:
    """output_name.

    Args:
        ncfile (str): ncfile
        isobaric_surface (int): isobaric_surface

    Returns:
        str:
    """
    date_time = fetchtime.fetch_time(ncfile)
    outname = (date_time + "_" + str(isobaric_surface))
    return outname


def main():
    """main.
    """
    args = parse_args()

    meteo_tool = meteotool.MeteoTools(args["file"])
    lat, lon = meteo_tool.get_lat_lon()
    isobaric_surface = (850, 500, 300)
    label_max = (30, 50, 80)
    lebel_min = (10, 20, 40)

    for i, pressure in enumerate(isobaric_surface):
        # get parameter
        height_gpm = meteo_tool.get_parameter('gh', isobaric_surface=pressure)
        u_wind = meteo_tool.get_parameter('u', isobaric_surface=pressure)
        v_wind = meteo_tool.get_parameter('v', isobaric_surface=pressure)
        wind_size = vector_size(u_wind, v_wind)

        jp_map = japanmap.JpMap()
        jp_map.contour_plot(lon, lat, height_gpm)
        jp_map.shade_plot(lon, lat, wind_size,
                label="wind speed (m/s)",
                color_bar_label_max=label_max[i],
                color_bar_label_min=lebel_min[i],
        )
        jp_map.vector_plot(lon, lat, u_wind, v_wind,
                           vector_interval=5,
                           vector_scale=15,
                           #mode="wind",
        )
        outname = output_name(args["file"], pressure)
        print(outname)
        jp_map.save_fig(outname, str(pressure) + "hPa")


if __name__ == "__main__":
    main()
