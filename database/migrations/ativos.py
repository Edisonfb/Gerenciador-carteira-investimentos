import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import pandas
from app.db.session import engine

df = pandas.read_csv('..//database/seeds/ativos.csv')

df.to_sql('ativo', con=engine, if_exists='append', index=False)