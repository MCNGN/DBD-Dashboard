import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
raw_dir = project_root / "raw_data"
preprocess_dir = project_root / "preprocess_data"

case_dbd = {"raw" : "case_dbd.csv", "preprocess" : "case_dbd_preprocess.csv"}
precipitation = {"raw" : "curah_hujan.csv", "preprocess" : "precipitation_preprocess.csv"}
humidity = {"raw" : "humidity.csv", "preprocess" : "humidity_preprocess.csv"}
temperature = {"raw" : "temperature.csv", "preprocess" : "temperature_preprocess.csv"}
density = {"raw" : "kepadatan_penduduk.csv", "preprocess" : "density_preprocess.csv"}

def preprocess_case_dbd(filename) :
    raw_path = raw_dir / filename
    preprocess_path = preprocess_dir / case_dbd["preprocess"]
    
    df = pd.read_csv(raw_path)
    df = df[["nama_kecamatan", "jumlah","tahun"]].groupby(["nama_kecamatan","tahun"]).agg("sum").reset_index().sort_values(["tahun"])
    df = df.replace("Bl. Limbangan","Balubur Limbangan").sort_values(["tahun","nama_kecamatan"]).rename(columns={"nama_kecamatan": "kecamatan", "tahun" : "year", "jumlah" : "jumlah_kasus"})
    df = df[["kecamatan", "year", "jumlah_kasus"]]
    df.to_csv(preprocess_path, index=False)

def preprocess_precipitation(filename) :
    raw_path = raw_dir / filename
    preprocess_path = preprocess_dir / precipitation["preprocess"]
    
    df = pd.read_csv(raw_path)
    df = df[["WADMKC", "mean","year"]].groupby(["WADMKC","year"]).agg("mean").reset_index().rename(columns={"WADMKC" : "kecamatan", "mean" : "curah_hujan"}).sort_values(["year","kecamatan"])
    df.to_csv(preprocess_path, index=False)

def preprocess_humidity(filename) :
    raw_path = raw_dir / filename
    preprocess_path = preprocess_dir / humidity["preprocess"]
    
    df = pd.read_csv(raw_path)
    df = df[["WADMKC", "mean","year"]].groupby(["WADMKC","year"]).agg("mean").reset_index().rename(columns={"WADMKC" : "kecamatan", "mean" : "kelembapan"}).sort_values(["year","kecamatan"])
    df.to_csv(preprocess_path, index=False)

def preprocess_temperature(filename) :
    raw_path = raw_dir / filename
    preprocess_path = preprocess_dir / temperature["preprocess"]
    
    df = pd.read_csv(raw_path)
    df = df[["WADMKC", "mean","year"]].groupby(["WADMKC","year"]).agg("mean").reset_index().rename(columns={"WADMKC" : "kecamatan", "mean" : "temperature"}).sort_values(["year","kecamatan"])
    df.to_csv(preprocess_path, index=False)

def preprocess_density(filename) :
    raw_path = raw_dir / filename
    preprocess_path = preprocess_dir / density["preprocess"]
    
    df = pd.read_csv(raw_path)
    df = df[["kecamatan", "kepadatan_penduduk","jumlah_penduduk","tahun"]].sort_values(["tahun","kecamatan"])
    df = df.replace("Blubur Limbangan","Balubur Limbangan").sort_values(["tahun","kecamatan"]).rename(columns={"tahun" : "year"})
    df["kepadatan_penduduk"] = df["kepadatan_penduduk"].astype(str).str.replace('.', '').str.replace(' ', '')
    df["jumlah_penduduk"] = df["jumlah_penduduk"].astype(str).str.replace('.', '').str.replace(',', '.').str.replace(' ', '').astype(float) * 1000
    df["jumlah_penduduk"] = df["jumlah_penduduk"].astype(int)
    df.to_csv(preprocess_path, index=False)


def merge_data():
   
    preprocess_case_dbd(case_dbd["raw"])
    preprocess_precipitation(precipitation["raw"])
    preprocess_humidity(humidity["raw"])
    preprocess_temperature(temperature["raw"])
    preprocess_density(density["raw"])

    preprocess_dir = project_root / "preprocess_data"
    case = preprocess_dir / case_dbd["preprocess"]
    perc = preprocess_dir / precipitation["preprocess"]
    humid = preprocess_dir / humidity["preprocess"]
    temp = preprocess_dir / temperature["preprocess"]
    dens = preprocess_dir / density["preprocess"]

    preprocess_file = preprocess_dir / "merge_data.csv"

    df = pd.read_csv(case).merge(pd.read_csv(perc), how="left", on=["kecamatan", "year"]).merge(pd.read_csv(humid), how="left", on=["kecamatan", "year"]).merge(pd.read_csv(temp), how="left", on=["kecamatan", "year"]).merge(pd.read_csv(dens), how="left", on=["kecamatan", "year"])
    df["ir"] = (df["jumlah_kasus"] / df["jumlah_penduduk"]) * 100_000
    df = df[["kecamatan","year","ir","jumlah_kasus","curah_hujan","kelembapan","temperature","kepadatan_penduduk","jumlah_penduduk",]]
    df.to_csv(preprocess_file, index=False)

    return preprocess_file


