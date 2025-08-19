import os
import pandas as pd
from sqlalchemy import create_engine

def export_summaries_to_excel():
    """Connects to the database, fetches summaries, and exports them to an Excel file."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("DATABASE_URL environment variable is not set.")
        return

    try:
        engine = create_engine(DATABASE_URL)
        print("Successfully connected to the database.")

        # Read the SQL query result directly into a pandas DataFrame
        query = "SELECT * FROM summaries;"
        df = pd.read_sql(query, engine)

        if not df.empty:
            # Export the DataFrame to an Excel file
            output_file = "summaries.xlsx"
            df.to_excel(output_file, index=False)
            print(f"Successfully exported {len(df)} records to '{output_file}'")
        else:
            print("No summaries found in the database to export.")

    except Exception as e:
        print(f"An error occurred during the export process: {e}")

if __name__ == "__main__":
    export_summaries_to_excel()