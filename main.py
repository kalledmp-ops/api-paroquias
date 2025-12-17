from fastapi import FastAPI, Query, HTTPException
import pandas as pd
import math
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="API de Paróquias – Arquidiocese de São Paulo",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP: permite qualquer origem
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Carrega CSV uma vez
df = pd.read_csv(
    "data/paroquias_regiao_belem_geo.csv",
    encoding="utf-8"
)
df["id"] = df.index

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

@app.get("/paroquias")
def listar_paroquias():
    return df.fillna("").to_dict(orient="records")

@app.get("/paroquias/proximas")
def paroquias_proximas(
    lat: float = Query(...),
    lng: float = Query(...),
    raio_km: float = Query(5.0)
):
    resultados = []

    for _, row in df.iterrows():
        try:
            lat_p = float(row["latitude"])
            lng_p = float(row["longitude"])
        except (ValueError, TypeError, KeyError):
            continue

        dist = haversine(lat, lng, lat_p, lng_p)

        if dist <= raio_km:
            item = row.fillna("").to_dict()
            item["distancia_km"] = round(dist, 2)
            resultados.append(item)

    resultados.sort(key=lambda x: x["distancia_km"])
    return resultados


@app.get("/paroquias/{paroquia_id}")
def detalhe_paroquia(paroquia_id: int):
    if paroquia_id not in df["id"].values:
        raise HTTPException(status_code=404, detail="Paróquia não encontrada")

    return df[df["id"] == paroquia_id].iloc[0].to_dict()

