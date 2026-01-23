from package.config import conf
from package.earth_engine.datasets import precipitation_monthly , temperature_monthly, humidity_monthly
from package.bps.datasets import get_population_density, get_case_dbd
from package.utils import check_data_exist, to_csv
from package.preprocess.preprocess import merge_data
from package.process.process import process_z_score
import pandas as pd

data = [{
        "func": precipitation_monthly, 
        "file": 'curah_hujan.csv',
        "label": 'curah hujan'
        },
        {
        "func": get_population_density, 
        "file": 'kepadatan_penduduk.csv',
        "label": 'populasi'
        },
        {
        "func": temperature_monthly, 
        "file": 'temperature.csv',
        "label": 'temperature'
        },
        {
        "func": humidity_monthly, 
        "file": 'humidity.csv',
        "label": 'kelembapan'
        },
        {
        "func": get_case_dbd, 
        "file": 'case_dbd.csv',
        "label": 'kasus dbd'
        }
]

for item in data:
    if check_data_exist(item["file"]):
        print(f"Data {item["label"]} sudah tersedia lanjutkan ke proses selanjutnya \n")
    else:
        try:
            print(f"Memprosses data {item["label"]} : ")
            dfs = []
            for year in range(conf.START_YEAR, conf.END_YEAR + 1):
                print("Processing year:", year)
                fc = item["func"](year)        
                dfs.append(fc)

            result = pd.concat(dfs, ignore_index=True)
            to_csv(result, item["file"])
            
            print(f"Berhasil memprosses data {item["label"]} \n")
        except Exception as e:
            print(f"Gagal memproses data {item["label"]} \n", str(e))

preprocess_data = merge_data()

process_z_score(preprocess_data)
