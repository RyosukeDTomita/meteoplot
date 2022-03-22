#!/bin/bash
##########################################################################
# Name: getPrmsl.bash
#
# Prmsl is 海面更生気圧. In python library magics cannot calcurate netcdfData. So using cdo, we convert prmsl (Pa) to prmsl (hPa)
# And surface.nc is include different forecast time data. In this shell script, we separete into forecast times.
#
# Usage: ./getPrmsl.bash
#
# Author: Ryosuke Tomita
# Date: 2021/07/30
##########################################################################
function select_nc_type()
{
    select nctype in surface.nc troposphere.nc stratosphere.nc apcp.nc
    do
        echo $nctype
        break
    done
    return 0
}

function main(){
    if [ ! -d ./data ]; then mkdir data; fi
    readonly DIRPATH="${HOME}/winter"
    readonly DIRNAME=($(ls $DIRPATH))
    nctype=$(select_nc_type)
    for d in "${DIRNAME[@]}"
    do
        ncfile="${DIRPATH}/${d}/$nctype"
        Date=($(cdo infon $ncfile | sed 1d | grep -o '202.\{7\}' | grep -v ':' | grep -o '.*\-.*\-.*' | uniq))
        hour=(00 06 12 18)
        #echo ${Date[@]}
        for t in "${!Date[@]}"
        do
            dailyData="${ncfile%\.nc}-${Date[$t]}"
            cdo select,date=${Date[$t]} $ncfile $dailyData
            for h in "${!hour[@]}"
            do
                hourlyData="${dailyData}_${hour[$h]}"
                cdo select,hour="${hour[$h]}" $dailyData $hourlyData

                prmslData="${hourlyData}-prmsl"
                cdo select,name=prmsl $hourlyData $prmslData

                prmslhPaData="${prmslData}_hPa"
                cdo -b F64 divc,100 $prmslData $prmslhPaData
                rm $prmslData "${ncfile}-prmsl"
            done
            rm $dailyData
        done
    done
}

main
