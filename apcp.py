# coding: utf-8
"""
Name:

plot apcp (initialdata).

example: python3 apcp.py --file <ncfile>

Author: Ryosuke Tomita
Date: 2021/10/28
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
    parser.add_argument("-f", "--file", help="set ncfile (apcp).",
                        type=str)
    parser.add_argument("-t", "--tfile", help="set ncfile (troposphere).",
                        type=str)
    p = parser.parse_args()
    args = {"file": p.file, "tfile": p.tfile}
    return args


def output_name(ncfile):
    """output_name.

    Args:
        ncfile:
    """
    date_time = fetchtime.fetch_time(ncfile)
    outname = (date_time + "apcp")
    return outname


def main():
    """main.
    """
    args = parse_args()
    apcp_file = args["file"]
    troposphere_file = args["tfile"]

    if args["tfile"] is not None:
        meteo_tool = meteotool.MeteoTools(troposphere_file)
        lat, lon = meteo_tool.get_lat_lon()
        rh_surf = meteo_tool.get_parameter("r", isobaric_surface=1000)

        temp_c_850 = meteo_tool.get_parameter("t", isobaric_surface=850) - 273.15
        temp_k_surf = meteo_tool.get_parameter("t", isobaric_surface=1000)

        # calcurate wet bulb temperature
        snow_ratio = meteo_tool.snow_or_rain(
            temp_k_surf, rh_surf, isobaric_surface=1000)

    # apcpとtroposphereではlatが逆向きに入っているため緯度経度やjp_maskの使い回しができない。
    meteo_tool2 = meteotool.MeteoTools(apcp_file)
    lat2, lon2 = meteo_tool2.get_lat_lon()
    apcp = meteo_tool2.get_parameter("APCP_surface")

    # plot
    outname = output_name(apcp_file)
    jp_map = japanmap.JpMap()
    jp_map.shade_plot(lon2, lat2, apcp,
                      label=f'Precipitation (kg/$m^2$)/6h',
                      color_bar_label_max=20,
                      color_bar_label_min=0,
                      double_color_bar=True)
    if args["tfile"] is not None:
        jp_map.color_line(lon, lat, temp_c_850, line_value=-6, color='#0000ff')
        #jp_map.color_line(lon, lat, temp_c_850, line_value=-9, color='#00ff00')
        jp_map.gray_shade(lon, lat, snow_ratio,
                          "snow/(snow+rain)",)

    jp_map.save_fig(outname, None)


if __name__ == "__main__":
    main()
