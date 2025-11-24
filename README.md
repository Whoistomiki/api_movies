# Movies API (FastAPI)

Ceci est une petite API CRUD pour des films, basée sur FastAPI et SQLite.

## Démarrer rapidement (sans environnement virtuel)

### 1. Ouvrir PowerShell et se placer dans la racine du projet :

```powershell
cd C:\Users\yu\Downloads\EFREI\api_movies
```

### 2. (Optionnel) Installer les dépendances si nécessaire :

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. (Optionnel) Reseed la base de données depuis le CSV (situé dans `data/movies.csv`) :

```powershell
# Supprime la BDD existante puis re-crée à partir de `data/movies.csv`
Remove-Item .\movies.db
python -m app.seed
```

### 4. Automatiser le seeding dès le lancement de l'API :

```
setx AUTO_SEED_LIMIT 10
```

### 5. Lancer le serveur FastAPI (sans virtualenv) :

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 6. Ouvrir la doc interactive : http://127.0.0.1:8000/docs

### 7. Test et check de l'api => scripts/check_api.py

## Endpoints principaux

- `GET /movies` : lister les films
- `GET /movies/{id}` : récupérer un film
- `POST /movies` : créer un film (JSON)
- `PUT /movies/{id}` : mettre à jour un film
- `DELETE /movies/{id}` : supprimer un film

## Exemple rapide PowerShell

Lister les films :

```powershell
Invoke-RestMethod http://127.0.0.1:8000/movies
```

Créer un film :

```powershell
$body = @{ title='Mon Film'; year=2025 } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/movies -Method Post -Body $body -ContentType 'application/json'
```

## Remarques

- Le fichier `movies.db` est créé à la racine après exécution du seed.
- Le CSV d'origine est `data/movies.csv`.
- Le serveur effectue un "auto-seed" au démarrage si la table `movies` est vide (le seed manuel via `python -m app.seed` reste disponible).
- Si `uvicorn` n'est pas installé, installe `uvicorn` via `pip` ou utilise la commande d'installation ci-dessus.
 - Le fichier `movies.db` est créé à la racine après exécution du seed.
 - Le CSV d'origine est `data/movies.csv`.
 - Le serveur effectue un "auto-seed" au démarrage si la table `movies` est vide. Par défaut l'auto-seed importe toute la partie non-duplicate du CSV, mais tu peux limiter le nombre d'enregistrements importés automatiquement en définissant la variable d'environnement `AUTO_SEED_LIMIT` (ex: `setx AUTO_SEED_LIMIT 20` sous Windows puis relancer le terminal). Si `AUTO_SEED_LIMIT` n'est pas défini, l'auto-seed importe tout.
 - Si `uvicorn` n'est pas installé, installe `uvicorn` via `pip` ou utilise la commande d'installation ci-dessus.
