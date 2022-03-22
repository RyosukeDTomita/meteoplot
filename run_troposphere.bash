#!/bin/bash
file_list=($(find ~/data_ini/troposphere -type f | sort))
for i in ${!file_list[@]};
do
    echo ${file_list[$i]}
    #python3 grad_t.py --file ${file_list[$i]}
    #python3 upper_air.py --file ${file_list[$i]}
    #python3 upper_air_humidity.py --file ${file_list[$i]}
    #python3 upper_air_humidity_nh.py --file ${file_list[$i]}
    python3 ptl_vrt_nh.py --file ${file_list[$i]}
done
