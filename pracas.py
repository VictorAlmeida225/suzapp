import json
from pathlib import Path

# Nome do arquivo de entrada/saída
entrada = Path("pracas_implantadas.geojson")
saida = Path("pracas.json")

# Campos que queremos manter
CAMPOS_PERMITIDOS = [
    "den_oficia",
    "endereco",
    "lei_dec_of",
    "link",
    "apelido",
    "bairro",
    "loteamento",
    "m2"
]

def safe(value):
    """Converte valores vazios em -----"""
    if value in (None, "", [], {}):
        return "-----"
    return value

def processar_geojson():
    with open(entrada, "r", encoding="utf-8") as f:
        data = json.load(f)

    novas_features = []
    vistos = set()  # para evitar duplicados

    for feat in data.get("features", []):
        props = feat.get("properties", {})
        geom = feat.get("geometry", {})

        # Seleciona apenas os campos permitidos
        new_props = {}
        for campo in CAMPOS_PERMITIDOS:
            new_props[campo] = safe(props.get(campo))

        # Geometry apenas coordinates invertidos
        coords = geom.get("coordinates", None)
        if coords and len(coords) == 2:
            yx = [coords[1], coords[0]]  # inverte x,y -> y,x
        else:
            yx = ["-----", "-----"]

        new_geom = {
            "type": "Point",
            "coordinates": yx
        }

        # Para evitar duplicados, criamos uma chave única das properties
        chave = tuple(new_props.items()) + tuple(yx)
        if chave in vistos:
            continue
        vistos.add(chave)

        novas_features.append({
            "properties": new_props,
            "geometry": new_geom
        })

    with open(saida, "w", encoding="utf-8") as f:
        json.dump(novas_features, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(novas_features)} registros processados e salvos em {saida}")

if __name__ == "__main__":
    processar_geojson()
