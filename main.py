from package.config import conf
from package.earth_engine.chirps import chirps_monthly
# from package.earth_engine.export import to_data_frame
from package.bps.datasets import show
from package.utils import check_data_exist, to_csv
import pandas as pd

curah_hujan = 'curah_hujan.csv'

if check_data_exist(curah_hujan):
    print("Data sudah tersedia lanjutkan ke proses selanjutnya")
else:
    try:
        dfs = []
        for year in range(conf.START_YEAR, conf.END_YEAR + 1):
            print("Processing year:", year)
            fc = chirps_monthly(year)        
            dfs.append(fc)

        result = pd.concat(dfs, ignore_index=True)
        to_csv(result, curah_hujan)
        
        print("Berhasil memprosses data")
    except Exception as e:
        print("Gagal memproses data curah hujan", str(e))


df = show()
to_csv(df,'data_penduduk_2025.csv')