import ee
from .authentication import init_google_engine
from package.config import conf


# Inisisasi Service Google Earth Engine
init_google_engine()

kecamatan = ee.FeatureCollection(conf.SHAPEFILE)
chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY").select("precipitation")
era5 = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY").select(["temperature_2m", "dewpoint_temperature_2m"])