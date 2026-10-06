import sys
sys.path.insert(0, r'D:\donation system\backend')
from app.database import SessionLocal, Base, engine
from sqlalchemy import inspect

# Check if the location_unknown column exists
inspector = inspect(engine)
columns = inspect(engine).get_columns('deliveries')
print('Delivery table columns:')
for c in columns:
    print(f'  {c["name"]}: {c["type"]} nullable={c["nullable"]} default={c["default"]}')