import glob
import os
from src.common.database import SessionLocal
from src.ingestion.csv_loader import load_csv_to_db

def main():
    csv_files = glob.glob("data/synthetic/*.csv")

    if not csv_files:
        print("No CSV files found in data/synthetic/")
        return

    db = SessionLocal()
    try:
        for csv_path in csv_files:
            print(f"\nLoading {csv_path} ...")
            load_csv_to_db(db, csv_path)
    finally:
        db.close()

if __name__ == "__main__":
    main()