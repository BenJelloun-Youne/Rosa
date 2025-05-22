import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from db_mapper import MergedData
from datetime import datetime
import os
import json

# Configuration de la page
st.set_page_config(
    page_title="Rosa - Analyse des Contacts",
    page_icon="📊",
    layout="wide"
)

# Fonction pour obtenir le chemin absolu de la base de données
def get_db_path():
    # Essayer d'abord le chemin relatif
    db_path = 'merged_data.db'
    if not os.path.exists(db_path):
        # Si non trouvé, chercher dans le répertoire parent
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(parent_dir, 'merged_data.db')
        if not os.path.exists(db_path):
            # Si toujours non trouvé, chercher dans le répertoire courant
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, 'merged_data.db')
    return db_path

# Initialisation des variables de session
if 'downloaded_contacts' not in st.session_state:
    st.session_state.downloaded_contacts = set()
if 'download_history' not in st.session_state:
    st.session_state.download_history = []

# Titre de l'application
st.title("📊 Visualisation et Filtrage des Données")

# Chargement des données avec gestion d'erreur
@st.cache_data(ttl=3600)
def load_data():
    try:
        db_path = get_db_path()
        if not os.path.exists(db_path):
            st.error(f"Base de données non trouvée à l'emplacement : {db_path}")
            return None
            
        conn = sqlite3.connect(db_path)
        query = """
        SELECT 
            "Nom du statut" as status,
            "Nombre de fois appelé" as total_calls,
            "Prénom" as first_name,
            "Nom" as last_name,
            "Téléphone" as phone_number,
            "Email" as email,
            "source_file"
        FROM merged_data
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return None

# Chargement des données
try:
    df = load_data()
except Exception as e:
    st.error(f"Erreur lors du chargement de la base de données : {str(e)}")
    st.stop()

# Sidebar pour les filtres
st.sidebar.header("Filtres")

# Filtre pour le statut
status_options = sorted(df['status'].unique())
selected_status = st.sidebar.multiselect(
    "Sélectionnez le(s) statut(s)",
    options=status_options,
    default=[]
)

# Nombre de lignes à télécharger
num_rows = st.sidebar.number_input(
    "Nombre de lignes à télécharger",
    min_value=1,
    max_value=len(df),
    value=100,
    step=1
)

# Application des filtres
filtered_df = df.copy()
if selected_status:
    filtered_df = filtered_df[filtered_df['status'].isin(selected_status)]

# Filtrer les contacts déjà téléchargés
available_contacts = filtered_df[~filtered_df['phone_number'].isin(st.session_state.downloaded_contacts)]

# Affichage des statistiques
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total des enregistrements", len(df))
with col2:
    st.metric("Enregistrements disponibles", len(available_contacts))
with col3:
    st.metric("Contacts déjà téléchargés", len(st.session_state.downloaded_contacts))
with col4:
    st.metric("Pourcentage disponible", f"{(len(available_contacts)/len(df)*100):.1f}%")

# Affichage des compteurs par statut
st.subheader("Répartition par statut")
status_counts = available_contacts['status'].value_counts()
for status, count in status_counts.items():
    st.write(f"**{status}**: {count} enregistrements disponibles")

# Visualisations
st.header("Visualisations")

# Graphique du nombre d'appels par statut
fig_calls = px.histogram(
    available_contacts,
    x='total_calls',
    color='status',
    title='Distribution des appels par statut (contacts disponibles uniquement)',
    barmode='group'
)
st.plotly_chart(fig_calls, use_container_width=True)

# Graphique des statuts
fig_status = px.pie(
    available_contacts,
    names='status',
    title='Répartition des statuts (contacts disponibles uniquement)'
)
st.plotly_chart(fig_status, use_container_width=True)

# Affichage des données filtrées
st.header("Contacts Disponibles")
st.dataframe(
    available_contacts.head(num_rows),
    use_container_width=True,
    hide_index=True
)

# Gestion du téléchargement
if len(available_contacts) > 0:
    # Limiter le nombre de lignes à télécharger
    contacts_to_download = available_contacts.head(num_rows)
    csv = contacts_to_download.to_csv(index=False).encode('utf-8')
    if st.download_button(
        "📥 Télécharger les contacts disponibles",
        csv,
        "contacts_disponibles.csv",
        "text/csv",
        key='download-csv'
    ):
        # Ajouter les contacts téléchargés à l'ensemble
        st.session_state.downloaded_contacts.update(contacts_to_download['phone_number'].tolist())
        # Ajouter à l'historique des téléchargements
        st.session_state.download_history.append({
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'statuts': selected_status,
            'nombre_contacts': len(contacts_to_download)
        })
        st.success(f"{len(contacts_to_download)} contacts téléchargés avec succès !")
        st.rerun()
else:
    st.warning("⚠️ Aucun contact disponible pour le téléchargement avec ces filtres.")

# Affichage de l'historique des téléchargements
if st.session_state.download_history:
    st.header("Historique des téléchargements")
    history_df = pd.DataFrame(st.session_state.download_history)
    st.dataframe(history_df, use_container_width=True)

# Option pour réinitialiser les contacts téléchargés
if st.sidebar.button("🔄 Réinitialiser l'historique des téléchargements"):
    st.session_state.downloaded_contacts = set()
    st.session_state.download_history = []
    st.success("Historique des téléchargements réinitialisé !")
    st.rerun() 