# coding: utf-8
"""
Name: meteotool.py

functions.

Usage:

Author: Ryosuke Tomita
Date: 2021/12/15
"""
import math
import numpy as np
import xarray as xr
import metpy.constants
import metpy.interpolate
from metpy.units import units
import metpy.calc as mpcalc
from ncmagics import readnc


class MeteoTools(readnc.CalcPhysics):
    """MeteoTools.
    """

    def cal_potential_temperature(self, temperature_k: np.ndarray,
                                  isobaric_surface=None) -> np.ndarray:
        """cal_potential_temperature.
        theta = Temperature * (P0/P)^0.29

        Args:
            temperature_k (np.ndarray): temperature_k
            isobaric_surface (int): isobaric_surface

        Returns:
            np.ndarray:
        """
        if isobaric_surface is None:
            ptl_temp = []
            isobaric_surface = sorted([
                int(pressure)
                for pressure in self.isobaric_surface_dict.keys()
        ], reverse=True)
            for pressure in isobaric_surface:
                ptl_temp.append(
                    mpcalc.potential_temperature(
                        pressure * units.mbar, temperature_k[self.isobaric_surface_dict[str(int(pressure))]] * units.kelvin
                    )
                )
        else:
            ptl_temp = mpcalc.potential_temperature(isobaric_surface * units.mbar, temperature_k * units.kelvin)
        return np.array(ptl_temp)

    def cal_diff_temp_dewpoint(self, temp_c: np.ndarray, rh: np.ndarray, isobaric_surface: int) -> np.ndarray:
        """cal_diff_temp_dewpoint.
        calcurate dewpoint and find the area
        which is the dewpoint - temperature = 湿数 < 3
        called humidity area.

        Args:
            temp_c (np.ndarray): temp_c
            rh (np.ndarray): rh
            isobaric_surface (int): isobaric_surface
        """
        # calcurate dewpoint
        mixing_ratio = mpcalc.mixing_ratio_from_relative_humidity(
                isobaric_surface* units.hPa, temp_c * units.celsius, rh * units.percent
        )
        vapor_pressure = self._cal_vapor_pressure(mixing_ratio, isobaric_surface)
        dewpoint = self._cal_dewpoint(vapor_pressure)
        diff_temp_dewpoint = np.array(temp_c * units.celsius - dewpoint)
        return np.where(diff_temp_dewpoint < 3.0, True, np.nan)

    def gradient_size(self, params_xr: xr.DataArray, unit: str) -> np.ndarray:
        """gradient_size.
        Using metpy.calc.gradient() calcurate gradient absorute size.
        This function use central difference calculus.

        Args:
            params_xr (xr.DataArray): params_xr
            unit (str): unit

        Returns:
            np.ndarray:
        """
        if   unit == "K":
            param_unit = units.kelvin
        elif unit == "C":
            param_unit = units.celsius
        else:
            raise Exception("unit is not valid")
        grad_x, grad_y = mpcalc.gradient(params_xr * param_unit)
        return (grad_x ** 2 + grad_y ** 2) ** 0.5
        #return grad_x, grad_y

    def snow_or_rain(self, temp_k: np.ndarray, rh: np.ndarray, isobaric_surface: int) -> np.ndarray:
        """snow_or_rain.
        Args:
            temp_k (np.ndarray): temp_k
            rh (np.ndarray): rh
            isobaric_surface (int): isobaric_surface

        Returns:
            np.ndarray:
        """
        # calcurate dew point
        mixing_ratio = self._cal_mixing_ratio(temp_k, rh, isobaric_surface)
        vapor_pressure = np.array(
                self._cal_vapor_pressure(mixing_ratio, isobaric_surface)
        )

        # calcurate wet buld temperature.
        temp_c = temp_k - 273.15
        tw = 0.584 * temp_c + 0.875 * vapor_pressure - 5.32
        s = [
            1 - 0.5 * np.e ** (-2.2 * (1.1 - tw[i][j]) ** 1.3)
            if tw[i][j] < 1.1
            else
            0.5 * np.e ** (-2.2 * (tw[i][j] - 1.1) ** 1.3)
            for i in range(len(tw))
            for j in range(len(tw[0]))
        ]
        s = np.array(s).reshape(len(tw), len(tw[0]))
        return s


    def cal_bulb_temp(self, temp_k: np.ndarray, rh: np.ndarray,
                      isobaric_surface: int) -> np.ndarray:
        """cal_bulb_temp.

        Args:
            temp_k (np.ndarray): temp_k
            rh (np.ndarray): rh
            isobaric_surface (int): isobaric_surface

        Returns:
            np.ndarray:
        """
        # calcurate dew point
        mixing_ratio = self._cal_mixing_ratio(temp_k, rh, isobaric_surface)
        vapor_pressure = self._cal_vapor_pressure(mixing_ratio, isobaric_surface)
        dew_point = self._cal_dewpoint(vapor_pressure)

        # calcurate wet buld temperature.
        pressure = np.zeros((81, 141)) + isobaric_surface

        tw = np.array(
                mpcalc.wet_bulb_temperature(
                    pressure * units.hPa, temp_k * units.kelvin, dew_point
                )
        ) - 273.15
        return tw

#----------equivalent potential temperature----------
    def _cal_mixing_ratio(self, temperature_k: np.ndarray, rh: np.ndarray,
                          isobaric_surface: int) -> np.ndarray:
        """cal_mixing_ratio.
        mixing ratio(水蒸気の混合比)

        Args:
            temperature_k (np.ndarray): temperature_k
            rh (np.ndarray): rh
            isobaric_surface (int): isobaric_surface

        Returns:
            np.ndarray:
        """
        mixing_ratio = mpcalc.mixing_ratio_from_relative_humidity(
            isobaric_surface * units.hPa, temperature_k * units.kelvin, rh * units.percent
        )
        return mixing_ratio

    def _cal_vapor_pressure(self, mixing_ratio: np.ndarray, isobaric_surface: int) -> np.ndarray:
        """cal_vapor_pressure.
        vapor pressure(水蒸気圧) [hPa]

        Args:
            isobaric_surface (int): isobaric_surface

        Returns:
            np.ndarray:
        """
        vapor_pressure = mpcalc.vapor_pressure(
            isobaric_surface * units.hPa, mixing_ratio
        )
        return vapor_pressure

    def _cal_dewpoint(self, vapor_pressure):
        """cal_dewpoint.
        calcurate dewpoint(露点温度) [K]
        """
        dewpoint = mpcalc.dewpoint(vapor_pressure)
        return dewpoint

    def cal_eqv_potential_temperature(self, temperature_k: np.ndarray, rh: np.ndarray, isobaric_surface: int) -> np.ndarray:
        """cal_eqv_potential_temperature.
        calcurate equivalent_potential_temperature(相当温位) [K]

        Args:
            temperature_k (np.ndarray): temperature_k
            isobaric_surface (int): isobaric_surface

        Returns:
            np.ndarray:
        """
        mixing_ratio = self._cal_mixing_ratio(temperature_k, rh, isobaric_surface)
        vapor_pressure = self._cal_vapor_pressure(mixing_ratio, isobaric_surface)
        dewpoint = self._cal_dewpoint(vapor_pressure)

        equivalent_potential_temperature = mpcalc.equivalent_potential_temperature(
            isobaric_surface * units.hPa, temperature_k * units.kelvin, dewpoint
        )
        return equivalent_potential_temperature


#----------potential vorticity on the isentropic----------
    def _reverse_z_index(self, array_3d: np.ndarray) -> np.ndarray:
        """_reverse_z_index.
        metpy.interpolate.interpolate_to_isosurface() assumes that
        highest vertical level (lowest pressure) is zeroth index.
        This function reverse array index.

        Args:
            array_3d (np.ndarray): array_3d

        Returns:
            np.ndarray:
        """
        return array_3d[::-1]

    def isentropic_surface_value(self, ptl_temp: np.ndarray, phys_val: np.ndarray,
                                 isentropic: int, reverse=True) -> np.ndarray:
        """isentropic_surface_value.

        Args:
            ptl_temp (np.ndarray): ptl_temp
            phys_val (np.ndarray): phys_val
            isentropic (int): isentropic
            reverse:

        Returns:
            np.ndarray:
        """
        if reverse:
            ptl_temp = self._reverse_z_index(ptl_temp)
            phys_val = self._reverse_z_index(phys_val)
        return (metpy.interpolate.interpolate_to_isosurface(ptl_temp, phys_val, isentropic))

    def gph_to_pressure(self, gph: np.ndarray) -> np.ndarray:
        """gph_to_pressure.
        convert geopotential height to pressure.

        Args:
            gph:
        """
        gp = (gph * units.gpm) * metpy.constants.earth_gravity
        height_m = mpcalc.geopotential_to_height(gp)
        pressure = mpcalc.height_to_pressure_std(height_m)
        return pressure

    def cal_ptl_vorticity(self, ise_u_wind: np.ndarray, ise_v_wind: np.ndarray, d_thita_dp: np.ndarray, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
        """cal_ptl_vorticity.
        isentropic potential vorticity barotoropic.
        PV = (f + zeta) / m
        m = - (round_p / round_thita) / g
        Unit is PVU (10**-6 K m**2 s**-1 kg**-1)

        Args:
            ise_u_wind (np.ndarray): ise_u_wind
            ise_v_wind (np.ndarray): ise_v_wind
            d_thita_dp (np.ndarray): d_thita_dp
            lat (np.ndarray): lat
            lon (np.ndarray): lon

        Returns:
            np.ndarray:
        """
        lon_2d, lat_2d = np.meshgrid(lon.values, lat.values)
        dx = 55.8 * math.cos(math.radians(45))
        m = -1 * d_thita_dp / metpy.constants.earth_gravity
        f = mpcalc.coriolis_parameter(lat_2d * units.degree)

        # vorticity
        ise_u_wind = xr.DataArray(ise_u_wind,
                dims=("latitude", "longitude"),
                coords={"latitude": lat, "longitude": lon}
        )
        ise_v_wind = xr.DataArray(ise_v_wind,
                dims=("latitude", "longitude"),
                coords={"latitude": lat, "longitude": lon}
        )
        vorticity = mpcalc.vorticity(ise_u_wind * units('m/s'), ise_v_wind * units('m/s'))
        ptl_vorticity = (f + vorticity) / (m)
        return ptl_vorticity * 10000
