import ee
from package.config import conf

def init_google_engine():

    ee.Authenticate()

    try:
        ee.Initialize(project=conf.PROJECT_NAME)
    except Exception:
        print("WARNING: Earth Engine belum ter-authenticate. Jalankan `earthengine authenticate` dulu.")
