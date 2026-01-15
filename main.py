from package.config import conf
from package.earth_engine.datasets import precipitation_monthly , temperature_monthly
from package.bps.datasets import get_population_density
from package.utils import check_data_exist, to_csv
import pandas as pd

curah_hujan = 'curah_hujan.csv'
population_density = 'kepadatan_penduduk.csv'
temperature = 'temperature.csv'

if check_data_exist(curah_hujan):
    print("Data sudah tersedia lanjutkan ke proses selanjutnya")
else:
    try:
        dfs = []
        for year in range(conf.START_YEAR, conf.END_YEAR + 1):
            print("Processing year:", year)
            fc = precipitation_monthly(year)        
            dfs.append(fc)

        result = pd.concat(dfs, ignore_index=True)
        to_csv(result, curah_hujan)
        
        print("Berhasil memprosses data")
    except Exception as e:
        print("Gagal memproses data curah hujan", str(e))


if check_data_exist(temperature):
    print("Data sudah tersedia lanjutkan ke proses selanjutnya")
else:
    try:
        dfs = []
        for year in range(conf.START_YEAR, conf.END_YEAR + 1):
            print("Processing year:", year)
            fc = temperature_monthly(year)        
            dfs.append(fc)

        result = pd.concat(dfs, ignore_index=True)
        to_csv(result, temperature)
        
        print("Berhasil memprosses data")
    except Exception as e:
        print("Gagal memproses data curah hujan", str(e))


dfs = []
for year in range(conf.START_YEAR, conf.END_YEAR + 1):
    print("Processing year:", year)
    population = get_population_density(year)        
    dfs.append(population)

result = pd.concat(dfs, ignore_index=True)
to_csv(result, population_density)