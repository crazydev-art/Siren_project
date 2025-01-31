import os
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import bcrypt

def create_user_db():
    # Get the database name from an environment variable
    db_name = os.getenv('POSTGRES_DB_USER', 'default_user_db')

    # Get PostgreSQL connection parameters from environment variables
    db_host = os.getenv('IPHOST', 'localhost')
    db_user = os.getenv('POSTGRES_USER', 'postgres')
    db_password = os.getenv('POSTGRES_PASSWORD', 'password')
    db_port = os.getenv('POSTGRES_PORT', '5432')

    try:
        # Connect to the PostgreSQL server
        conn = psycopg2.connect(
            dbname="postgres",
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Create the database
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"Database '{db_name}' created successfully.")

    except psycopg2.errors.DuplicateDatabase:
        print(f"Database '{db_name}' already exists.")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Database connection closed.")

def create_users_table():
    # Get the database name from an environment variable
    db_name = os.getenv('POSTGRES_DB_USER')

    # Get PostgreSQL connection parameters from environment variables
    db_host = os.getenv('IPHOST')
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_port = os.getenv('POSTGRES_PORT', '5432')

    try:
        # Connect to the specific database
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cursor = conn.cursor()

        # Create the users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Table 'users' created successfully.")

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Database connection closed.")

def create_admin_user():
    # Get the database name from an environment variable
    db_name = os.getenv('POSTGRES_DB_USER')

    # Get PostgreSQL connection parameters from environment variables
    db_host = os.getenv('IPHOST')
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_port = os.getenv('POSTGRES_PORT', '5432')

    # Admin user details
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@gmail.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin_password')  # Plaintext password

    # Hash the admin password
    hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        # Connect to the specific database
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cursor = conn.cursor()

        # Insert the admin user
        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        """, (admin_username, admin_email, hashed_password))
        conn.commit()
        print("Admin user created successfully (or already exists).")

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    create_user_db()
    create_users_table()
    create_admin_user()
