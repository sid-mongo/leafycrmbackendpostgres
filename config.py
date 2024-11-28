import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    # Replace these values with your RDS credentials
    DB_HOST = "hackathon.cluster-cbdbqao3phxo.ap-south-1.rds.amazonaws.com"  # RDS endpoint without 'http://'
    DB_PORT = "5432"  # Default PostgreSQL port, change if different
    DB_NAME = "leafycrm"  # Database name
    DB_USER = "postgres"  # RDS username
    DB_PASSWORD = "hackathon"  # RDS password

    # Construct the database URI for SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
