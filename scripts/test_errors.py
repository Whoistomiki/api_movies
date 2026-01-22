import os
import sys
from fastapi.testclient import TestClient

# Ajout de la racine du projet pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)

def run_tp4_tests():
    print("=== TEST DES GESTIONS D'ERREURS (TP 4) ===\n")

    # --- 1. TEST ERREUR 422 (Validation Pydantic) ---
    print("1) Test 422 - Validation Pydantic (Titre trop court)")
    r = client.post("/movies/", json={"title": "A", "genre": "Action", "studio": "Test", "year": 2020})
    print(f"   Status: {r.status_code} | Attendu: 422")

    # --- 2. TEST ERREUR 409 (Conflit / Doublon) ---
    print("\n2) Test 409 - Conflit (Film déjà existant)")
    # On utilise un film connu du CSV (ex: Twilight)
    duplicate_movie = {
        "title": "Twilight", 
        "genre": "Romance", 
        "studio": "Summit", 
        "year": 2008
    }
    # Premier essai (peut-être déjà là ou créé)
    client.post("/movies/", json=duplicate_movie)
    # Deuxième essai pour déclencher le 409
    r = client.post("/movies/", json=duplicate_movie)
    print(f"   Status: {r.status_code} | Attendu: 409")
    print(f"   Message: {r.json().get('detail')}")

    # --- 3. TEST ERREUR 400 (Règle Métier) ---
    print("\n3) Test 400 - Règle Métier (Film récent score 0%)")
    bad_rule_movie = {
        "title": "Future Flop",
        "genre": "Comedy",
        "studio": "Test",
        "year": 2025,
        "audience_score": 0
    }
    r = client.post("/movies/", json=bad_rule_movie)
    print(f"   Status: {r.status_code} | Attendu: 400")
    print(f"   Message: {r.json().get('detail')}")

    # --- 4. TEST ERREUR 404 (Ressource introuvable) ---
    print("\n4) Test 404 - GET sur ID inexistant")
    r = client.get("/movies/999999")
    print(f"   Status: {r.status_code} | Attendu: 404")

    print("\n5) Test 404 - DELETE sur ID inexistant")
    r = client.delete("/movies/999999")
    print(f"   Status: {r.status_code} | Attendu: 404")

    # --- 5. TEST SUCCÈS (Pour vérifier que tout fonctionne encore) ---
    print("\n6) Test 201 - Création valide avec valeurs par défaut")
    valid_movie = {
        "title": "TP4 Success Movie",
        "genre": "Drama",
        "studio": "Efrei Studio",
        "year": 2023
    }
    r = client.post("/movies/", json=valid_movie)
    if r.status_code == 201:
        data = r.json()
        print(f"   Status: 201 | Scores par défaut: Audience={data['audience_score']}, Rotten={data['rotten_tomatoes']}")
        # Nettoyage
        client.delete(f"/movies/{data['id']}")

if __name__ == "__main__":
    run_tp4_tests()