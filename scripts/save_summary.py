import os
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Get the connection string from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# Set up the database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a base for your model classes
Base = declarative_base()

# Define your data model for the summary
class Summary(Base):
    __tablename__ = "summaries"
    id = Column(String, primary_key=True)
    title = Column(String)
    content = Column(Text)

# Create the table in the database
Base.metadata.create_all(bind=engine)

def save_summary_to_db(summary_data: dict):
    """Saves a summary to the database."""
    db = SessionLocal()
    try:
        new_summary = Summary(
            id=summary_data['id'],
            title=summary_data['title'],
            content=summary_data['content']
        )
        db.add(new_summary)
        db.commit()
        print("Summary saved successfully!")
    except Exception as e:
        db.rollback()
        print(f"Failed to save summary: {e}")
    finally:
        db.close()

