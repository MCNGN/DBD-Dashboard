import ee
import geemap
from .datasets import chirps, kecamatan
from package.utils import months
from package.config import conf


def chirps_monthly(year):
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