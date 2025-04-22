import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in the parent directory (project root)
dotenv_path = Path(__file__).resolve().parent.parent / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path)
    print(f"INIT_DB: Loaded environment variables from {dotenv_path}")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("init_db.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("InitDB")

def init_database():
    """
    Initialize the PostgreSQL database
    """
    # Get database connection parameters from environment variables
    db_name = os.environ.get('DB_NAME') or os.environ.get('DATABASE_NAME')
    db_user = os.environ.get('DB_USER') or os.environ.get('DATABASE_USER')
    db_password = os.environ.get('DB_PASSWORD') or os.environ.get('DATABASE_PASSWORD')
    db_host = os.environ.get('DB_HOST', 'localhost') or os.environ.get('DATABASE_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432') or os.environ.get('DATABASE_PORT', '5432')
    
    # Print the database connection parameters for debugging
    logger.info(f"Database connection parameters:")
    logger.info(f"DB_NAME: {db_name}")
    logger.info(f"DB_USER: {db_user}")
    logger.info(f"DB_HOST: {db_host}")
    logger.info(f"DB_PORT: {db_port}")
    
    try:
        # Connect to PostgreSQL server using the postgres database
        logger.info(f"Connecting to PostgreSQL server at {db_host}:{db_port}")
        conn = psycopg2.connect(
            dbname="postgres",
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            logger.info(f"Creating database '{db_name}'")
            cursor.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"Database '{db_name}' created successfully")
        else:
            logger.info(f"Database '{db_name}' already exists")
        
        # Close connection
        cursor.close()
        conn.close()
        
        # Connect to the newly created database
        logger.info(f"Connecting to database '{db_name}'")
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'property_details'
            );
        """)
        tables_exist = cursor.fetchone()[0]
        
        if not tables_exist:
            # Create tables
            logger.info("Creating tables")
            
            # Create property_details table
            cursor.execute("""
                CREATE TABLE property_details (
                    id SERIAL PRIMARY KEY,
                    survey_number VARCHAR(50),
                    surnoc VARCHAR(50),
                    hissa VARCHAR(50),
                    village VARCHAR(100),
                    hobli VARCHAR(100),
                    taluk VARCHAR(100),
                    district VARCHAR(100),
                    owner_name TEXT,
                    owner_details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create property_images table
            cursor.execute("""
                CREATE TABLE property_images (
                    id SERIAL PRIMARY KEY,
                    property_id INTEGER REFERENCES property_details(id) ON DELETE CASCADE,
                    image_data BYTEA,
                    image_type VARCHAR(50),
                    year_period VARCHAR(50),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create indexes for faster queries
            cursor.execute("""
                CREATE INDEX idx_property_details_survey_number ON property_details(survey_number);
                CREATE INDEX idx_property_details_village ON property_details(village);
                CREATE INDEX idx_property_details_district ON property_details(district);
                CREATE INDEX idx_property_images_property_id ON property_images(property_id);
            """)
            
            # Commit changes
            conn.commit()
            
            logger.info("Tables created successfully")
        else:
            logger.info("Tables already exist")
        
        # Close connection
        cursor.close()
        conn.close()
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()