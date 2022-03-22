# coding: utf-8
"""
Name: japanmap.py

Plot japan map using cartopy.

Usage: This is the module.

Author: Ryosuke Tomita
Date: 2021/09/08
"""
from typing import Union
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
#from matplotlib.colors import Normalize
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfea
#from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter


class NhMap:
    """NhMap.
    Make orthogonal map (north hemisphere).
    """

    def __init__(self, color=False):
        """__init__.

        Args:
            color:
        """
        self.fig = plt.figure(figsize=(36, 24), facecolor='w')
        self.ax = self.fig.add_subplot(1, 1, 1,
                #projection=ccrs.PlateCarree(central_longitude=0.0),
                projection=ccrs.Orthographic(90, 90), #日本が下に来るように90度時計回りに地形を回転
        )

        self.ax.set_global()
        self.ax.coastlines(lw=3.5) # coastline thickness

        # using axis lat,lon format
        dlon, dlat = 20, 20  # grid line interval.
        xticks = np.arange(-180, 180.1, dlon)
        yticks = np.arange(-90, 90.1, dlat)

        # land color,ocean color
        if color:
            #self.ax.add_feature(cfea.LAND, color='#98fb98')
            #self.ax.add_feature(cfea.OCEAN, color='#87cefa')
            self.ax.add_feature(cfea.LAND, color='#f5deb3')
            self.ax.add_feature(cfea.OCEAN, color='#afeeee')

        # grid setting
        grid = self.ax.gridlines(crs=ccrs.PlateCarree(),
                                 draw_labels=False,
                                 linewidth=1,
                                 alpha=0.7,
                                 color='k',)
        grid.xlocator = mticker.FixedLocator(xticks)
        grid.ylocator = mticker.FixedLocator(yticks)


        self.color_list = ['#0000ff', '#00ffff', '#008000', '#adff2f',
                           '#ffff00', '#ffd700', '#ffa500', '#ff0000',
                           '#c71585', '#ff1493', '#9400d3', '#00ced1',
                           '#556b2f', '#deb887', '#daa520', '#8b4513',
                           '#4b0082', '#ffffff',
                           ]

        self.plt_cnt = 0
        self.double_color_bar = False

    def plot_data(self, x, y, label: str, line=True):
        """plot_data.
        plot location data. plot type is dot.

        Args:
            x:
            y:
            label (str): label
            cnst_marker
        """
        plt.rcParams['font.size'] = 36 # label font size
        if line:
            linewidth = 4
            linestyle = "solid"
        else:
            #no line
            linewidth = 0
            linestyle = None
        self.ax.plot(x, y, 'bo',
                     label=label,
                     markersize=15,
                     color=self.color_list[self.plt_cnt],
                     markeredgewidth=1.6,
                     markeredgecolor='#000000',
                     linestyle=linestyle,
                     linewidth=linewidth,)
        self.plt_cnt += 1

    def plot_value(self, x, y, z):
        """plot_value.
        plot z value on japan map. x, y are location data.

        Args:
            x:
            y:
            z:
        """

        for i in range(len(x)):
            self.ax.plot(x[i], y[i], marker=str(f'${z[i]:.2f}$'), markersize=90, color='k')

    def plot_prmsl_circle(self, x, y, z):
        """plot_value.
        plot z value on japan map. x, y are location data.

        Args:
            x:
            y:
            z:
        """

        for i in range(len(x)):
            scale = (1030 - z[i]) // 3
            self.ax.plot(x[i], y[i], 'bo',
                         markersize=15+scale,
                         color=self.color_list[self.plt_cnt-1],
                         markeredgewidth=1.6,
                         markeredgecolor='#000000',)

    def contour_plot(self, x, y, z, contour_type=None):
        """contour_plot.

        Args:
            x:
            y:
            z:
        """
        X, Y = np.meshgrid(x, y)
        if contour_type == "pressure":
            contour = self.ax.contour(X, Y, z, colors="black",
                                      levels=list(range(900, 1040, 4)),
                                      linewidths=3.0,
                                      transform=ccrs.PlateCarree(),
                    )
        else:
            contour = self.ax.contour(X, Y, z,
                                      colors="black",
                                      linewidths=3.0,
                                      transform=ccrs.PlateCarree(),
                                      )
        self.ax.clabel(contour, fontsize=36, fmt='%1.1f')

    def color_line(self, x, y, z, line_value: Union[int, float], color="blue"):
        """color_line.

        Args:
            x:
            y:
            z:
            line_value (Union[int, float]): line_value
            color:
        """
        X, Y = np.meshgrid(x, y)
        contour = self.ax.contour(X, Y, z,
                                  colors=color,
                                  levels=[line_value],
                                  linewidths=10.0,
                                  linestyles='dashed',
                                  transform=ccrs.PlateCarree(),
                                  )
        self.ax.clabel(contour, fontsize=48, fmt='%1.1f')

    def gray_shade(self, x, y, z, label: str,
                   color_bar_label_max=1.0,
                   color_bar_label_min=0.0,
                   ):
        if self.double_color_bar:
            shrink_ratio = 0.56
        else:
            shrink_ratio = 0.7
        ticks = list(np.linspace(color_bar_label_min,
                                 color_bar_label_max,
                                 5))
        plt.rcParams['font.size'] = 36
        x_2d, y_2d = np.meshgrid(x, y)
        hatch = self.ax.contourf(x_2d, y_2d, z,
                                 hatches=['-'*2, '/'*3, '\\'*3, '+'*2],
                                 cmap='gray_r',
                                 alpha=0.4,
                                 vmax=color_bar_label_max,
                                 vmin=color_bar_label_min,
                                 extend='both',
                                 transform=ccrs.PlateCarree(),
                                 )
        #hatch.set_clim(0, 1)
        color_bar = plt.colorbar(hatch,
                                 orientation="vertical",
                                 ticks=ticks,#[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                                 shrink=shrink_ratio,)
        color_bar.set_label(label, fontsize=36)

    def shade_plot(self, x, y, z, label: str,
                   color_bar_label_min=None,
                   color_bar_label_max=None,
                   color_map_type="kishotyo",
                   double_color_bar=False):
        """shade_plot.
        make color map.
        Args:
            x:
            y:
            z:
            label (str): label
            color_bar_label_min:
            color_bar_label_max:
        """
        def _get_jmacmap():
            """_get_jmacmap.
            """
            jmacolors=np.array([
                [242, 242, 242, 1], # white
                [160, 210, 255, 1], # light blue
                [33, 140, 255, 1], # aqua
                [0, 65, 255, 1], # blue
                [250, 245, 0, 1], # yellow
                [255, 153, 0, 1], # orange
                [255, 40, 0, 1], # red
                [180, 0, 104, 1]], # dark red
                dtype=np.float)
            jmacolors[:,:3] /= 256
            jmacmap=LinearSegmentedColormap.from_list("jmacmap2",colors=jmacolors)
            return jmacmap

        def _get_tempcmap():
            """_get_tempcmap.
            """
            tempcolors=np.array([
                [160, 0, 200, 1], # puple
                [0, 65, 255, 1], # blue
                [33, 140, 255, 1], # aqua
                [160, 210, 255, 1], # light blue
                [242, 242, 242, 1], # white
                [250, 245, 0, 1], # yellow
                [255, 153, 0, 1], # orange
                [255, 40, 0, 1], # red
                [180, 0, 104, 1]] # dark red
                ,dtype=np.float)
            tempcolors[:,:3] /= 256
            tempcmap=LinearSegmentedColormap.from_list("tempcmap",colors=tempcolors)
            return tempcmap

        # initial setting of shade
        if double_color_bar:
            shrink_ratio = 0.56
            self.double_color_bar = True
        else:
            shrink_ratio = 0.7

        plt.rcParams['font.size'] = 36
        X, Y = np.meshgrid(x, y)
        if   color_map_type == "diff":
            color_map = "RdBu_r"
        elif color_map_type == "temperature":
            color_map = _get_tempcmap()
        elif (color_map_type is not None) and (color_map_type not in ("temperature", "diff", "kishotyo")):
            color_map = color_map_type
        else:
            color_map = _get_jmacmap()

        # auto color bar range(using for test).
        if (color_bar_label_min is None) or (color_bar_label_max is None):
            shade = self.ax.pcolormesh(X, Y, z, cmap=color_map,
                    transform=ccrs.PlateCarree(),
                    )
            color_bar = plt.colorbar(shade,
                                     orientation="vertical",
                                     shrink=shrink_ratio,
                                     extend="both",
            )
        #color bar max min are assigned.
        else:
            shade = self.ax.pcolormesh(X, Y, z,
                    cmap=color_map,
                    transform=ccrs.PlateCarree(),
                    #transform=ccrs.RotatedPole(pole_longitude=-90, pole_latitude=90)
                    )
                                      # norm=Normalize(vmin=color_bar_label_min, vmax=color_bar_label_max))

            shade.set_clim(color_bar_label_min, color_bar_label_max) #color bar range.
            color_bar = plt.colorbar(shade,
                                     orientation="vertical",
                                     shrink=shrink_ratio,
                                     extend="both",
            )
        color_bar.set_label(label, fontsize=36,)

    def _skip_value(self, array, len_x: int, len_y: int, vector_interval: int, lat):
        """skip_value.
        used in vector_plot()

        Args:
            array:
            len_x (int): len_x
            len_y (int): len_y
            vector_interval (int): vector_interval
        """
        skiped_array = [
            array[i][j]
            for i in range(len_y)
            for j in range(len_x)
            if i % vector_interval == 0 and j % vector_interval == 0
        ]
        #skiped_array = []
        #for i in range(len_y):
        #    for j in range(len_x):
        #        if lat[i] > 0:
        #            scale = 1 + math.sqrt(math.cos(math.radians(lat[i])))
        #        else:
        #            scale = 1
        #        if (i % vector_interval == 0) and (j % math.ceil(scale * vector_interval) == 0):
        #            skiped_array.append(array[i][j])
        return np.array(skiped_array)

    def vector_plot(self, x, y, u, v, vector_interval: int, vector_scale, mode=None):
        """vector_plot.
        make vector map.
        use _skip_value()

        Args:
            x:
            y:
            u:
            v:
            vector_interval (int): vector_interval
            vector_scale:
        """

        x_2d, y_2d = np.meshgrid(x, y)
        u_skipped = self._skip_value(u, len(x), len(y), vector_interval, y)
        v_skipped = self._skip_value(v, len(x), len(y), vector_interval, y)
        x_2d_skipped = self._skip_value(x_2d, len(x), len(y), vector_interval, y)
        y_2d_skipped = self._skip_value(y_2d, len(x), len(y), vector_interval, y)
        if mode == "wind":
            self.ax.barbs(x_2d_skipped, y_2d_skipped, u_skipped, v_skipped,
                    transform=ccrs.PlateCarree(),
                    length=7,
            )
        else:
            # headlengthがheadaxislengthより大きく設定されると矢印がひし形に近づいていく。
            self.ax.quiver(x_2d_skipped, y_2d_skipped, u_skipped, v_skipped,
                    angles='uv',
                    scale_units='xy',
                    scale=vector_scale,
                    width=0.005,
                    headwidth=4, headlength=4, headaxislength=3.5,
                    transform=ccrs.RotatedPole(pole_longitude=0, pole_latitude=90)
                    #transform=ccrs.PlateCarree(),
           )
    def hatch_plot(self, x, y, z, alpha=0.3):
        """hatch_plot.
        https://matplotlib.org/stable/gallery/images_contours_and_fields/contourf_hatching.html
        Args:
            x:
            y:
            z:
        """
        x_2d, y_2d = np.meshgrid(x, y)
        self.ax.contourf(x_2d, y_2d, z,
                hatches='.',
                cmap='gray',
                alpha=alpha,
                transform=ccrs.PlateCarree(),
        )

    def hatch_plot_2(self, x, y, z):
        """hatch_plot.

        Args:
            x:
            y:
            z:
        """
        x_2d, y_2d = np.meshgrid(x, y)
        self.ax.contourf(x_2d, y_2d, z, hatches='*',cmap='pink', alpha=0.8)

    def save_fig(self, outname: str, title=None):
        """save_fig.
        save figure.

        Args:
            outname (str): outname
            title (str): title
        """
        self.ax.set_title(title, fontsize=32)
        bar_, label = self.ax.get_legend_handles_labels()
        self.ax.legend(bar_, label, loc='upper left',
                       borderaxespad=0, bbox_to_anchor=(1.05, 1))
        self.fig.savefig(outname, bbox_inches="tight", pad_inches=0.5)
        plt.close()
