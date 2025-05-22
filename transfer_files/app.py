import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from db_mapper import MergedData
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Visualisation des Données",
    page_icon="📊",
    layout="wide"
)

# Initialisation des variables de session
if 'downloaded_contacts' not in st.session_state:
    st.session_state.downloaded_contacts = set()
if 'download_history' not in st.session_state:
    st.session_state.download_history = []

# Titre de l'application
st.title("📊 Visualisation et Filtrage des Données")

# Connexion à la base de données avec mise en cache
@st.cache_data(ttl=3600)  # Cache pour 1 heure
def load_data():
    conn = sqlite3.connect('merged_data.db')
    # Optimisation : ne charger que les colonnes nécessaires
    df = pd.read_sql_query("""
        SELECT 
            "Nom du statut",
            "Nombre de fois appelé",
            "Prénom",
            "Nom",
            "Téléphone",
            "Email",
            "source_file"
        FROM merged_data
    """, conn)
    conn.close()
    return df

# Chargement des données
df = load_data()

# Sidebar pour les filtres
st.sidebar.header("Filtres")

# Filtre pour le statut
status_options = sorted(df['Nom du statut'].unique())
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
    filtered_df = filtered_df[filtered_df['Nom du statut'].isin(selected_status)]

# Filtrer les contacts déjà téléchargés
available_contacts = filtered_df[~filtered_df['Téléphone'].isin(st.session_state.downloaded_contacts)]

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
status_counts = available_contacts['Nom du statut'].value_counts()
for status, count in status_counts.items():
    st.write(f"**{status}**: {count} enregistrements disponibles")

# Visualisations
st.header("Visualisations")

# Graphique du nombre d'appels par statut
fig_calls = px.histogram(
    available_contacts,
    x='Nombre de fois appelé',
    color='Nom du statut',
    title='Distribution des appels par statut (contacts disponibles uniquement)',
    barmode='group'
)
st.plotly_chart(fig_calls, use_container_width=True)

# Graphique des statuts
fig_status = px.pie(
    available_contacts,
    names='Nom du statut',
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
        st.session_state.downloaded_contacts.update(contacts_to_download['Téléphone'].tolist())
        # Ajouter à l'historique des téléchargements
        st.session_state.download_history.append({
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'statuts': selected_status,
            'nombre_contacts': len(contacts_to_download)
        })
        st.success(f"{len(contacts_to_download)} contacts téléchargés avec succès !")
        st.experimental_rerun()
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
    st.experimental_rerun() 