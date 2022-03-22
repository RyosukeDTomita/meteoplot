# coding: utf-8
"""
Name: upper_air_humidity.py

Make upper level weather chart.

Usage: python3 upper_air_humidity.py --file <ncfile>

Author: Ryosuke Tomita
Date: 2022/01/07
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

    for i, pressure in enumerate(isobaric_surface):
        # get parameter
        temp_c = meteo_tool.get_parameter('t', isobaric_surface=pressure) - 273.15
        rh = meteo_tool.get_parameter('r', isobaric_surface=pressure)
        height_gpm = meteo_tool.get_parameter('gh', isobaric_surface=pressure)
        u_wind = meteo_tool.get_parameter('u', isobaric_surface=pressure)
        v_wind = meteo_tool.get_parameter('v', isobaric_surface=pressure)

        jp_map = japanmap.JpMap()
        jp_map.contour_plot(lon, lat, height_gpm)
        jp_map.shade_plot(lon, lat, rh,
                          label="relative humidity (%)",
                          color_bar_label_max=100,
                          color_bar_label_min=0,
                          color_map_type="gray",
                          double_color_bar=False,)
        jp_map.hatch_plot(lon, lat,
                np.where(rh >= 80, True, np.nan),
                alpha=0.0,
        )
        jp_map.vector_plot(lon, lat, u_wind, v_wind,
                           vector_interval=5, vector_scale=10, mode="wind")
        if pressure == 850:
            jp_map.color_line(lon, lat, temp_c, line_value=-6, color='#0000ff')
        if pressure == 500:
            jp_map.color_line(lon, lat, temp_c, line_value=-36, color='#b22222')
        outname = output_name(args["file"], pressure)
        print(outname)
        jp_map.save_fig(outname, str(pressure) + "hPa")


if __name__ == "__main__":
    main()
