import pandas as pd
import sqlite3
import glob
import os
from datetime import datetime

def create_clean_database():
    # Suppression de l'ancienne base si elle existe
    if os.path.exists('merged_data.db'):
        os.remove('merged_data.db')
    
    # Création de la nouvelle base de données
    conn = sqlite3.connect('merged_data.db')
    return conn

def remove_duplicates(conn):
    cursor = conn.cursor()
    
    # Création d'une table temporaire sans doublons
    cursor.execute('''
        CREATE TABLE temp_merged_data AS
        SELECT DISTINCT * FROM merged_data
    ''')
    
    # Suppression de l'ancienne table
    cursor.execute('DROP TABLE merged_data')
    
    # Renommage de la table temporaire
    cursor.execute('ALTER TABLE temp_merged_data RENAME TO merged_data')
    
    # Création des index
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_source_file ON merged_data(source_file)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_import_date ON merged_data(import_date)')
    
    conn.commit()

def process_csv_files():
    # Récupération de tous les fichiers CSV
    csv_files = glob.glob('*.csv')
    
    # Création de la base de données propre
    conn = create_clean_database()
    
    # Traitement de chaque fichier CSV
    for csv_file in csv_files:
        try:
            # Lecture du fichier CSV avec séparateur point-virgule
            df = pd.read_csv(csv_file, encoding='utf-8', sep=';')
            
            # Ajout d'une colonne pour identifier la source
            df['source_file'] = csv_file
            
            # Ajout d'une colonne pour la date d'import
            df['import_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Écriture dans la base de données
            table_name = 'merged_data'
            df.to_sql(table_name, conn, if_exists='append', index=False)
            
            print(f"Fichier traité avec succès : {csv_file}")
            
        except Exception as e:
            print(f"Erreur lors du traitement du fichier {csv_file}: {str(e)}")
    
    # Suppression des doublons
    print("\nSuppression des doublons...")
    remove_duplicates(conn)
    
    # Affichage du nombre total d'enregistrements
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM merged_data')
    total_records = cursor.fetchone()[0]
    print(f"\nNombre total d'enregistrements uniques : {total_records}")
    
    conn.close()

if __name__ == "__main__":
    process_csv_files() 