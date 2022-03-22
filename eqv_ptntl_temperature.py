# coding: utf-8
"""
Name: eqv_ptntl_temperature.py

Calcurate equivalent_potential_temperature.

example: python3 eqv_ptntl_temperature.py --file <ncfile>

Author: Ryosuke Tomita
Date: 2021/10/22
"""
import argparse
import re
from ncmagics import japanmap, meteotool


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


def output_name(ncfile, isobaric_surface) -> str:
    """output_name.

    Args:
        ncfile:
        isobaric_surface:

    Returns:
        str:
    """
    ncfile_has_datetime = re.search('[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}', ncfile)
    if ncfile_has_datetime:
        forecast_time  = ncfile_has_datetime.group()
    else:
        raise Exception("ncfile doesn't have datetime data.")
    outname = (forecast_time + "ept_" + str(isobaric_surface))
    return outname


def main():
    """main.
    """
    args = parse_args()

    meteo_tool = meteotool.MeteoTools(args["file"])
    lat, lon = meteo_tool.get_lat_lon()

    isobaric_surface = 850

    # calcurate equivalent_potential_temperature
    temperature_k = meteo_tool.get_parameter('t', isobaric_surface=isobaric_surface)
    rh = meteo_tool.get_parameter('r', isobaric_surface=isobaric_surface)
    eqv_potential_temperature = meteo_tool.cal_eqv_potential_temperature(temperature_k, rh, isobaric_surface)

    # other parameter
    u_wind = meteo_tool.get_parameter('u', isobaric_surface=isobaric_surface)
    v_wind = meteo_tool.get_parameter('v', isobaric_surface=isobaric_surface)
    height_gpm = meteo_tool.get_parameter('gh', isobaric_surface=isobaric_surface)

    # plot
    jp_map = japanmap.JpMap()
    jp_map.contour_plot(lon, lat, height_gpm)
    jp_map.shade_plot(lon, lat, eqv_potential_temperature,
        label="equivalent potential temperature (K)",
        color_bar_label_max=350,
        color_bar_label_min=250,
        color_map_type="temperature")
    jp_map.vector_plot(lon, lat, u_wind, v_wind,
                            vector_interval=5, vector_scale=10)
    outname = output_name(args["file"], isobaric_surface)
    jp_map.save_fig(outname, str(isobaric_surface) + "hPa")


if __name__ == "__main__":
    main()
