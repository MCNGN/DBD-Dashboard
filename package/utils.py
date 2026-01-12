import os
import pandas as pd
from pathlib import Path

months = list(range(1,13))

def rh_from_temp_dewpoints(tC, tdC):
    num = tdC.expression("exp(17.625*TD/(243.04+TD))", {"TD": tdC})
    den = tC.expression("exp(17.625*T/(243.04+T))", {"T": tC})
    return num.divide(den).multiply(100).rename("rh_percent")

def check_data_exist(file_name):
    p = Path(f'./raw_data/{file_name}')
    print(p)
    return p.is_file()

def to_csv(df, filename):
    csv = pd.DataFrame(df)

    project_root = Path(__file__).resolve().parents[1]
    raw_dir = project_root / "raw_data"
    raw_dir.mkdir(parents=True, exist_ok=True)

    out_path = raw_dir / filename

    csv.to_csv(out_path, index=False)