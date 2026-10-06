import sys
sys.path.insert(0, r'D:\donation system\backend')
from app.database import engine
from sqlalchemy import text

# Add the location_unknown column to the deliveries table
with engine.connect() as conn:
    conn.execute(text("ALTER TABLE deliveries ADD COLUMN IF NOT EXISTS location_unknown BOOLEAN DEFAULT FALSE NOT NULL;"))
    conn.commit()
    print("Column location_unknown added successfully")
    
    # Verify
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='deliveries'"))
    print("Delivery table columns:")
    for row in result:
        print(f"  {row[0]}")