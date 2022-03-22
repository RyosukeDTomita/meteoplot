# coding: utf-8
"""
Name:

plot cumulative amount.

example: python3 apcp_cumulateive_amount.py --file <ncfile1> <ncfile2>
Asuming that ncfile1 is younger than ncfile2

Author: Ryosuke Tomita
Date: 2021/10/28
"""
import argparse
import re
from datetime import datetime
from ncmagics import fetchtime, japanmap, meteotool


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
    parser.add_argument("-t", "--tfile", help="set ncfile (troposphere).",
                        type=str)
    p = parser.parse_args()
    args = {"file": p.file, "tfile": p.tfile}
    return args


def output_name(file_list):
    def _extract_datetime(ncfile):
        date_time = fetchtime.fetch_time(ncfile)
        outname_part = datetime.strptime(date_time, "%Y-%m-%d_%H")
        return outname_part.strftime('%Y%m%d_%H')

    def _calcureate_time(datetime_list):
        before_time_obj = datetime.strptime(datetime_list[0], '%Y%m%d_%H')
        after_time_obj = datetime.strptime(datetime_list[1], '%Y%m%d_%H')
        diff_time = after_time_obj - before_time_obj
        return diff_time.days * 24 + diff_time.seconds // 3600

    outname = ("-".join([_extract_datetime(file_) for file_ in file_list]))
    return outname, _calcureate_time(outname.split("-"))


def main():
    """main.
    """
    args = parse_args()
    begin_event_file = args["file"][0]
    end_event_file = args["file"][1]
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
    cal_phys = meteotool.MeteoTools(begin_event_file)
    lat2, lon2 = cal_phys.get_lat_lon()
    apcp_data = []
    for file_ in begin_event_file, end_event_file:
        apcp_data.append(cal_phys.get_parameter("APCP_surface", ncfile=file_))
    diff_apcp = apcp_data[1] - apcp_data[0]

    # plot
    outname, cumulative_time = output_name(args["file"])
    jp_map = japanmap.JpMap()
    jp_map.shade_plot(lon2, lat2, diff_apcp,
            label=f'Precipitation (kg$m^2$)/{str(cumulative_time)}h',
            color_bar_label_max=60,
            color_bar_label_min=0,
            double_color_bar=True,
  ) # 6hour is 25, 48 hour is 60

    if args["tfile"] is not None:
        jp_map.color_line(lon, lat, temp_c_850, line_value=-6, color='#0000ff')
        jp_map.gray_shade(lon, lat, snow_ratio, "snow/(snow+rain)")
    jp_map.save_fig(outname, None)


if __name__ == "__main__":
    main()
