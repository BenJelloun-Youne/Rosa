# Application de Visualisation des Données

Cette application Streamlit permet de visualiser et filtrer des données de contacts, avec les fonctionnalités suivantes :

- Filtrage par statut
- Visualisation des données avec des graphiques interactifs
- Téléchargement des contacts disponibles
- Gestion des contacts déjà téléchargés
- Historique des téléchargements

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/BenJelloun-Youne/Rosa.git
cd Rosa
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancer l'application :
```bash
streamlit run app.py
```

## Structure du Projet

- `app.py` : Application Streamlit principale
- `merged_data.db` : Base de données SQLite contenant les données
- `requirements.txt` : Liste des dépendances Python
- `db_mapper.py` : Module de mapping de la base de données

## Fonctionnalités

- Visualisation des données avec des graphiques interactifs
- Filtrage par statut
- Téléchargement des contacts disponibles
- Gestion des contacts déjà téléchargés
- Historique des téléchargements 