import pandas as pd
from package.config import conf

def get_population_density(year):
    url = f"https://webapi.bps.go.id/v1/api/interoperabilitas/datasource/simdasi/id/25/tahun/{year}/id_tabel/WVRlTTcySlZDa3lUcFp6czNwbHl4QT09/wilayah/3205000/key/{conf.API_KEY}"   
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    raw = pd.read_json(url, storage_options=headers)
    raw = raw.to_dict()

    rows = []
    for item in raw["data"][1]["data"]:
        rows.append({
            "kecamatan": item["label"],
            "kode_wilayah": item["kode_wilayah"],
            "jumlah_penduduk": item["variables"]["nzudy5elv7"]["value"],
            "laju_pertumbuhan": item["variables"]["d8efayjxld"]["value"],
            "persentase_penduduk": item["variables"]["efg2cjrdn2"]["value"],
            "kepadatan_penduduk": item["variables"]["xauol4vjpj"]["value"],
            "rasio_jenis_kelamin": item["variables"]["ztxhjlhyqd"]["value"],
        })

    df = pd.DataFrame(rows)
    df.insert(7,"tahun",year)
    return df

def get_case_dbd(year):
    url = f"https://satudata-api.garutkab.go.id/api/dataset-value/jumlah-kasus-penyakit-demam-berdarah-dengue-dbd-menurut-puskesmas-di-kabupaten-garut-4113"   
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    raw = pd.read_json(url, storage_options=headers)
    raw = raw.to_dict()
    raw_df = pd.DataFrame(raw["data"]).transpose()
    df = raw_df[raw_df["tahun"] == year]

    return df

if __name__ == "__main__":
    print(get_case_dbd(2022))