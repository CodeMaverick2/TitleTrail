import os
import sys
import django
from django.core.management import call_command
from django.db import connection

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

def setup_database():
    """
    Set up the database tables
    """
    print("Setting up database tables...")
    
    # Check if tables already exist
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'property_details'
            );
        """)
        tables_exist = cursor.fetchone()[0]
    
    if tables_exist:
        print("Tables already exist. Skipping creation.")
        return
    
    # Create tables
    from models import PropertyDetails, PropertyImage
    
    # Run migrations
    call_command('makemigrations', interactive=False)
    call_command('migrate', interactive=False)
    
    print("Database tables created successfully.")

if __name__ == "__main__":
    setup_database()