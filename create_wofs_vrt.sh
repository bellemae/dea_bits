#!/bin/bash

# day & month to use in file name eg. 0209
daymonth=$1

# start of containing directory string eg.S2B_OPER_MSI_ARD_TL_EPAE_20190214T020418_A010138
str=$2


# S2B_OPER_MSI_ARD_TL_EPAE_20190214T020418_A010138_54KWC_N02.07/QA/fmask16.tif

# S2 granule ids required
#cells=("T54KVD" "T54KVE" "T54KVF" "T54KWD" "T54KWE" "T54KWF")
cells=("T54KWG" "T54KXG" "T54KXF" "T54KXE" "T54KXD" "T54KXC" "T54KWC")


for cell in "${cells[@]}"; do
	echo "******************"+${cell}
	# create an int16 version of fmask
	gdal_translate -ot Int16 ${str}_${cell}_N02.07/QA/${str}_${cell}_N02.07_FMASK.TIF ${str}_${cell}_N02.07/QA/fmask16.tif

	#build vrt of all required bands
	gdalbuildvrt ${cell}-${daymonth}.vrt -resolution highest -separate ${str}_${cell}_N02.07/NBART/NBART_B02.TIF ${str}_${cell}_N02.07/NBART/NBART_B03.TIF ${str}_${cell}_N02.07/NBART/NBART_B04.TIF ${str}_${cell}_N02.07/NBART/NBART_B08.TIF ${str}_${cell}_N02.07/NBART/NBART_B11.TIF ${str}_${cell}_N02.07/NBART/NBART_B12.TIF ${str}_${cell}_N02.07/QA/fmask16.tif
done


