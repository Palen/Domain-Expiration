from pymongo import MongoClient


def get_db_conn(config):
    """
    Get DB Connection from a provided `Config` instance
    """
    client = MongoClient(config.get('MONGO', 'host'), int(config.get('MONGO', 'port')))
    conn = client[config.get('MONGO', 'db_name')]
    return conn
