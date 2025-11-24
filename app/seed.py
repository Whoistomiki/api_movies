"""Small script to seed the SQLite DB from the CSV.

Usage (from project root):
  python -m app.seed
"""
import os
from .database import seed_from_csv

def main():
    # assume movies.csv is located in the project `data` folder
    project_root = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(project_root, 'data', 'movies.csv')
  print(f"Seeding DB from: {csv_path}")
  # seed_full by default when called manually
  seed_from_csv(csv_path)
    print("Seeding finished. DB: movies.db")

if __name__ == '__main__':
    main()
