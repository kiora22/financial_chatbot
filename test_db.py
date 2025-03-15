import os
import sys
from sqlmodel import SQLModel, create_engine

# Add the parent directory to the path so we can import from our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings

def test_db():
    print(f"Database URL: {settings.database_url}")
    db_path = settings.sqlite_db_path
    print(f"DB Path: {db_path}")
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Test if we can write to the directory
    test_file = os.path.join(os.path.dirname(db_path), "test_write.txt")
    try:
        with open(test_file, "w") as f:
            f.write("test")
        print(f"Successfully wrote to {test_file}")
        os.remove(test_file)
    except Exception as e:
        print(f"Error writing to directory: {e}")
    
    # Try creating the database
    try:
        engine = create_engine(settings.database_url)
        SQLModel.metadata.create_all(engine)
        print("Successfully created database")
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    test_db()