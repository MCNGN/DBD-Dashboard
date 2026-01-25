import pandas as pd
from pathlib import Path
from sklearn.cluster import KMeans

project_root = Path(__file__).resolve().parents[2]
processed_dir = project_root / "processed_data"

def process_z_score(filename):

    df = pd.read_csv(filename)
    columns = ["ir","curah_hujan","kelembapan","temperature","kepadatan_penduduk","jumlah_penduduk"]

    for column in columns:
        df[f'{column}_z_score'] = df.groupby('year')[column].transform( lambda x : (x - x.mean()) / x.std())

    processed_file = processed_dir / "merge_data_zscore.csv"

    df.to_csv(processed_file, index=False)

    return processed_file

def process_clustering():
    print("Hello World !")