import pandas as pd
from pathlib import Path
from sklearn.cluster import KMeans

project_root = Path(__file__).resolve().parents[2]
processed_dir = project_root / "processed_data"

def process_z_score(filename):

    df = pd.read_csv(filename)
    columns = ["ir","curah_hujan","kelembapan","temperature","kepadatan_penduduk"]

    for column in columns:
        df[f'{column}_z_score'] = df.groupby('year')[column].transform( lambda x : (x - x.mean()) / x.std())

    processed_file = processed_dir / "merge_data_zscore.csv"

    df.to_csv(processed_file, index=False)

    return processed_file

def process_clustering(filename):

    df = pd.read_csv(filename)
    
    feature_columns = ["ir_z_score", "curah_hujan_z_score", "kelembapan_z_score", 
                       "temperature_z_score", "kepadatan_penduduk_z_score"]
    
    df['cluster'] = -1 
    df['risk_category'] = ''

    for year in df['year'].unique():
        year_mask = df['year'] == year
        X = df.loc[year_mask, feature_columns]
        
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        original_clusters = kmeans.fit_predict(X)
        
        # Buat DataFrame sementara untuk mapping
        temp_df = pd.DataFrame({
            'original_cluster': original_clusters,
            'ir': df.loc[year_mask, 'ir'].values
        })
        
        # Hitung rata-rata IR per cluster dan urutkan
        cluster_ir_mean = temp_df.groupby('original_cluster')['ir'].mean().sort_values()
        
        # Mapping: cluster dengan IR terendah = 0 (Rendah), tertinggi = 2 (Tinggi)
        cluster_mapping = {old: new for new, old in enumerate(cluster_ir_mean.index)}
        risk_labels = {0: 'Rendah', 1: 'Sedang', 2: 'Tinggi'}
        
        # Terapkan mapping ke cluster baru
        new_clusters = [cluster_mapping[c] for c in original_clusters]
        df.loc[year_mask, 'cluster'] = new_clusters
        df.loc[year_mask, 'risk_category'] = [risk_labels[c] for c in new_clusters]
    
    processed_file = processed_dir / "merge_data_clustered.csv"
    df.to_csv(processed_file, index=False)
    
    return processed_file