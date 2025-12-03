from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_PORT = os.getenv('DATABASE_PORT', 5432)
DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')

DATABASE_URL = "sqlite:///icici.db"
#f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
#"sqlite:///icici.db"

engine = create_engine(DATABASE_URL, echo=False) 

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


