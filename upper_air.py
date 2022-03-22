# coding: utf-8
"""
Name: upper_lower_wind.py

Make upper level weather chart.

Usage: python3 upper_air.py --file <ncfile>

Author: Ryosuke Tomita
Date: 2021/11/25
"""
import argparse
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
    1. get args.
    2. Make CalcPhysics instance and get lat lon.
    3. read physical value.
    4. calcurate difference between temperature to dewpoint.
    5. plot data.
    """
    args = parse_args()

    meteo_tool = meteotool.MeteoTools(args["file"])
    lat, lon = meteo_tool.get_lat_lon()
    isobaric_surface = (850, 500, 300)
    label_max = (30, 0, "-30")
    lebel_min = (-30, -60, "-60")

    for i, pressure in enumerate(isobaric_surface):
        # get parameter
        temp_c = meteo_tool.get_parameter('t', isobaric_surface=pressure) - 273.15
        rh = meteo_tool.get_parameter('r', isobaric_surface=pressure)
        height_gpm = meteo_tool.get_parameter('gh', isobaric_surface=pressure)
        u_wind = meteo_tool.get_parameter('u', isobaric_surface=pressure)
        v_wind = meteo_tool.get_parameter('v', isobaric_surface=pressure)

        # calcurate difference between temperature to dewpoint.
        diff_temp_dewpoint = meteo_tool.cal_diff_temp_dewpoint(temp_c, rh, pressure)

        # plot
        jp_map = japanmap.JpMap()
        jp_map.contour_plot(lon, lat, height_gpm)
        jp_map.shade_plot(lon, lat, temp_c,
                label="temperature ($^\circ$C)",
                color_bar_label_max=label_max[i],
                color_bar_label_min=lebel_min[i],
                color_map_type="temperature"
        )
        jp_map.vector_plot(lon, lat, u_wind, v_wind,
                           vector_interval=5, vector_scale=10, mode="wind")
        if pressure == 850:
            jp_map.hatch_plot(lon, lat, diff_temp_dewpoint)
            jp_map.color_line(lon, lat, temp_c, line_value=-6, color='#0000ff')
            jp_map.color_line(lon, lat, temp_c, line_value=-9, color='#00ff00')
        if pressure == 500:
            jp_map.color_line(lon, lat, temp_c, line_value=-36, color='#b22222')
        outname = output_name(args["file"], pressure)
        print(outname)
        jp_map.save_fig(outname, str(pressure) + "hPa")


if __name__ == "__main__":
    main()
