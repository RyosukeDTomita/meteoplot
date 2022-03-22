# coding: utf-8
"""
Name: readnc.py

read netcdf file and cut near japan area.

example:
    from ncmagics import readnc

Authore: Ryosuke Tomita
Date: 2021/12/06
"""
from typing import Tuple
import dataclasses
import numpy as np
from netCDF4 import Dataset
import xarray as xr


@dataclasses.dataclass
class CalcPhysics:
    """CalcPhysics.
    """
    ncfile: str

    def __post_init__(self):
        """__post_init__.
        """
        self.dataset = Dataset(self.ncfile)

        # set variable name.
        self.variables_name_level = None
        for dim in self.dataset.dimensions:
            if   self.dataset[dim].axis == "Y":
                self.variables_name_lat = dim
            elif self.dataset[dim].axis == "X":
                self.variables_name_lon = dim
            elif self.dataset[dim].axis == "Z":
                self.variables_name_level = dim
            else:
                continue

        # check data is 3D or 2D
        try:
            isobaric_surface = np.array(self.dataset.variables[self.variables_name_level])
            isobaric_surface_key = [str(int(level)) for level in isobaric_surface]
            isobaric_value = list(range(len(isobaric_surface)))
            self.isobaric_surface_dict = dict(zip(isobaric_surface_key, isobaric_value))
            if "lev" in self.variables_name_level:
                self.data_dims = "3D"
            else:
                self.data_dims = "2D"
        except KeyError:
            self.data_dims = "2D"

        self.jp_mask: np.ma.core.MaskedArray
        self.len_jp_lat: int
        self.len_jp_lon: int

    def _cut_near_japan_area(self, lat: np.ndarray, lon: np.ndarray):
        """_cut_near_japan_area.

        Args:
            lat (np.ndarray): lat
            lon (np.ndarray): lon
        """
        lon_2d, lat_2d = np.meshgrid(lon, lat)
        self.jp_mask = ((lon_2d >= 110) & (lon_2d <= 180) & (lat_2d >= 20) & (lat_2d <= 60))

        lat_gt20_lt60 = ((lat >= 20) & (lat <= 60))
        lon_gt110_lt180 = ((lon >= 110) & (lon <= 180))
        jp_lat = lat[lat_gt20_lt60]
        jp_lon = lon[lon_gt110_lt180]
        self.len_jp_lat = len(jp_lat)
        self.len_jp_lon = len(jp_lon)
        return jp_lat, jp_lon

    def get_lat_lon(self) -> Tuple[np.ndarray, np.ndarray]:
        """get_lat_lon.
        Args:

        Returns:
            Tuple[np.ndarray, np.ndarray]:
        """
        lat = self.dataset.variables[self.variables_name_lat][:]
        lon = self.dataset.variables[self.variables_name_lon][:]

        jp_lat, jp_lon = self._cut_near_japan_area(lat, lon)
        return np.array(jp_lat), np.array(jp_lon)

    def get_lat_lon_xr(self) -> Tuple[xr.DataArray, xr.DataArray]:
        """get_lat_lon_xr.

        Args:

        Returns:
            Tuple[xr.DataArray, xr.DataArray]:
        """
        self.dataset_xr = xr.open_dataset(self.ncfile)
        lat = self.dataset_xr[self.variables_name_lat]
        lon = self.dataset_xr[self.variables_name_lon]

        jp_lat, jp_lon = self._cut_near_japan_area(lat, lon)
        return jp_lat, jp_lon

    def get_parameter(self, params:str, ncfile=None, isobaric_surface=None) -> np.ndarray:
        """get_parameter.
        read netcdf file to get physical parameter.
        Warning: ncfile can be updated but lat, lon data cannot updated. 
        If you use netcdf file which is different lat lon data,
        remake Class instance.

            ncfile:
            isobaric_surface:

        Returns:
            np.ndarray:
        """

        # update ncfile.
        if ncfile is not None and self.ncfile != ncfile:
            self.ncfile = ncfile
            self.dataset.close()
            self.dataset = Dataset(self.ncfile)

        # select isobaric surface
        if isobaric_surface is not None:
            data_raw = self.dataset.variables[params][0][self.isobaric_surface_dict[str(isobaric_surface)]]
            self.data_dims = "2D"
        else:
            data_raw = self.dataset.variables[params][0]

        # erase not near japan area data.
        if  self.data_dims == "3D":
            data = []
            for data_2d in data_raw:
                data.append(
                        data_2d[np.where(self.jp_mask)].reshape(self.len_jp_lat, self.len_jp_lon)
                )
        elif self.data_dims == "2D":
            data = data_raw[np.where(self.jp_mask)].reshape(self.len_jp_lat, self.len_jp_lon)
        return np.array(data)
