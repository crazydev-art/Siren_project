import os
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import pool
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, date
from decimal import Decimal
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture detailed logs
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Output logs to the console
)

def get_postgres_pool(postgres_config):
    """Create a PostgreSQL connection pool."""
    return psycopg2.pool.ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        **postgres_config
    )

def get_mongo_client(mongo_config):
    """Create a MongoDB client."""
    mongo_uri = (
        f"mongodb://{mongo_config['USERNAME']}:{mongo_config['PASSWORD']}@"
        f"{mongo_config['IPHOST']}:{mongo_config['PORT']}/"
        f"{mongo_config['DATABASE']}?authSource=admin"
    )
    return MongoClient(mongo_uri)

def convert_dates(doc):
    """Convert datetime.date objects in a dictionary to datetime.datetime."""
    for key, value in doc.items():
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            doc[key] = datetime(value.year, value.month, value.day)
    return doc

def preprocess_document(doc):
    for key, value in doc.items():
        try:
            if isinstance(value, date) and not isinstance(value, datetime):
                doc[key] = datetime(value.year, value.month, value.day)
            elif isinstance(value, datetime):
                doc[key] = value.isoformat()  # Convert datetime to ISO format string
            elif isinstance(value, Decimal):
                doc[key] = float(value)
            elif isinstance(value, str):
                pass  # Strings are already compatible
            elif value is None:
                doc[key] = None  # Handle None explicitly if needed
            else:
                logging.warning(f"Unknown type for key: {key}, value: {value} ({type(value)}) - converting to string")
                doc[key] = str(value)  # Convert unsupported types to strings
        except Exception as e:
            logging.error(f"Error processing key: {key}, value: {value}, type: {type(value)} - {e}")
            raise
    return doc

def copy_single_table(postgres_pool, mongo_db, postgres_table, mongo_collection, batch_size=45000):
    """Transfer data from a PostgreSQL table to a MongoDB collection."""
    try:
        conn = postgres_pool.getconn()
        cursor = conn.cursor(cursor_factory=DictCursor)

        logging.info(f"Starting transfer for table: {postgres_table} -> collection: {mongo_collection}")

        # Fetch and transfer data in batches
        cursor.execute(f"SELECT * FROM {postgres_table};")
        mongo_col = mongo_db[mongo_collection]
        
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break

            # Preprocess documents to handle datetime.date
            documents = [preprocess_document(dict(row)) for row in rows]
            mongo_col.insert_many(documents)
            
            logging.info(f"Inserted {len(documents)} records from {postgres_table} to {mongo_collection}.")

    except Exception as e:
        logging.error(f"Error transferring data for table {postgres_table}: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            postgres_pool.putconn(conn)

def copy_table(postgres_config, mongo_config, table_map):
    """Main function to orchestrate the data transfer."""
    try:
        # Initialize PostgreSQL pool and MongoDB client
        postgres_pool = get_postgres_pool(postgres_config)
        mongo_client = get_mongo_client(mongo_config)
        mongo_db = mongo_client[mongo_config['DATABASE']]

        # Parallelize the transfer using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for postgres_table, mongo_collection in table_map.items():
                futures.append(executor.submit(copy_single_table, postgres_pool, mongo_db, postgres_table, mongo_collection))

            # Wait for all tasks to complete
            for future in futures:
                future.result()

        logging.info("Data transfer completed successfully.")

    except Exception as e:
        logging.error(f"Error during data transfer: {e}")

    finally:
        # Close the PostgreSQL connection pool
        if postgres_pool:
            postgres_pool.closeall()
        # Close the MongoDB client
        if mongo_client:
            mongo_client.close()

# PostgreSQL Configuration
postgres_config = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('IPHOST'),
    'port': 5432
}

# MongoDB Configuration
mongo_config = {
    'IPHOST': os.getenv('IPHOST', 'localhost'),
    'PORT': '27017',
    'DATABASE': 'siren',
    'USERNAME': os.getenv('MONGO_INITDB_ROOT_USERNAME'),
    'PASSWORD': os.getenv('MONGO_INITDB_ROOT_PASSWORD')
}

# Map of PostgreSQL tables to MongoDB collections
table_map = {
    'adresse': 'adresse',
    'categorie_juridique': 'categorie_juridique',
    'etablissement': 'etablissement',
    'geolocalisation': 'geolocalisation',
    'nafv2': 'nafv2',
    'unitelegale': 'unitelegale',
}

# Transfer data
if __name__ == "__main__":
    copy_table(postgres_config, mongo_config, table_map)
