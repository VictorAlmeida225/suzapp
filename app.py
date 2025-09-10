import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Mapa de Praças", page_icon="🗺️", layout="wide")
st.title("📍 Mapa de Praças")

JSON_FILE = "pracas.json"
VISITAS_FILE = "visitas.json"

def campo(valor):
    if valor is None or valor == "" or valor == " ":
        return "-----"
    return valor

# Carrega dados
try:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    st.error(f"Arquivo '{JSON_FILE}' não encontrado!")
    st.stop()

# Carrega ou inicializa estados
if os.path.exists(VISITAS_FILE):
    with open(VISITAS_FILE, "r", encoding="utf-8") as f:
        visitas = json.load(f)
else:
    visitas = {}

def gerar_links(coords):
    if coords == ["-----", "-----"]:
        return {"Google Maps": "", "Waze": ""}
    lat, lon = coords
    return {
        "Google Maps": f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}",
        "Waze": f"https://waze.com/ul?ll={lat},{lon}&navigate=yes"
    }

def salvar_visitas():
    with open(VISITAS_FILE, "w", encoding="utf-8") as f:
        json.dump(visitas, f, ensure_ascii=False, indent=4)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Filtros de exibição")
if st.sidebar.button("🗑️ Limpar seleções"):
    for i in range(len(data)):
        key_base = f"praça_{i}"
        visitas[f"{key_base}_visitado"] = False
        visitas[f"{key_base}_timestamp"] = None
        visitas[f"{key_base}_academia"] = False
        visitas[f"{key_base}_quadra"] = False
        visitas[f"{key_base}_parquinho"] = False
        visitas[f"{key_base}_sem_nada"] = False
    salvar_visitas()
    params = st.query_params
    params["reload"] = str(int(params.get("reload", ["0"])[0]) ^ 1)
    st.query_params = params

filtro_visita = st.sidebar.selectbox("Mostrar praças:", ["Todas", "Visitadas", "Não visitadas"])
filtro_academia = st.sidebar.checkbox("Academia", value=False)
filtro_quadra = st.sidebar.checkbox("Quadra/Campo", value=False)
filtro_parquinho = st.sidebar.checkbox("Parquinho de criança", value=False)
filtro_sem_nada = st.sidebar.checkbox("Sem nada!", value=False)

# -----------------------------
# Ordenação por timestamp
# -----------------------------
for i in range(len(data)):
    key_base = f"praça_{i}"
    if f"{key_base}_timestamp" not in visitas:
        visitas[f"{key_base}_timestamp"] = None

def get_timestamp(i):
    ts = visitas.get(f"praça_{i}_timestamp")
    if ts:
        return datetime.fromisoformat(ts)
    else:
        return datetime.max

indices_ordenados = sorted(range(len(data)), key=get_timestamp)

def filtrar_pracas(i):
    key_base = f"praça_{i}"
    visitado_val = visitas.get(f"{key_base}_visitado", False)
    academia_val = visitas.get(f"{key_base}_academia", False)
    quadra_val = visitas.get(f"{key_base}_quadra", False)
    parquinho_val = visitas.get(f"{key_base}_parquinho", False)
    sem_nada_val = visitas.get(f"{key_base}_sem_nada", False)

    if filtro_visita == "Visitadas" and not visitado_val:
        return False
    if filtro_visita == "Não visitadas" and visitado_val:
        return False

    if filtro_academia and not academia_val:
        return False
    if filtro_quadra and not quadra_val:
        return False
    if filtro_parquinho and not parquinho_val:
        return False
    if filtro_sem_nada and not sem_nada_val:
        return False

    return True

indices_exibir = [i for i in indices_ordenados if filtrar_pracas(i)]
total_exibir = len(indices_exibir)
total_pracas = len(data)

st.subheader(f"Total de praças: {total_pracas} | Mostrando: {total_exibir}")

# -----------------------------
# Cards das praças
# -----------------------------
for i in indices_exibir:
    feature = data[i]
    props = feature.get("properties", {})
    coords = feature.get("geometry", {}).get("coordinates", ["-----","-----"])
    coords = [campo(coords[0]), campo(coords[1])] if coords else ["-----","-----"]
    links = gerar_links(coords)

    key_base = f"praça_{i}"
    visitado_val = visitas.get(f"{key_base}_visitado", False)

    with st.container():
        # Enumeração
        if visitado_val:
            numero = sorted(
                [(idx, visitas[f"praça_{idx}_timestamp"]) for idx in range(len(data)) if visitas.get(f"praça_{idx}_visitado")],
                key=lambda x: datetime.fromisoformat(x[1])
            ).index((i, visitas[f"{key_base}_timestamp"])) + 1
            titulo = f"{numero}. {campo(props.get('den_oficia'))}"
        else:
            titulo = campo(props.get('den_oficia'))
        st.markdown(f"### {titulo}")

        st.write(f"**Endereço:** {campo(props.get('endereco'))}")
        st.write(f"**Bairro:** {campo(props.get('bairro'))}")
        st.write(f"**Loteamento:** {campo(props.get('loteamento'))}")
        st.write(f"**Área (m²):** {campo(props.get('m2'))}")
        st.write(f"**Esporte:** {'Sim' if campo(props.get('esporte')).lower() in ['sim','true','1'] else 'Não'}")

        col1, col2 = st.columns([1,2])
        with col1:
            # Já visitado
            visitado = st.checkbox("✅ Já visitado", value=visitado_val, key=f"{key_base}_visitado")

            # Timestamp
            if visitado and not visitado_val:
                visitas[f"{key_base}_timestamp"] = datetime.now().isoformat()
            elif not visitado:
                visitas[f"{key_base}_timestamp"] = None
                visitas[f"{key_base}_academia"] = False
                visitas[f"{key_base}_quadra"] = False
                visitas[f"{key_base}_parquinho"] = False
                visitas[f"{key_base}_sem_nada"] = False

            # Checkbox Sem nada! primeiro para pegar valor atual
            sem_nada = st.checkbox("❌ Sem nada!", value=visitas.get(f"{key_base}_sem_nada", False), key=f"{key_base}_sem_nada", disabled=not visitado)

            # Outras checkboxes desabilitadas se JV não marcado ou sem_nada marcado
            disabled_others = not visitado or sem_nada

            academia = st.checkbox("🏋️ Academia", value=visitas.get(f"{key_base}_academia", False),
                                   key=f"{key_base}_academia", disabled=disabled_others)
            quadra = st.checkbox("🏟️ Quadra/Campo", value=visitas.get(f"{key_base}_quadra", False),
                                 key=f"{key_base}_quadra", disabled=disabled_others)
            parquinho = st.checkbox("🎡 Parquinho de criança", value=visitas.get(f"{key_base}_parquinho", False),
                                    key=f"{key_base}_parquinho", disabled=disabled_others)

            # Se sem_nada marcado, limpa as outras
            if sem_nada:
                academia = False
                quadra = False
                parquinho = False

            # Atualiza estado
            visitas[f"{key_base}_visitado"] = visitado
            visitas[f"{key_base}_academia"] = academia
            visitas[f"{key_base}_quadra"] = quadra
            visitas[f"{key_base}_parquinho"] = parquinho
            visitas[f"{key_base}_sem_nada"] = sem_nada

            salvar_visitas()

        with col2:
            if links["Google Maps"]:
                st.markdown(f"[🗺️ Google Maps]({links['Google Maps']})  ")
                st.markdown(f"[🌎 Waze]({links['Waze']})")
            else:
                st.write("📍 Coordenadas não disponíveis")

        st.markdown("---")

# -----------------------------
# Contador final
# -----------------------------
total_visitadas = sum(visitas.get(f"praça_{i}_visitado", False) for i in range(total_pracas))
st.info(f"✅ Total visitadas: {total_visitadas} | Ainda faltam: {total_pracas - total_visitadas}")
