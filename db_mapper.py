import sqlite3
from typing import List, Any, Dict
import pandas as pd

class MergedData:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @staticmethod
    def get_columns(db_path: str = 'merged_data.db') -> List[str]:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info(merged_data)')
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        return columns

    @staticmethod
    def fetch_all(db_path: str = 'merged_data.db') -> List['MergedData']:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM merged_data')
        columns = [description[0] for description in cursor.description]
        results = []
        for row in cursor.fetchall():
            data = dict(zip(columns, row))
            results.append(MergedData(**data))
        conn.close()
        return results

    @staticmethod
    def get_duplicates(db_path: str = 'merged_data.db') -> Dict[str, int]:
        """Retourne un dictionnaire des colonnes avec leur nombre de doublons"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupération des colonnes
        cursor.execute('PRAGMA table_info(merged_data)')
        columns = [row[1] for row in cursor.fetchall()]
        
        duplicates = {}
        for column in columns:
            try:
                cursor.execute(f'''
                    SELECT "{column}", COUNT(*) as count
                    FROM merged_data
                    GROUP BY "{column}"
                    HAVING COUNT(*) > 1
                ''')
                results = cursor.fetchall()
                if results:
                    duplicates[column] = len(results)
            except sqlite3.OperationalError:
                print(f"Impossible d'analyser les doublons pour la colonne: {column}")
        
        conn.close()
        return duplicates

    @staticmethod
    def get_statistics(db_path: str = 'merged_data.db') -> Dict[str, Any]:
        """Retourne des statistiques sur la base de données"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Nombre total d'enregistrements
        cursor.execute('SELECT COUNT(*) FROM merged_data')
        stats['total_records'] = cursor.fetchone()[0]
        
        # Nombre de fichiers sources uniques
        cursor.execute('SELECT COUNT(DISTINCT source_file) FROM merged_data')
        stats['unique_sources'] = cursor.fetchone()[0]
        
        # Date du premier et dernier import
        cursor.execute('SELECT MIN(import_date), MAX(import_date) FROM merged_data')
        min_date, max_date = cursor.fetchone()
        stats['first_import'] = min_date
        stats['last_import'] = max_date
        
        conn.close()
        return stats

if __name__ == "__main__":
    # Affiche les colonnes de la table merged_data
    print("Colonnes de la table merged_data :")
    print(MergedData.get_columns())
    
    # Affiche les statistiques
    print("\nStatistiques de la base de données :")
    stats = MergedData.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Affiche les doublons potentiels
    print("\nAnalyse des doublons par colonne :")
    duplicates = MergedData.get_duplicates()
    if duplicates:
        for column, count in duplicates.items():
            print(f"{column}: {count} doublons trouvés")
    else:
        print("Aucun doublon trouvé")
    
    # Exemple pour afficher les 5 premiers enregistrements
    print("\nExemple d'enregistrements :")
    for obj in MergedData.fetch_all()[:5]:
        print(obj.__dict__) 