"""Build data/boston_zip_centroids.csv: center points of ZIP code areas (ZCTAs) in the City of Boston.

Run from rxcompass/:  ..\\.venv\\Scripts\\python.exe scripts\\build_zip_centroids.py

Sources (U.S. Census Bureau, public):
- Which ZCTAs overlap Boston city (place GEOID 2507000): 2020 ZCTA-to-place relationship file.
- Center point (internal point latitude/longitude) of each ZCTA: 2024 Gazetteer ZCTA file.
Downloads go to data/raw/ (git-ignored).
"""

import csv
import io
import zipfile
from datetime import date
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "boston_zip_centroids.csv"
REL_URL = "https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_place20_natl.txt"
GAZ_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_zcta_national.zip"
BOSTON_PLACE = "2507000"
MIN_SHARE = 0.10  # keep a ZCTA if at least 10% of its land is inside Boston
# Nearby towns where patients who use Boston pharmacies often live or work (share of land in Boston = 0). Added
# 2026-10-24 after a patient searched from Randolph (02368).
NEARBY = {"02368": "Randolph", "02186": "Milton", "02169": "Quincy", "02170": "Quincy", "02171": "Quincy",
          "02184": "Braintree", "02021": "Canton", "02026": "Dedham", "02445": "Brookline", "02446": "Brookline",
          "02138": "Cambridge", "02139": "Cambridge", "02140": "Cambridge", "02141": "Cambridge", "02142": "Cambridge",
          "02143": "Somerville", "02144": "Somerville", "02145": "Somerville", "02148": "Malden", "02149": "Everett",
          "02150": "Chelsea", "02151": "Revere", "02152": "Winthrop", "02155": "Medford", "02458": "Newton",
          "02459": "Newton", "02460": "Newton", "02472": "Watertown", "02492": "Needham"}


def fetch(url: str) -> bytes:
    path = RAW / Path(url).name
    if not path.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        path.write_bytes(httpx.get(url, timeout=300, follow_redirects=True).content)
    return path.read_bytes()


def main() -> None:
    rel = csv.DictReader(io.StringIO(fetch(REL_URL).decode("utf-8-sig")), delimiter="|")
    share = {}
    for r in rel:
        if r["GEOID_PLACE_20"] == BOSTON_PLACE and r["GEOID_ZCTA5_20"]:
            land = float(r["AREALAND_PART"] or 0)
            total = float(r["AREALAND_ZCTA5_20"] or 0)
            share[r["GEOID_ZCTA5_20"]] = land / total if total else 0.0
    keep = {z: s for z, s in share.items() if s >= MIN_SHARE}
    for z in NEARBY:
        keep.setdefault(z, 0.0)

    gz = zipfile.ZipFile(io.BytesIO(fetch(GAZ_URL)))
    txt = gz.read(gz.namelist()[0]).decode("utf-8")
    rows = list(csv.reader(io.StringIO(txt), delimiter="\t"))
    head = [h.strip() for h in rows[0]]
    i_z, i_lat, i_lon = head.index("GEOID"), head.index("INTPTLAT"), head.index("INTPTLONG")
    out = []
    for r in rows[1:]:
        z = r[i_z].strip()
        if z in keep:
            out.append({"zip": z, "latitude": float(r[i_lat]), "longitude": float(r[i_lon].strip()),
                        "share_of_land_in_boston": round(keep[z], 3),
                        "source": f"{GAZ_URL} ; {REL_URL}", "checked_date": date.today().isoformat()})
    out.sort(key=lambda x: x["zip"])
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} Boston and nearby ZIP centers -> {OUT}")
    print(" ".join(x["zip"] for x in out))


if __name__ == "__main__":
    main()
