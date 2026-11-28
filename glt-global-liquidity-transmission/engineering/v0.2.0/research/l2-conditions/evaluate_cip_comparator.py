"""Historical cross-currency comparator only; run with pandas and pyarrow."""
import json
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd
import pyarrow.parquet as pq

root = Path(sys.argv[1])
columns = []
for currency in ("EUR", "JPY"):
    d = pq.ParquetFile(root / f"{currency}.parquet").read().to_pandas()
    q = d.loc[d.tenor.eq("1y") & d.rho_sofr.notna()].set_index("date")
    assert q.index.is_unique
    residual = ((q.diff_y - q.rho_sofr) * 100 - q.cip_govt_sofr).abs().dropna()
    assert len(residual) and residual.max() < 0.001
    columns.append(q.rho_sofr.mul(100).rename(currency))
    three = d.loc[d.tenor.eq("3m")].dropna(subset=["rho_sofr", "rho_ibor"])
    diff = (three.rho_sofr - three.rho_ibor).abs() * 100
    print(currency, "1y", len(q), q.index.min().date(), q.index.max().date(),
          "3m overlap/differences/max abs bp", len(three), int((diff > 1e-6).sum()), round(diff.max(), 5))
cross = pd.concat(columns, axis=1).dropna().sort_index()
print("Cross only overlap and Pearson:", len(cross), cross.index.min().date(),
      cross.index.max().date(), round(cross.corr().iloc[0, 1], 4))
with zipfile.ZipFile(root / "prates.zip") as archive:
    xml = ET.fromstring(archive.read("PRATES_data.xml"))
target = [n for n in xml.iter() if n.get("SERIES_NAME") == "RESBM_N.D"]
assert len(target) == 1
iorb = pd.Series({pd.Timestamp(e.get("TIME_PERIOD")): float(e.get("OBS_VALUE"))
                  for e in target[0] if e.get("TIME_PERIOD") and e.get("OBS_VALUE")}, name="IORB")
sofr = pd.Series({pd.Timestamp(r["effectiveDate"]): r["percentRate"]
                  for r in json.loads((root / "sofr.json").read_text())["refRates"]}, name="SOFR")
z = cross.join([iorb, sofr], how="inner").dropna()
z["domestic_bps"] = (z.SOFR - z.IORB).mul(100).round(6)
z = z[["EUR", "JPY", "domestic_bps"]]
print("Triple overlap:", len(z), z.index.min().date(), z.index.max().date())
for label, frame, method in (("levels", z, "pearson"), ("ranks", z, "spearman"),
                             ("matched-session changes", z.diff(), "pearson")):
    print(label, "\n", frame.corr(method=method).round(4).to_string())
print(z.reindex(pd.to_datetime(["2023-03-13", "2023-03-20", "2024-08-05", "2025-04-09", "2025-06-30"])).round(2).to_string())
