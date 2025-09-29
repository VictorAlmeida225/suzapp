import json
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Players Explorer - Mock")

# --- CARREGA JSON LOCAL ---
with open("mock_players.json", "r", encoding="utf-8") as f:
    data = json.load(f)

leagues = data["leagues"]
teams = data["teams"]
players = data["players"]

# --- ESTADO DAS LIGAS ---
if "ligas_ativas" not in st.session_state:
    st.session_state["ligas_ativas"] = [l["league_id"] for l in leagues]

# --- UI LOGOS LIGAS ---
st.markdown("### Selecione as Ligas")
cols = st.columns(len(leagues))
for idx, l in enumerate(leagues):
    active = l["league_id"] in st.session_state["ligas_ativas"]
    with cols[idx]:
        st.image(l.get("logo") or "", width=70)
        if active:
            st.write(f"**{l['league_name']}**")
            if st.button(f"Desativar {l['league_name']}", key=f"off_{l['league_id']}"):
                st.session_state["ligas_ativas"].remove(l["league_id"])
        else:
            st.write(f"<span style='opacity:0.5'>{l['league_name']}</span>", unsafe_allow_html=True)
            if st.button(f"Ativar {l['league_name']}", key=f"on_{l['league_id']}"):
                st.session_state["ligas_ativas"].append(l["league_id"])

# --- FILTRA TIMES POR LIGAS ATIVAS ---
ligas_ativas = st.session_state["ligas_ativas"]
teams_ativas = [t for t in teams if t["league_id"] in ligas_ativas]
team_ids = [t["team_id"] for t in teams_ativas]

# --- FILTRA JOGADORES POR TIMES ATIVOS ---
df = pd.DataFrame([p for p in players if p["team_id"] in team_ids])

# --- FILTROS LATERAL ---
st.sidebar.header("Filtros")
if not df.empty:
    # Idade
    idade_min, idade_max = int(df["age"].min()), int(df["age"].max())
    idade_range = st.sidebar.slider("Idade", idade_min, idade_max, (idade_min, idade_max))

    # Número da camisa
    num_min, num_max = int(df["number"].min()), int(df["number"].max())
    num_range = st.sidebar.slider("Número da Camisa", num_min, num_max, (num_min, num_max))

    # Nacionalidade
    nacionalidades = sorted(df["nationality"].dropna().unique())
    nats_sel = st.sidebar.multiselect("Nacionalidade", options=nacionalidades, default=nacionalidades)

    # Posição
    posicoes = sorted(df["position"].dropna().unique())
    pos_sel = st.sidebar.multiselect("Posição", options=posicoes, default=posicoes)

    # Aplica filtros
    df = df[
        (df["age"].between(*idade_range)) &
        (df["number"].between(*num_range)) &
        (df["nationality"].isin(nats_sel)) &
        (df["position"].isin(pos_sel))
    ]

# --- EXIBE TABELA ---
if not df.empty:
    # Substituir team_id pelo nome do time
    df["team_name"] = df["team_id"].map({t["team_id"]: t["team_name"] for t in teams})
    st.dataframe(df[["name","age","number","position","nationality","team_name"]], use_container_width=True)
else:
    st.warning("Nenhum jogador encontrado para os filtros atuais.")
