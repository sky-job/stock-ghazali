import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Ghazali Stock Pro", layout="wide")

# --- ⚠️ METTEZ VOTRE VRAI LIEN GOOGLE SHEETS CI-DESSOUS ⚠️ ---
url = "https://docs.google.com/spreadsheets/d/1vMgzCYFD2s7UVQ-TQ7ZK2A162QObv6c936Sx5X5uDt0/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url, ttl=10)
df = df.dropna(how="all") 

st.title("🧪 Inventaire Ghazali Parfums (Mode Cloud)")

# --- RECHERCHE ---
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

st.divider()

# --- AFFICHAGE COLONNES ---
col_table, col_panel = st.columns([7, 3])

with col_table:
    st.write(f"📊 Articles visibles : **{len(df_display)}**")
    st.dataframe(df_display, use_container_width=True, hide_index=True, height=600)

# --- ZONE SÉCURISÉE (MODIFICATIONS) ---
with col_panel:
    st.markdown("### 🔒 Zone Sécurisée")
    
    # Vérifier si l'utilisateur est connecté dans la mémoire de l'application
    if 'authentifie' not in st.session_state:
        st.session_state['authentifie'] = False
        
    # S'il n'est pas connecté, on affiche seulement la case mot de passe
    if not st.session_state['authentifie']:
        st.info("Verrouillé. Mot de passe requis pour modifier le stock.")
        mot_de_passe = st.text_input("Mot de passe :", type="password")
        
        if st.button("Déverrouiller"):
            # On vérifie avec le coffre-fort Streamlit
            if mot_de_passe == st.secrets["MDP_ADMIN"]:
                st.session_state['authentifie'] = True
                st.rerun()
            else:
                st.error("❌ Mot de passe incorrect")
                
    # S'il EST connecté, on affiche le menu de modification normal
    else:
        if st.button("🔒 Se déconnecter"):
            st.session_state['authentifie'] = False
            st.rerun()
            
        with st.expander("⚙️ Modifications", expanded=True):
            action = st.radio("Action :", ["➕ Ajouter", "📝 Modifier"], horizontal=True)
            
            if action == "➕ Ajouter":
                with st.form("ajout"):
                    n_id = st.text_input("ID")
                    n_genre = st.selectbox("Genre", ["Femme", "Homme", "Unisexe"])
                    n_marque = st.text_input("Marque")
                    n_nom = st.text_input("Nom")
                    n_code = st.text_input("Code")
                    n_qty = st.number_input("Quantité", min_value=0)
                    
                    if st.form_submit_button("Sauvegarder"):
                        new_row = pd.DataFrame([[n_id, n_genre, n_marque, n_nom, n_code, n_qty]], columns=df.columns)
                        updated_df = pd.concat([df, new_row], ignore_index=True)
                        conn.update(spreadsheet=url, data=updated_df)
                        st.success("Enregistré sur le Cloud !")
                        st.rerun()
                        
            elif action == "📝 Modifier":
                search_id = st.text_input("ID à modifier :")
                if search_id:
                    df['ID_str'] = df['ID'].astype(str)
                    if search_id in df['ID_str'].values:
                        idx = df.index[df['ID_str'] == search_id][0]
                        with st.form("modif"):
                            m_id = st.text_input("ID", value=str(df.at[idx, 'ID']))
                            genres = ["Femme", "Homme", "Unisexe"]
                            c_genre = df.at[idx, 'Genre']
                            g_idx = genres.index(c_genre) if c_genre in genres else 0
                            m_genre = st.selectbox("Genre", genres, index=g_idx)
                            m_marque = st.text_input("Marque", value=str(df.at[idx, 'Marque']))
                            m_nom = st.text_input("Nom", value=str(df.at[idx, 'Nom']))
                            m_code = st.text_input("Code", value=str(df.at[idx, 'Code']))
                            m_qty = st.number_input("Quantité", value=int(df.at[idx, 'Quantité']), min_value=0)
                            
                            if st.form_submit_button("Mettre à jour"):
                                df.loc[idx, ['ID', 'Genre', 'Marque', 'Nom', 'Code', 'Quantité']] = [m_id, m_genre, m_marque, m_nom, m_code, m_qty]
                                df_to_save = df.drop(columns=['ID_str'])
                                conn.update(spreadsheet=url, data=df_to_save)
                                st.success("Mis à jour !")
                                st.rerun()
                    else:
                        st.warning("ID introuvable.")
