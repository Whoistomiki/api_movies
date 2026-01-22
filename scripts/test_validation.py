import os
import sys
from fastapi.testclient import TestClient

# Ajout du dossier racine au path pour l'import d'app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)

def test_validation():
    print("--- DÉBUT DES TESTS DE VALIDATION (TP 4) ---\n")

    # 1. Test du Genre non autorisé (doit renvoyer 422)
    print("1) Test genre invalide ('Horreur')...")
    bad_genre = {
        "title": "Inception",
        "genre": "Horreur", # Pas dans la liste autorisée
        "studio": "Warner Bros",
        "year": 2010
    }
    r = client.post("/movies", json=bad_genre)
    print(f"Status: {r.status_code} (Attendu: 422)")
    
    # 2. Test du Titre trop court (doit renvoyer 422)
    print("\n2) Test titre trop court ('A')...")
    bad_title = {
        "title": "A", # min_length = 2
        "genre": "Action",
        "studio": "Test",
        "year": 2020
    }
    r = client.post("/movies", json=bad_title)
    print(f"Status: {r.status_code} (Attendu: 422)")

    # 3. Test de l'Année future (doit renvoyer 422 via le validateur dynamique)
    print("\n3) Test année future (2030)...")
    bad_year = {
        "title": "Future Movie",
        "genre": "Sci-Fi",
        "studio": "Mars Studio",
        "year": 2030 # Supérieur à l'année actuelle
    }
    r = client.post("/movies", json=bad_year)
    print(f"Status: {r.status_code} (Attendu: 422)")
    if r.status_code == 422:
        print(f"Message d'erreur: {r.json()['detail'][0]['msg']}")

    # 4. Test des valeurs par défaut (doit renvoyer 201)
    print("\n4) Test valeurs par défaut (scores absents)...")
    default_movie = {
        "title": "Minimal Movie",
        "genre": "Drama",
        "studio": "Indie Studio",
        "year": 2022
        # audience_score et rotten_tomatoes sont absents
    }
    r = client.post("/movies", json=default_movie)
    if r.status_code == 201:
        data = r.json()
        print(f"Status: 201. Scores par défaut -> Audience: {data['audience_score']}, Rotten: {data['rotten_tomatoes']}")
        # Nettoyage
        client.delete(f"/movies/{data['id']}")

if __name__ == "__main__":
    test_validation()