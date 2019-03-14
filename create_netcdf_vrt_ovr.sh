#!/bin/bash

# example
#OVR_FIELDS="frequency count_wet count_clear"
OVR_FIELDS="bcdev"
#OVR_GLOB='*FYsummary.nc'
OVR_OUTPUT='.'
SENSORS="ls7"
# overview-build-all-vrt
# overview-resample-all
# overview-collate

# create yearly vrts
ncdf-yearly-vrt () {
    local field=$1
    local sensor=$2

    for y in {1986..2018}; do
        #y=2013

        # wet season summary vrts
        ## vrt_name=wofs_${y}-11_$((y + 1))-03_summary.vrt;

        # dry season summary vrts
        #vrt_name=wofs_${y}-04_${y}-10_summary.vrt;

        vrt_name=${sensor}_tmad-${y}-${field}.vrt

        if  [ ! -e vrt_name ]; then
            # set this to gather together appropriate netcdfs
            OVR_GLOB=*${y}0101*;

            echo Creating vrt: "${vrt_name}"
            ncdf-list-fields ${field} ${sensor} | xargs -x --max-args 2000 gdalbuildvrt ${vrt_name}

        fi
    done
}

ncdf-yearly-overviews () {
    for y in {1986..2017}; do
        local sensor=$1
        local field=$2
        # wet season summary vrts
        #vrt_name=wofs_${y}-11_$((y + 1))-03_summary.vrt;

        # dry season summary vrts
        #vrt_name=wofs_${y}-04_${y}-10_summary.vrt;

        vrt_name=${sensor}_tmad-${y}-${field}.vrt;
        echo "Creating overviews for ${vrt_name}"

        gdaladdo -r nearest ${vrt_name}  16 64 256 1024 2048
    done
}

# list the netcdf files in the manner needed for gdalbuildvrt NETCDF:filename:band
ncdf-list-fields () {
    local field=$1
    local folder=$2
    for file in $(find ${folder} -iname "${OVR_GLOB}"); do
            echo "NETCDF:${file}:${field}"
    done
}

ncdf-list-fields-thisdir() {
    local field=$1

    for file in $(find ls5 -iname "${OVR_GLOB}" -maxdepth 1); do
            echo "NETCDF:${file}:${field}"
    done
}

# build vrt with list of files returned from overview-list-netcdf-field
ncdf-build-vrt () {
    local field=$1

    echo building vrt for "$field" with glob "${OVR_GLOB}"
    ncdf-list-fields "${field}" | xargs -x --max-args 2000 gdalbuildvrt "${OVR_OUTPUT}/${field}.vrt"
    echo done building vrt for "$field"
}

# create overviews of vrt created
ncdf-create-overviews () {
    local field=$1

    echo resampling "$field"
    gdaladdo "${OVR_OUTPUT}/${field}.vrt" 16 64 256 1024 2048
    echo done resampling "$field"
}

# create vrts for each field listed
ncdf-build-all-vrt () {
    if [[ -z "${OVR_FIELDS}" ]]; then
        echo "no OVR_FIELDS set"
        return
    fi

    if [[ -z "${OVR_GLOB}" ]]; then
        echo "no OVR_GLOB set"
        return
    fi

	if [[ -z "${OVR_OUTPUT}" ]]; then
		echo "no OVR_OUTPUT set"
		return
    fi

    for field in ${OVR_FIELDS}; do
        #ncdf-build-vrt "$field" "${OVR_GLOB}"
        ncdf-yearly-vrt "$field"
    done
}

# create overviews for each field listed
ncdf-create-all-overviews () {
    if [[ -z "${OVR_FIELDS}" ]]; then
        echo "no OVR_FIELDS set"
        return
    fi

    if [[ -z "${OVR_GLOB}" ]]; then
        echo "no OVR_GLOB set"
        return
    fi

	if [[ -z "${OVR_OUTPUT}" ]]; then
		echo "no OVR_OUTPUT set"
		return
    fi

    #for field in ${OVR_FIELDS}; do
    #    ncdf-create-overviews "$field"
    #done
    for sensor in ${SENSORS}; do
         ncdf-yearly-overviews "$sensor"

    done
}

# Create an overview of overviews
ncdf-overview-collate () {
    if [[ -z "${OVR_FIELDS}" ]]; then
        echo "no OVR_FIELDS set"
        return
    fi

	if [[ -z "${OVR_OUTPUT}" ]]; then
		echo "no OVR_OUTPUT set"
		return
    fi

    local OVR_ARRAY=($OVR_FIELDS)
	local OVR_PATH="${OVR_OUTPUT}/"
	OVR_ARRAY=("${OVR_ARRAY[@]/#/${OVR_PATH}}")
	OVR_ARRAY=("${OVR_ARRAY[@]/%/.vrt}")

    echo "${OVR_ARRAY[@]}"
    gdalbuildvrt "${OVR_OUTPUT}/full.vrt" -separate "${OVR_ARRAY[@]}"
}
