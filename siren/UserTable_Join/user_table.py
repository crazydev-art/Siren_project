import os
import logging
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import bcrypt

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_env_variable(var_name, default=None, required=True):
    """Fetch an environment variable or raise an error if it's required and not set."""
    value = os.getenv(var_name, default)
    if required and value is None:
        raise EnvironmentError(f"Environment variable '{var_name}' is not set.")
    return value

# def create_user_db():
#     # Get the database name from an environment variable
#     # db_name = os.getenv('POSTGRES_DB_USER')

#     # Get PostgreSQL connection parameters from environment variables
#     # db_host = os.getenv('IPHOST')
#     # db_user = os.getenv('POSTGRES_USER')
#     # db_password = os.getenv('POSTGRES_PASSWORD')
#     # db_port = os.getenv('POSTGRES_PORT')

#     db_name = get_env_variable('POSTGRES_DB_USER')
#     db_host = get_env_variable('IPHOST')
#     db_user = get_env_variable('POSTGRES_USER')
#     db_password = get_env_variable('POSTGRES_PASSWORD')
#     db_port = get_env_variable('POSTGRES_PORT', '5432', required=False)

def create_user_db():
    db_name = get_env_variable('POSTGRES_DB_USER')
    db_host = get_env_variable('IPHOST')
    db_user = get_env_variable('POSTGRES_USER')
    db_password = get_env_variable('POSTGRES_PASSWORD')
    db_port = get_env_variable('POSTGRES_PORT', '5432', required=False)

    try:
        # Connect to the default 'postgres' database to create a new database
        conn = psycopg2.connect(
            dbname="postgres", user=db_user, password=db_password, host=db_host, port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # Required for CREATE DATABASE

        with conn.cursor() as cursor:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            logger.info(f"Database '{db_name}' created successfully.")

        conn.close()  # Close connection after creation
    except psycopg2.errors.DuplicateDatabase:
        logger.info(f"Database '{db_name}' already exists.")
    except psycopg2.Error as e:
        logger.error(f"An error occurred while creating the database: {e}")
    finally:
        if conn:
            conn.close()
    # try:
    #     with psycopg2.connect(dbname="postgres", user=db_user, password=db_password, host=db_host, port=db_port) as conn:
    #         conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    #         with conn.cursor() as cursor:
    #             cursor.execute(sql.SQL("CREATE DATABASE {}" ).format(sql.Identifier(db_name)))
    #             logger.info(f"Database '{db_name}' created successfully.")
    # except psycopg2.errors.DuplicateDatabase:
    #     logger.info(f"Database '{db_name}' already exists.")
    # except psycopg2.Error as e:
    #     logger.error(f"An error occurred while creating the database: {e}")

def create_users_table():
    db_name = get_env_variable('POSTGRES_DB_USER')
    db_host = get_env_variable('IPHOST')
    db_user = get_env_variable('POSTGRES_USER')
    db_password = get_env_variable('POSTGRES_PASSWORD')
    db_port = get_env_variable('POSTGRES_PORT', '5432', required=False)

    try:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port) as conn:
            with conn.cursor() as cursor:
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
                logger.info("Table 'users' created successfully.")
    except psycopg2.Error as e:
        logger.error(f"An error occurred while creating the table: {e}")

def create_admin_user():
    db_name = get_env_variable('POSTGRES_DB_USER')
    db_host = get_env_variable('IPHOST')
    db_user = get_env_variable('POSTGRES_USER')
    db_password = get_env_variable('POSTGRES_PASSWORD')
    db_port = get_env_variable('POSTGRES_PORT', '5432', required=False)

    admin_username = get_env_variable('ADMIN_USERNAME', 'admin', required=False)
    admin_email = get_env_variable('ADMIN_EMAIL', 'admin@gmail.com', required=False)
    admin_password = get_env_variable('ADMIN_PASSWORD', 'admin_password', required=False)

    hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (username, email, password)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (username) DO NOTHING
                """, (admin_username, admin_email, hashed_password))
                conn.commit()
                logger.info("Admin user created successfully (or already exists).")
    except psycopg2.Error as e:
        logger.error(f"An error occurred while creating the admin user: {e}")
    # try:
    #     # Connect to the PostgreSQL server
    #     conn = psycopg2.connect(
    #         dbname="postgres",
    #         user=db_user,
    #         password=db_password,
    #         host=db_host,
    #         port=db_port
    #     )
    #     conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    #     cursor = conn.cursor()

    #     # Create the database
    #     cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
    #     print(f"Database '{db_name}' created successfully.")

    # except psycopg2.errors.DuplicateDatabase:
    #     print(f"Database '{db_name}' already exists.")
    # except psycopg2.Error as e:
    #     print(f"An error occurred: {e}")
    # finally:
    #     if conn:
    #         cursor.close()
    #         conn.close()
    #         print("Database connection closed.")

# def create_users_table():
#     # Get the database name from an environment variable
#     db_name = os.getenv('POSTGRES_DB_USER')

#     # Get PostgreSQL connection parameters from environment variables
#     db_host = os.getenv('IPHOST')
#     db_user = os.getenv('POSTGRES_USER')
#     db_password = os.getenv('POSTGRES_PASSWORD')
#     db_port = os.getenv('POSTGRES_PORT', '5432')

#     try:
#         # Connect to the specific database
#         conn = psycopg2.connect(
#             dbname=db_name,
#             user=db_user,
#             password=db_password,
#             host=db_host,
#             port=db_port
#         )
#         cursor = conn.cursor()

#         # Create the users table
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS users (
#                 id SERIAL PRIMARY KEY,
#                 username VARCHAR(50) NOT NULL UNIQUE,
#                 email VARCHAR(100) NOT NULL UNIQUE,
#                 password TEXT NOT NULL,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )
#         """)
#         conn.commit()
#         print("Table 'users' created successfully.")

#     except psycopg2.Error as e:
#         print(f"An error occurred: {e}")
#     finally:
#         if conn:
#             cursor.close()
#             conn.close()
#             print("Database connection closed.")

# def create_admin_user():
#     # Get the database name from an environment variable
#     db_name = os.getenv('POSTGRES_DB_USER')

#     # Get PostgreSQL connection parameters from environment variables
#     db_host = os.getenv('IPHOST')
#     db_user = os.getenv('POSTGRES_USER')
#     db_password = os.getenv('POSTGRES_PASSWORD')
#     db_port = os.getenv('POSTGRES_PORT', '5432')

#     # Admin user details
#     admin_username = os.getenv('ADMIN_USERNAME', 'admin')
#     admin_email = os.getenv('ADMIN_EMAIL', 'admin@gmail.com')
#     admin_password = os.getenv('ADMIN_PASSWORD', 'admin_password')  # Plaintext password

#     # Hash the admin password
#     hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

#     try:
#         # Connect to the specific database
#         conn = psycopg2.connect(
#             dbname=db_name,
#             user=db_user,
#             password=db_password,
#             host=db_host,
#             port=db_port
#         )
#         cursor = conn.cursor()

#         # Insert the admin user
#         cursor.execute("""
#             INSERT INTO users (username, email, password)
#             VALUES (%s, %s, %s)
#             ON CONFLICT (username) DO NOTHING
#         """, (admin_username, admin_email, hashed_password))
#         conn.commit()
#         print("Admin user created successfully (or already exists).")

#     except psycopg2.Error as e:
#         print(f"An error occurred: {e}")
#     finally:
#         if conn:
#             cursor.close()
#             conn.close()
#             print("Database connection closed.")

if __name__ == "__main__":
    create_user_db()
    create_users_table()
    create_admin_user()
