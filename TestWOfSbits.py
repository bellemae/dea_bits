# For the given area
#   load the new CU data in native projection
#   classify using WOfS classifier
#   mask using fmask / dsm
#   load current WOfS data - in same projection as CU
#   compare two classifications
#   save out comparison file with bands:
#     'new_water'
#     'curr_water'
#     'missing'
#     'extra'
#     'match'


import datacube
import sys

sys.path.insert(0,'/g/data/u46/users/bt2744/work/code/wofs-prods/wofs/') # to import wofs (and preferentially from here)
import wofs.wofs_app

import numpy as np
import scipy
import xarray
from datacube.storage import masking
from functools import reduce
import xarray as xr
from datacube.drivers.netcdf import write_dataset_to_netcdf

MASKED_HIGH_SLOPE = 1 << 4   # (dec 16)  bit 4: 1=pixel masked out due to high slope
MASKED_TERRAIN_SHADOW = 1 << 3  # (dec 8)   bit 3: 1=pixel masked out due to terrain shadow or
MASKED_NO_CONTIGUITY = 1 << 1   # (dec 2)   bit 1: 1=pixel masked out due to lack of data contiguity
NO_DATA = 1 << 0   # (dec 1)   bit 0: 1=pixel masked out due to NO_DATA in NBAR source, 0=valid data in NBAR
MASKED_CLOUD = 1 << 6   # (dec 64)  bit 6: 1=pixel masked out due to cloud
MASKED_CLOUD_SHADOW = 1 << 5   # (dec 32)  bit 5: 1=pixel masked out due to cloud shadow

# Water detected on slopes equal or greater than this value are masked out
SLOPE_THRESHOLD_DEGREES = 12.0
# If the sun only grazes a hillface, observation unreliable (vegetation shadows etc)
LOW_SOLAR_INCIDENCE_THRESHOLD_DEGREES = 30



#--------------These are from wofs and should be referenced there rather than copied------
def eo_filter(source):
    """
    Find where there is no data
    Input must be dataset, not array (since bands could have different nodata values).
    """
    nodata_bools = source.apply(lambda array: array == array.nodata).to_array(dim='band')

    nothingness = nodata_bools.all(dim='band')
    noncontiguous = nodata_bools.any(dim='band')

    return np.uint8(NO_DATA) * nothingness | np.uint8(MASKED_NO_CONTIGUITY) * noncontiguous


def dilate(array):
    """Dilation e.g. for cloud and cloud/terrain shadow"""
    # kernel = [[1] * 7] * 7 # blocky 3-pixel dilation
    y, x = np.ogrid[-3:4, -3:4]
    kernel = ((x * x) + (y * y) <= 3.5**2)  # disk-like 3-pixel radial dilation
    return scipy.ndimage.binary_dilation(array, structure=kernel)


def terrain_filter(dsm, nbar):
    """
        Terrain shadow masking, slope masking, solar incidence angle masking.
        Input: xarray DataSets
    """

    shadows, slope, sia = wofs.terrain.shadows_and_slope(dsm, nbar.nbart_blue.time.values)

    shadowy = dilate(shadows != wofs.terrain.LIT) | (sia < LOW_SOLAR_INCIDENCE_THRESHOLD_DEGREES)

    steep = (slope > SLOPE_THRESHOLD_DEGREES)

    result = np.uint8(MASKED_TERRAIN_SHADOW) * shadowy | np.uint8(MASKED_HIGH_SLOPE) * steep

    return xarray.DataArray(result, coords=[dsm.y, dsm.x])  # note, assumes (y,x) axis ordering


#-------------------------------------------------------------------------------------------
def pq_filter(fmask):
    masking = np.zeros(fmask.shape, dtype=np.uint8)
    masking[fmask == 0] += NO_DATA
    masking[fmask == 2] += MASKED_CLOUD
    masking[fmask == 3] += MASKED_CLOUD_SHADOW

    return masking


def load_dataset(dc_up, ds, query):
    # Bands/measurements to load
    wofs_measurements = ['nbart_red', 'nbart_blue', 'nbart_green', 'nbart_nir',
                        'nbart_swir_1', 'nbart_swir_2', 'fmask', 'terrain_shadow',
                         'nbart_contiguity']

    ds = dc_up.load(product=ds.type.name,
                    measurements=wofs_measurements,
                    datasets = [ds],
                    **query
                    )

    return ds.squeeze()


def classify(ds):
    bands = ['nbart_blue', 'nbart_green', 'nbart_red', 'nbart_nir', 'nbart_swir_1', 'nbart_swir_2']
    return wofs.classifier.classify(ds[bands].to_array(dim='band'))


def load_dsm(ds, q):
    # Terrain - shadow / high slope
    dc_prod = datacube.Datacube()

    terrain_padding = 6850

    x1 = ds.x.data[0] - terrain_padding
    x2 = ds.x.data[-1] + terrain_padding
    y1 = ds.y.data[0] - terrain_padding
    y2 = ds.y.data[-1] + terrain_padding

    dsm = dc_prod.load(product='dsm1sv10',
                       crs=q['output_crs'],
                       output_crs=q['output_crs'],
                       resolution=q['resolution'],
                       align=q['align'],
                       resampling='average',
                       x=(x1, x2),
                       y=(y1, y2)
                       )

    return dsm.squeeze()


def load_wofl(ds, query):
    datetime = str(ds.time.data)[:19]
    dc_prod = datacube.Datacube()
    print(f"date: {datetime}")
    print(f"Query: {query}")
    wofl = dc_prod.load( product='wofs_albers', time=datetime, **query )
    return wofl.squeeze()


def save(newWOFL, currWOFL, name, both=True):
    newWOFL.attrs['nodata'] = 1

    if both:
        currWOFL['CU_water'] = newWOFL
    else:
        currWOFL = currWOFL[[]]
        currWOFL['water'] = newWOFL

    write_dataset_to_netcdf(currWOFL, f'/g/data/u46/users/bt2744/work/Projects/collection_upgrade/{name}')


if __name__ == '__main__':

    dc_up = datacube.Datacube(env="ard_interop")
    # dc_up = datacube.Datacube(env="josh_test")
    res = 30
    time = ('2017-01-01', '2017-02-20')

    # point
    # lat, lon = -19.25, 146.75    #Townsville
    # lat, lon = -12.25, 132.37    #Kakadu
    lat, lon = -28.53, 153.538
    # area
    buff = 0.1
    lon_dim = (lon - buff, lon + buff)
    lat_dim = (lat - buff, lat + buff)

    # Find all the datasets for my area/time of interest
    datasets = dc_up.find_datasets(product='ls8_ard',
                               time=time,
                               lat=lat_dim,
                               lon=lon_dim,
                               gqa_iterative_mean_xy=[0, 1])

    # for each dataset, load data, classify, filter, compare, save
    # eventually - for ds in datasets:
    #---
    for dataset in datasets:
        print(f"------------------Processing {dataset}")
        query = {
            'resolution': (res, res),
            'align': (res / 2.0, res / 2.0),
            'output_crs': dataset.crs.crs_str,
            'lat': lat_dim,
            'lon': lon_dim,
        }

        # load the data
        data = load_dataset(dc_up, dataset, query)
        dsm = load_dsm(data, query)
        currWOFL = load_wofl(data, query)

        #ensure we have a current WOFL before continuing
        if currWOFL:
            print("Found matching wofl")

            # classify and filter
            newWOFL = classify(data) | eo_filter(data) | pq_filter(data.fmask) | terrain_filter(dsm, data)

            file_name = f"water_bits_{lat}_{lon}_{str(data.time.data)[:19]}.nc"
            save(newWOFL, currWOFL, file_name)
        else:
            print(f"No wofl to match date: {str(data.time.data)}")





