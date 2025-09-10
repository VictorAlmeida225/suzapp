import json

input_file = "pracas_implantadas.geojson"
output_file = "pracas.json"

# Ordem desejada dos campos (excluindo 'saude')
ordem_properties = [
    "den_oficia", "endereco", "lei_dec_of", "link",
    "apelido", "bairro", "loteamento", "esporte", "m2"
]

def tratar_feature(feature):
    props = feature.get("properties", {})
    # Mantém apenas os campos desejados e na ordem definida
    properties = {k: props.get(k, "-----") for k in ordem_properties}

    # Mantém geometry com coordinates invertidos
    geometry = feature.get("geometry", {})
    coords = geometry.get("coordinates", None)
    if coords and isinstance(coords, list) and len(coords) >= 2:
        geometry_tratada = {"coordinates": [coords[1], coords[0]]}
    else:
        geometry_tratada = {"coordinates": ["-----", "-----"]}

    # Combina properties e geometry
    feature_tratada = {
        "properties": properties,
        "geometry": geometry_tratada
    }

    return feature_tratada

# Leitura do arquivo geojson
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Processa todas as features
features_tratadas = [tratar_feature(f) for f in data.get("features", [])]

# Função para mesclar duplicados
def mesclar_duplicados(features):
    vistos = []
    unicos = []
    for f in features_tratadas:
        chave = json.dumps(f, sort_keys=True)  # converte feature em string para comparação
        if chave not in vistos:
            vistos.append(chave)
            unicos.append(f)
    return unicos

features_unicas = mesclar_duplicados(features_tratadas)

# Salva o resultado final
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(features_unicas, f, ensure_ascii=False, indent=4)

print(f"Arquivo tratado salvo em: {output_file}")
