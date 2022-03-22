# PROGRAM LIST
- [apcp_cumulative_amount.py](./apcp_cumulative_amount.py): calcurate apcp(Total precipitation) and plot.

Asuming that ncfile1 is younger than ncfile2

```shell
python3 apcp_cumulateive_amount.py --file <apcp_ncfile1> <apcp_ncfile2> --tfile <troposphere_ncfile>
```
- [apcp.py](./apcp.py): Plot GPV initialdata's apcp and plot.

```shell
python3 apcp.py --file <gpv_initialdata_apcp_ncfile>
```
- [diff_upper_lower_wind.py](./diff_upper_lower_wind.py): Calcurate the difference between 300 hPa and 850 hPa wind and plot.

```shell
python3 diff_upper_lower_wind.py --file <troposphere_ncfile>
```
- [eqv_ptntl_temperature.py](./eqv_ptntl_temperature.py): Calcurate equivarent temparature and plot.

```shell
python3 eqv_ptntl_temperature.py --file <troposphere_ncfile>
```
- [grad_pt.py](./grad_pt.py), [grad_t.py](./grad_t.py): Calcurate gradient of potential temparature, temparature and plot.

```shell
python3 gradpt.py --file <troposphere_ncfile>
```
- [jet.py](./jet.py): Calcurate 300 hPa wind vector size and plot.

```shell
python3 jet.py --file <troposphere_ncfile>
```
- [prmsl_temp_wind.py](./prmsl_temp_wind.py): Plot sea level pressure, temparature, wind.

```shell
python3 prmsl_temp_wind.py --file <surface_ncfile>
```
- [upper_air.py](./upper_air.py): Plot 850 500 300 hPa temparature, geopotential height, wind.

```shell
python3 upper_air.py --file <troposphere_ncfile>
```
- [upper_air_humidity.py](./upper_air_humidity.py): Plot 850 500 300 hPa humidity.

```shell
python3 upper_air_humidity.py --file <troposphere_ncfile>
```
- [ptl_vrt.py](./ptl_vrt.py): Calucurate equivarent potential temparature and plot.

```shell
python3 ptl_vrt.py --file <troposphere_ncfile>
```
- [ptl_vrt_nh.py](./ptl_vrt_nh.py): [ptl_vrt.py](./ptl_vrt.py)'s plot style alternative version.![example](./example/example_nh.png)

```shell
python3 ptl_vrt_nh.py --file <troposphere_ncfile>
```
- [diff_ptl_vrt_nh.py](./diff_ptl_vrt_nh.py): calcurate difference between ncfile1 ando ncfile2 equivarent potential temparature and plot.
Asuming that ncfile1 is younger than ncfile2

```shell
python3 ptl_vrt.py --file <troposphere_ncfile1> <troposphere_ncfile2>
```
