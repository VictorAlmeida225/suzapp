import json
import streamlit as st
from pathlib import Path
from datetime import datetime

DADOS_JSON = Path("dados.json")
ESTADO_JSON = Path("estado_usuario.json")

# -----------------------------
# Funções utilitárias
# -----------------------------
def campo_valido(valor):
    if valor is None:
        return "-----"
    valor_str = str(valor).strip()
    if valor_str == "":
        return "-----"
    return valor_str

def salvar_estado(estado):
    with open(ESTADO_JSON, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)

def carregar_estado():
    if ESTADO_JSON.exists():
        with open(ESTADO_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# -----------------------------
# Carregar dados do JSON
# -----------------------------
if not DADOS_JSON.exists():
    st.error("Arquivo dados.json não encontrado.")
    st.stop()

with open(DADOS_JSON, "r", encoding="utf-8") as f:
    dados_raw = json.load(f)

# -----------------------------
# Normalizar dados
# -----------------------------
def normalizar_dados(dados_raw):
    dados_norm = []
    for f in dados_raw:
        prop = f.get("properties", {})
        geo = f.get("geometry", {})

        den_oficia = campo_valido(prop.get("den_oficia", ""))
        apelido = campo_valido(prop.get("apelido", ""))
        nome = den_oficia if den_oficia != "-----" else apelido if apelido != "-----" else "-----"

        endereco = campo_valido(prop.get("endereco", ""))
        bairro = campo_valido(prop.get("bairro", ""))
        loteamento = campo_valido(prop.get("loteamento", ""))
        area = campo_valido(prop.get("m2", ""))

        coords = geo.get("coordinates", [])
        if len(coords) == 2:
            x, y = coords
            lat, lon = x, y
        else:
            lat = lon = None

        dados_norm.append({
            "nome": nome,
            "endereco": endereco,
            "bairro": bairro,
            "loteamento": loteamento,
            "area": area,
            "lat": lat,
            "lon": lon
        })
    return dados_norm

dados = normalizar_dados(dados_raw)

# -----------------------------
# Inicializar estado do usuário
# -----------------------------
estado_usuario_list = carregar_estado()
estado_usuario = {x["nome"]: x for x in estado_usuario_list}

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("⚙️ Filtros e Ações")
filtro_nome = st.sidebar.text_input("🔎 Buscar pelo nome")

if st.sidebar.button("🧹 Limpar tudo"):
    # Limpa o JSON do usuário
    estado_usuario = {}
    salvar_estado([])
    
    # Limpa todas as chaves de session_state relacionadas às checkboxes
    for key in list(st.session_state.keys()):
        if key.startswith(("jv_", "quadra_", "parquinho_", "academia_", "semnada_")):
            del st.session_state[key]
    
    # Recarrega a página para refletir
    st.experimental_rerun = True

# -----------------------------
# Ordenar dados por timestamp JV
# -----------------------------
def ordenar_dados(dados, estado_usuario):
    visitados = [p for p in dados if p["nome"] in estado_usuario and estado_usuario[p["nome"]].get("timestamp")]
    visitados.sort(key=lambda x: estado_usuario[x["nome"]]["timestamp"])
    nao_visitados = [p for p in dados if p["nome"] not in estado_usuario or not estado_usuario[p["nome"]].get("timestamp")]
    return visitados + nao_visitados

dados_ordenados = ordenar_dados(dados, estado_usuario)

# -----------------------------
# Loop principal
# -----------------------------
for p in dados_ordenados:
    nome = p["nome"]
    lat, lon = p["lat"], p["lon"]

    estado = estado_usuario.get(nome, {})
    visitado = estado.get("jv", False)
    quadra = estado.get("quadra", False)
    parquinho = estado.get("parquinho", False)
    academia = estado.get("academia", False)
    semnada = estado.get("semnada", False)
    timestamp = estado.get("timestamp", None)

    # Número de visita
    visitados = [x for x in estado_usuario.values() if x.get("timestamp")]
    visitados.sort(key=lambda x: x["timestamp"])
    ordem = next((i+1 for i,x in enumerate(visitados) if x["nome"]==nome), None)
    label_nome = f"{ordem}. {nome}" if ordem else nome

    with st.container():
        st.subheader(label_nome)
        st.write(f"📍 Endereço: {p['endereco']}")
        st.write(f"🏘️ Bairro: {p['bairro']} | 🗺️ Loteamento: {p['loteamento']}")
        st.write(f"📏 Área: {p['area']} m²")

        # JV
        jv_checked = st.checkbox("✅ Já visitado", value=visitado, key=f"jv_{nome}")
        if jv_checked != visitado:
            if jv_checked:
                estado_usuario[nome] = {"nome": nome, "jv": True, "timestamp": datetime.now().timestamp(),
                                        "quadra": False, "parquinho": False, "academia": False, "semnada": False}
            else:
                estado_usuario[nome]["jv"] = False
                estado_usuario[nome]["timestamp"] = None
                estado_usuario[nome]["quadra"] = False
                estado_usuario[nome]["parquinho"] = False
                estado_usuario[nome]["academia"] = False
                estado_usuario[nome]["semnada"] = False
            salvar_estado(list(estado_usuario.values()))
            st.experimental_rerun = True  # marca para atualizar

        # Sem nada
        semnada_checked = st.checkbox("🚫 Sem nada", value=semnada, key=f"semnada_{nome}", disabled=not jv_checked)
        if semnada_checked != semnada:
            estado_usuario[nome]["semnada"] = semnada_checked
            if semnada_checked:
                estado_usuario[nome]["quadra"] = False
                estado_usuario[nome]["parquinho"] = False
                estado_usuario[nome]["academia"] = False
            salvar_estado(list(estado_usuario.values()))
            st.experimental_rerun = True

        disabled_others = semnada or not jv_checked
        quadra_checked = st.checkbox("🏀 Quadra/Campo", value=quadra, key=f"quadra_{nome}", disabled=disabled_others)
        parquinho_checked = st.checkbox("🎡 Parquinho", value=parquinho, key=f"parquinho_{nome}", disabled=disabled_others)
        academia_checked = st.checkbox("🏋️ Academia", value=academia, key=f"academia_{nome}", disabled=disabled_others)

        if quadra_checked != quadra:
            estado_usuario[nome]["quadra"] = quadra_checked
            salvar_estado(list(estado_usuario.values()))
        if parquinho_checked != parquinho:
            estado_usuario[nome]["parquinho"] = parquinho_checked
            salvar_estado(list(estado_usuario.values()))
        if academia_checked != academia:
            estado_usuario[nome]["academia"] = academia_checked
            salvar_estado(list(estado_usuario.values()))

        if lat and lon:
            maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            waze_url = f"https://waze.com/ul?ll={lat},{lon}&navigate=yes"
            st.markdown(f"[🗺️ Google Maps]({maps_url}) | 🌎 [Waze]({waze_url})")
        else:
            st.write("Coordenadas não disponíveis.")
