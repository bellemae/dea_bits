#!/bin/bash

# example
#OVR_FIELDS="frequency count_wet count_clear"
OVR_FIELDS="frequency"
#OVR_GLOB='*2011_summary.nc'
# OVR_OUTPUT='some_folder'
# overview-build-all-vrt
# overview-resample-all
# overview-collate

overview-list-netcdf-field () {
    local field=$1

    for file in $(find annualstats -iname "${OVR_GLOB}"); do
            echo "NETCDF:${file}:${field}"
    done
}

overview-list-netcdf-field-thisdir() {
    local field=$1

    for file in $(find . -iname "${OVR_GLOB}" -maxdepth 1); do
            echo "NETCDF:${file}:${field}"
    done
}

overview-build-vrt () {
    local field=$1

    echo building vrt for "$field" with glob "${OVR_GLOB}"
    overview-list-netcdf-field "${field}" | xargs -x --max-args 2000 gdalbuildvrt "${OVR_OUTPUT}/${field}.vrt"
    echo done building vrt for "$field"
}

overview-resample () {
    local field=$1

    echo resampling "$field"
    gdaladdo -r average "${OVR_OUTPUT}/${field}.vrt" 16 64 256 1024 2048
    echo done resampling "$field"
}

overview-build-all-vrt () {
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
        overview-build-vrt "$field" "${OVR_GLOB}"
    done
}

overview-resample-all () {
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
        overview-resample "$field"
    done
}

overview-collate () {
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
