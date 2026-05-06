import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Ghazali Stock Online", layout="wide")

# --- CONNEXION À GOOGLE SHEETS ---
# Note : L'URL de votre Google Sheet devra être configurée dans les "Secrets" une fois en ligne
url = "https://docs.google.com/spreadsheets/d/1vMgzCYFD2s7UVQ-TQ7ZK2A162QObv6c936Sx5X5uDt0/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

# Lecture des données
df = conn.read(spreadsheet=url, usecols=[0, 1, 2, 3, 4, 5])
df = df.dropna(how="all") # Nettoyer les lignes vides

st.title("🧪 Inventaire Ghazali Parfums (Mode Cloud)")

# --- RECHERCHE ET INTERFACE ---
# (Gardez la même logique de recherche que nous avons créée précédemment)
st.markdown("### 🔍 Recherche rapide")
col_choix, col_texte = st.columns([1, 3])
with col_choix:
    colonne_recherche = st.selectbox("Filtrer par :", ["ID", "Genre", "Marque", "Nom", "Code", "Quantité"])
with col_texte:
    search_query = st.text_input(f"Tapez votre recherche pour '{colonne_recherche}' ici :", "").strip()

if search_query:
    mask = df[colonne_recherche].astype(str).str.contains(search_query, case=False, na=False)
    df_display = df[mask]
else:
    df_display = df

col_table, col_panel = st.columns([7, 3])

with col_table:
    st.write(f"📊 Articles visibles : **{len(df_display)}**")
    st.dataframe(df_display, use_container_width=True, hide_index=True, height=500)

# --- MODIFICATIONS ---
with col_panel:
    with st.expander("⚙️ Modifications", expanded=True):
        action = st.radio("Action :", ["➕ Ajouter", "📝 Modifier"], horizontal=True)
        
        if action == "➕ Ajouter":
            with st.form("ajout"):
                # Champs du formulaire... (ID, Nom, etc.)
                new_data = [st.text_input("ID"), st.selectbox("Genre", ["Femme", "Homme", "Unisexe"]), 
                            st.text_input("Marque"), st.text_input("Nom"), 
                            st.text_input("Code"), st.number_input("Quantité", min_value=0)]
                if st.form_submit_button("Sauvegarder"):
                    # Logique pour ajouter une ligne au Google Sheet
                    new_row = pd.DataFrame([new_data], columns=df.columns)
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    conn.update(spreadsheet=url, data=updated_df)
                    st.success("Enregistré sur le Cloud !")
                    st.rerun()