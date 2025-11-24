#!/usr/bin/env python3
"""Script de vérification simple pour l'API Movies.

Exécute sans serveur en utilisant TestClient de FastAPI.
Actions:
 - reseed depuis data/movies.csv (idempotent)
 - liste les 5 films les plus profitables
 - crée un film de test (doit renvoyer 201)
 - tente de créer le même film (doit échouer 400)
 - supprime le film de test (doit renvoyer 204)

Usage:
    python scripts/check_api.py
"""
import os
import sys
import json
from fastapi.testclient import TestClient

# ensure project root is on sys.path so `import app` works when script run from scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app
from app.database import seed_from_csv

def main():
    project_root = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(project_root, 'data', 'movies.csv')
    print(f"Seeding DB from: {csv_path} (idempotent)")
    stats = seed_from_csv(csv_path)
    print("Seed stats:", stats)

    client = TestClient(app)

    # 1) lister 5 films les plus rentables (order_by=-profitability)
    print('\n1) Top 5 films par profitability:')
    r = client.get('/movies?order_by=-profitability&limit=5')
    if r.status_code != 200:
        print('Erreur GET /movies', r.status_code, r.text)
        return
    top5 = r.json()
    print(json.dumps(top5, ensure_ascii=False, indent=2))

    # 2) créer un film de test
    test_movie = {
        'title': 'Scripted Test Movie',
        'genre': 'Test',
        'studio': 'Unit',
        'year': 2099,
        'profitability': 1.23,
        'worldwide_gross': 10.0,
    }
    print('\n2) Création d\'un film de test:')
    r = client.post('/movies', json=test_movie)
    print('Status:', r.status_code)
    if r.status_code == 201:
        created = r.json()
        print('Créé:', json.dumps(created, ensure_ascii=False, indent=2))
        test_id = created['id']
    else:
        print('Réponse:', r.text)
        return

    # 3) tentative de doublon (doit échouer 400)
    print('\n3) Tentative de création d\'un doublon (même title+year):')
    r2 = client.post('/movies', json=test_movie)
    print('Status (doublon attendu 400):', r2.status_code)
    print('Body:', r2.text)

    # 4) suppression du film test
    print('\n4) Suppression du film test:')
    r3 = client.delete(f'/movies/{test_id}')
    print('Status (attendu 204):', r3.status_code)

if __name__ == '__main__':
    main()
