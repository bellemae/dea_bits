## download files from s3
        ### WOfS bands
        # aws s3 cp  s3://dea-public-data/L2/sentinel-2-nrt/S2MSIARD/2019-02-14/ /g/data/u46/users/bt2744/work/data/floodFeb19/s2_imagery/2019-02-14/ --exclude "*" --include "*54KVF*/NBART/*" --include "*54KVE*/NBART/*" --include "*54KVD*/NBART/*" --include "*54KWF*/NBART/*" --include "*54KWE*/NBART/*" --include "*54KWD*/NBART/*" --recursive
         ### QA bands
        # aws s3 cp  s3://dea-public-data/L2/sentinel-2-nrt/S2MSIARD/2019-02-09/ /g/data/u46/users/bt2744/work/data/floodFeb19/s2_imagery/2019-02-09/ --exclude "*" --include "*54KVF*/QA/*NBART_CONT*" --include "*54KVF*/QA/*FMASK.TIF" --include "*54KVE*/QA/*NBART_CONT*" --include "*54KVE*/QA/*FMASK.TIF" --include "*54KVD*/QA/*NBART_CONT*" --include "*54KVD*/QA/*FMASK.TIF" --include "*54KWF*/QA/*NBART_CONT*" --include "*54KWF*/QA/*FMASK.TIF" --include "*54KWE*/QA/*NBART_CONT*" --include "*54KWE*/QA/*FMASK.TIF" --include "*54KWD*/QA/*NBART_CONT*" --include "*54KWD*/QA/*FMASK.TIF" --recursive
## create vrt of all bands
        #  /g/data/u46/users/bt2744/work/data/floodFeb19/s2_imagery/create_vrt.sh
## then run this




import datacube
import sys
import click

sys.path.append('../dea-notebooks/10_Scripts')
import DEAPlotting, SpatialTools, DEADataHandling

sys.path.insert(0,'/g/data/u46/users/bt2744/work/code/wofs/') # to import wofs (and preferentially from here)
import wofs.wofs_app
from datacube import helpers
from datacube.utils import geometry
import rasterio as rio
import xarray as xr
import matplotlib.pyplot as plt


# Load data from file
def _load_file_data(filename):
    with xr.open_rasterio(filename) as f:
        return f

def _classify(data):
    print("Classify the dataset")
    water = wofs.classifier.classify(data).to_dataset(dim="water")
    print(water)
    water.attrs['crs'] = geometry.CRS(data.attrs['crs'])

    return water

def _save(ds, name):
    helpers.write_geotiff(name, ds)

def _mask(water, fmask):
    # fmask: null(0), cloud(2), cloud shadow(3)
    return water.where(~(fmask.isin([0, 2, 3])))

if __name__=='__main__':
    year="2019"
    monthdays = ['0214', '0219',]
    for md in monthdays:
        loc="/g/data/u46/users/bt2744/work/data/floodFeb19/s2_imagery/2019-"+md[0:2]+"-"+md[2:4]+"/"

        cells = ["T54KVD", "T54KVE","T54KVF","T54KWD","T54KWE","T54KWF"]

        for cell in cells:
            infile = cell+"-"+md+".vrt"
            outfile = "water_"+infile.split('.')[0]+".tif"

            print("Processing "+infile+"....")
            ds = _load_file_data(loc+infile)
            water = _classify(ds[0:6])
            _save(water, loc+outfile)
            _save(_mask(water, ds[-1]), loc+"m_"+outfile)


    print("Done.")