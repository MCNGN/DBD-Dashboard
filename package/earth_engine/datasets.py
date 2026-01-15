import ee
import geemap
from .authentication import init_google_engine
from package.config import conf
from package.utils import months

# Inisisasi Service Google Earth Engine
init_google_engine()

kecamatan = ee.FeatureCollection(conf.SHAPEFILE)
chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY").select("precipitation")
era5 = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY").select(["temperature_2m", "dewpoint_temperature_2m"])


def precipitation_monthly(year):
    acc = ee.FeatureCollection([])

    for m in months:
        start = ee.Date.fromYMD(year, m, 1)
        end = start.advance(1, "month")

        rain_month = chirps.filterDate(start, end).sum().rename("rain_mm")

        stats = rain_month.reduceRegions(
            collection=kecamatan,
            reducer=ee.Reducer.mean(),
            scale=conf.SCALE_CHIRPS
        ).map(lambda f: f.set({"year": year, "month": m, "var": "rain_mm"}))

        acc = acc.merge(stats)

    df = geemap.ee_to_df(acc)    
    
    return df

def temperature_monthly(year) :
    out = ee.FeatureCollection([])

    for m in months:
        start = ee.Date.fromYMD(year, m, 1)
        end = start.advance(1, "month")

        temp_month = era5.filterDate(start, end).select('temperature_2m').mean().subtract(273.15).rename('tmean_c')

        stats = temp_month.reduceRegions(
            collection=kecamatan,
            reducer=ee.Reducer.mean(),
            scale=conf.SCALE_ERA5
        ).map(lambda f: f.set({"year": year, "month": m, "var": "tmean_c"}))
    
        out = out.merge(stats)
    
    df = geemap.ee_to_df(out)    
    
    return df