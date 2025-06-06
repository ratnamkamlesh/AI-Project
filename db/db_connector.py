import pymysql
import pandas as pd
import streamlit as st
from typing import Optional, List, Dict, Any
import traceback

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    st.warning("PostgreSQL support not available. Install psycopg2-binary for PostgreSQL connectivity.")

try:
    import pymongo
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False


class DatabaseConnector:
    def __init__(self, db_type: str, host: str, port: int, username: str, password: str, database: str = None):
        self.db_type = db_type.lower()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.connection = None

    def test_connection(self) -> Dict[str, Any]:
        """Test database connection and return status"""
        try:
            if self.db_type == 'mysql':
                return self._test_mysql_connection()
            elif self.db_type == 'postgresql':
                return self._test_postgresql_connection()
            elif self.db_type == 'mongodb':
                return self._test_mongodb_connection()
            elif self.db_type == 'sqlite':
                return self._test_sqlite_connection()
            else:
                return {"success": False, "error": f"Unsupported database type: {self.db_type}"}
        except Exception as e:
            return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

    def _test_mysql_connection(self) -> Dict[str, Any]:
        try:
            conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=10
            )
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            cursor.close()
            conn.close()
            return {"success": True, "message": f"Connected to MySQL {version['VERSION()']}", "type": "mysql"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_postgresql_connection(self) -> Dict[str, Any]:
        if not PSYCOPG2_AVAILABLE:
            return {"success": False, "error": "PostgreSQL driver not available. Install psycopg2-binary."}
        
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                database=self.database,
                cursor_factory=RealDictCursor,
                connect_timeout=10
            )
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            cursor.close()
            conn.close()
            return {"success": True, "message": f"Connected to PostgreSQL", "type": "postgresql"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_mongodb_connection(self) -> Dict[str, Any]:
        if not PYMONGO_AVAILABLE:
            return {"success": False, "error": "MongoDB driver not available. Install pymongo."}
        
        try:
            client = pymongo.MongoClient(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                serverSelectionTimeoutMS=10000
            )
            client.server_info()  # Test connection
            return {"success": True, "message": "Connected to MongoDB", "type": "mongodb"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_sqlite_connection(self) -> Dict[str, Any]:
        try:
            conn = sqlite3.connect(self.host)  # For SQLite, host is the file path
            conn.execute("SELECT sqlite_version()")
            conn.close()
            return {"success": True, "message": "Connected to SQLite", "type": "sqlite"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_databases(self) -> List[str]:
        """Get list of available databases"""
        try:
            if self.db_type == 'mysql':
                return self._get_mysql_databases()
            elif self.db_type == 'postgresql':
                return self._get_postgresql_databases()
            elif self.db_type == 'mongodb':
                return self._get_mongodb_databases()
            elif self.db_type == 'sqlite':
                return [self.host]  # SQLite has one database per file
            else:
                return []
        except Exception as e:
            st.error(f"Error getting databases: {str(e)}")
            return []

    def _get_mysql_databases(self) -> List[str]:
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        dbs = [row['Database'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return dbs

    def _get_postgresql_databases(self) -> List[str]:
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            database='postgres',  # Connect to default database
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
        dbs = [row['datname'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return dbs

    def _get_mongodb_databases(self) -> List[str]:
        client = pymongo.MongoClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password
        )
        return client.list_database_names()

    def get_tables(self, database: str) -> List[str]:
        """Get list of tables/collections in a database"""
        try:
            if self.db_type == 'mysql':
                return self._get_mysql_tables(database)
            elif self.db_type == 'postgresql':
                return self._get_postgresql_tables(database)
            elif self.db_type == 'mongodb':
                return self._get_mongodb_collections(database)
            elif self.db_type == 'sqlite':
                return self._get_sqlite_tables()
            else:
                return []
        except Exception as e:
            st.error(f"Error getting tables: {str(e)}")
            return []

    def _get_mysql_tables(self, database: str) -> List[str]:
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [list(row.values())[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables

    def _get_postgresql_tables(self, database: str) -> List[str]:
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            database=database,
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        tables = [row['tablename'] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tables

    def _get_mongodb_collections(self, database: str) -> List[str]:
        client = pymongo.MongoClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password
        )
        db = client[database]
        return db.list_collection_names()

    def _get_sqlite_tables(self) -> List[str]:
        conn = sqlite3.connect(self.host)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables

    def fetch_data(self, table_or_query: str, database: str = None, limit: int = 1000) -> pd.DataFrame:
        """Fetch data from table or execute query"""
        try:
            if self.db_type == 'mysql':
                return self._fetch_mysql_data(table_or_query, database, limit)
            elif self.db_type == 'postgresql':
                return self._fetch_postgresql_data(table_or_query, database, limit)
            elif self.db_type == 'mongodb':
                return self._fetch_mongodb_data(table_or_query, database, limit)
            elif self.db_type == 'sqlite':
                return self._fetch_sqlite_data(table_or_query, limit)
            else:
                return pd.DataFrame()
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            return pd.DataFrame()

    def _fetch_mysql_data(self, table_or_query: str, database: str, limit: int) -> pd.DataFrame:
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # Check if it's a query or table name
        if any(keyword in table_or_query.upper() for keyword in ['SELECT', 'WITH', 'SHOW']):
            query = table_or_query
        else:
            query = f"SELECT * FROM {table_or_query} LIMIT {limit}"
        
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    def _fetch_postgresql_data(self, table_or_query: str, database: str, limit: int) -> pd.DataFrame:
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            database=database
        )
        
        # Check if it's a query or table name
        if any(keyword in table_or_query.upper() for keyword in ['SELECT', 'WITH', 'SHOW']):
            query = table_or_query
        else:
            query = f"SELECT * FROM {table_or_query} LIMIT {limit}"
        
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    def _fetch_mongodb_data(self, collection: str, database: str, limit: int) -> pd.DataFrame:
        client = pymongo.MongoClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password
        )
        db = client[database]
        collection_obj = db[collection]
        documents = list(collection_obj.find().limit(limit))
        return pd.DataFrame(documents)

    def _fetch_sqlite_data(self, table_or_query: str, limit: int) -> pd.DataFrame:
        conn = sqlite3.connect(self.host)
        
        # Check if it's a query or table name
        if any(keyword in table_or_query.upper() for keyword in ['SELECT', 'WITH']):
            query = table_or_query
        else:
            query = f"SELECT * FROM {table_or_query} LIMIT {limit}"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df


# Convenience functions for backward compatibility
def get_databases():
    """Placeholder - requires connection setup"""
    return []

def get_table_names(database_name):
    """Placeholder - requires connection setup"""
    return []

def fetch_data(query, database=None):
    """Placeholder - requires connection setup"""
    return pd.DataFrame()


def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='your_user',
        password='your_password',
        database='your_database',
        cursorclass=pymysql.cursors.DictCursor
    )

def get_table_relationships(tables, database=None):
    conn = pymysql.connect(
        host='localhost',
        user='your_user',
        password='your_password',
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    format_strings = ','.join(['%s'] * len(tables))
    query = f"""
        SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s
          AND REFERENCED_TABLE_NAME IS NOT NULL
          AND TABLE_NAME IN ({format_strings})
          AND REFERENCED_TABLE_NAME IN ({format_strings});
    """
    params = [database] + tables + tables
    cursor.execute(query, params)
    rels = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"table": r["TABLE_NAME"], "key": r["COLUMN_NAME"], "related_table": r["REFERENCED_TABLE_NAME"]} for r in rels]
