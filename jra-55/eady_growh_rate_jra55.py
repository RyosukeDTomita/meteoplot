# coding: utf-8
"""
Name: eady_growth_rate.py

Calcurate eady_growth rate.

example: python3 eady_growth_rate.py --file <ncfile>

Author: Ryosuke Tomita
Date: 2021/10/22
"""
import argparse
import numpy as np
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


def cal_brunt_vaisala_frequency(d_ln_theta: np.ndarray, d_z: np.ndarray) -> np.ndarray:
    """cal_brunt_vaisala_frequency.
    brunt vaisala frequency [s^-2]
    N^2 = (g/theta) * (d_theta/dz)

    Args:
        d_ln_theta (np.ndarray): d_ln_theta
        d_z (np.ndarray): d_z

    Returns:
        np.ndarray:
    """
    gravity = 9.8
    N = np.sqrt(gravity * d_ln_theta / np.array(d_z))

    return N


def cal_eady_growh_rate(N: np.ndarray, d_u: np.ndarray, d_z: np.ndarray,
                        lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    """cal_eady_growh_rate.
    Eady growth rate [day^(-1)]
    sigma = 0.31 * (f/N) |round_u/round_z|
    N: brunt vaisala frequency calcurated by cal_brunt_vaisala_frequency()

    Args:
        N (np.ndarray): N
        d_u (np.ndarray): d_u
        d_z (np.ndarray): d_z
        lat (np.ndarray): lat
        lon (np.ndarray): lon

    Returns:
        np.ndarray:
    """
    omega = 6.28 / 86400
    _, lat_2d = np.meshgrid(lon, lat)
    f = 2 * omega * np.sin(np.radians(lat_2d))

    sigma = 0.31 * (f/N) * np.abs(d_u/d_z) * 3600 * 24
    print(np.mean(sigma))
    return sigma


def main():
    """main.
    1. get args.
    2. Make CalcPhysics instance.
    3. get 700 hPa and 800 hPa 's physical values.
    4. calcurate eady_growth_rate.
    5. plot.
    """
    #gh_file = "/home/tomita/jra55/isobaric_surface/geo_p/anl_p125_hgt.202001_nc"
    #u_file = "/home/tomita/jra55/isobaric_surface/wind/anl_p125_ugrd.202001_nc"
    #tfile = "/home/tomita/jra55/isobaric_surface/temp/anl_p125_tmp.202001_nc"
    gh_file = "/home/tomita/jra55/isobaric_surface/geo_p/anl_p125_hgt.202101_nc"
    u_file = "/home/tomita/jra55/isobaric_surface/wind/anl_p125_ugrd.202101_nc"
    tfile = "/home/tomita/jra55/isobaric_surface/temp/anl_p125_tmp.202101_nc"

    meteo_tool = meteotool.MeteoTools(gh_file)
    lat, lon = meteo_tool.get_lat_lon()

    temperature_k, gh, u_wind, w_wind, potential_temperature = [], [], [], [], []
    for pressure in (70000, 85000):
        gh.append(
            (meteo_tool.get_parameter('gh', isobaric_surface=pressure, ncfile=gh_file) +
            meteo_tool.get_parameter('gh', isobaric_surface=pressure, ncfile=gh_file.replace("202101", "202012"))) / 2
        )
        u_wind.append(
            (meteo_tool.get_parameter('u', isobaric_surface=pressure, ncfile=u_file) +
            meteo_tool.get_parameter('u', isobaric_surface=pressure, ncfile=u_file.replace("202101", "202012"))) / 2
        )
        #w_wind.append(meteo_tool.get_parameter('w', isobaric_surface=pressure))

        # calcurate potential_temperature
        temperature_k = (meteo_tool.get_parameter('t', isobaric_surface=pressure, ncfile=tfile) +  meteo_tool.get_parameter('t', isobaric_surface=pressure, ncfile=tfile.replace("202101", "202012")) / 2)
        potential_temperature.append(meteo_tool.cal_potential_temperature(temperature_k, pressure))

    # calcurate brunt vaisala frequency
    d_z = gh[0] - gh[1]
    d_ln_theta = (np.log(np.array(potential_temperature[0]))
        - np.log(np.array(potential_temperature[1])))
    N = cal_brunt_vaisala_frequency(d_ln_theta, d_z)

    # calcurate Eady growth rate.
    d_u = u_wind[0] - u_wind[1]
    sigma = cal_eady_growh_rate(N, d_u, d_z, lat, lon)

    # plot data
    jp_map = japanmap.JpMap()
    jp_map.contour_plot(lon, lat, sigma)
    jp_map.shade_plot(lon, lat, sigma, label="eady growth rate (day$^{-1}$)", color_bar_label_min=0, color_bar_label_max=1,)
    jp_map.save_fig("sigma", "Eady growth rate (day$^{-1}$)")


if __name__ == "__main__":
    main()
