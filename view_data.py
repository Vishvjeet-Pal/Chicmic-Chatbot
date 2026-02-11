from sqlalchemy import create_engine, inspect, text

# Path to your SQLite database
DB_PATH = "test.db"   # change this

# Create engine
engine = create_engine(f"sqlite:///{DB_PATH}")

# Inspector to get table names
inspector = inspect(engine)

# Get all tables
tables = inspector.get_table_names()

print(f"Found tables: {tables}\n")

# Query all tables
with engine.connect() as conn:
    for table in tables:
        print(f"===== Table: {table} =====")
        
        result = conn.execute(text(f"SELECT * FROM {table}"))
        rows = result.fetchall()

        if not rows:
            print("No data\n")
            continue

        # Print column names
        print(result.keys())

        # Print rows
        for row in rows:
            print(dict(row._mapping))  # SQLAlchemy 1.4+

        print("\n")
