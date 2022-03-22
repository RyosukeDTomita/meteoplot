# coding: utf-8
"""
Name: grad_pt.py

Calcurate equivalent_potential_temperature.

example: python3 grad_pt.py --file <ncfile>

Author: Ryosuke Tomita
Date: 2021/10/22
"""
import argparse
import xarray as xr
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


def np_to_xr(param_np: np.ndarray,
             lat: xr.DataArray, lon: xr.DataArray) -> xr.DataArray:
    """np_to_xr.

    Args:
        param_np (np.ndarray): param_np
        lat (xr.DataArray): lat
        lon (xr.DataArray): lon

    Returns:
        xr.DataArray:
    """
    param_xr = xr.DataArray(param_np,
            dims=("latitude", "longitude"),
            coords={"latitude": lat, "longitude": lon}
    )
    return param_xr


def output_name(ncfile:str, isobaric_surface: int) -> str:
    """output_name.

    Args:
        ncfile (str): ncfile
        isobaric_surface (str): isobaric_surface

    Returns:
        str:
    """
    date_time = fetchtime.fetch_time(ncfile)
    outname = (date_time + "grad_pt_" + str(isobaric_surface))
    return outname


def main():
    """main.
    """
    args = parse_args()

    meteo_tool = meteotool.MeteoTools(args["file"])
    lat, lon = meteo_tool.get_lat_lon_xr()

    isobaric_surface = (850 , 500, 300)
    for pressure in isobaric_surface:
        print(f"-----{pressure}------")

        # gradient of potential temperature [K/100km]
        tempe_k = meteo_tool.get_parameter('t', isobaric_surface=pressure)
        ptl_temp_k= meteo_tool.cal_potential_temperature(tempe_k, pressure)
        ptl_temp_k_xr = np_to_xr(ptl_temp_k, lat, lon)
        grad_pt = meteo_tool.gradient_size(ptl_temp_k_xr, "K") * 100000 # K/m -> K/100km

        # wind
        u_wind = meteo_tool.get_parameter('u', isobaric_surface=pressure)
        v_wind = meteo_tool.get_parameter('v', isobaric_surface=pressure)

        # plot
        jp_map = japanmap.JpMap()
        jp_map.contour_plot(lon, lat, ptl_temp_k)
        if pressure == 850:
            jp_map.shade_plot(lon, lat, grad_pt,
                label="gradient of potential temperature (K/100km)",
                color_bar_label_max=6,
                color_bar_label_min=2,
                color_map_type="YlOrBr",
            )
        else:
            jp_map.shade_plot(lon, lat, grad_pt,
                label="gradient of potential temperature (K/100km)",
                color_bar_label_max=6,
                color_bar_label_min=2,
                color_map_type="YlOrBr",
            )
        jp_map.vector_plot(lon, lat, u_wind, v_wind,
                           vector_interval=8, vector_scale=10)
        outname = output_name(args["file"], pressure)
        jp_map.save_fig(outname, str(pressure) + "hPa")


if __name__ == "__main__":
    main()
