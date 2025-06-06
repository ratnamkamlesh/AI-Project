import pymysql
import pandas as pd


def get_databases():
    conn = pymysql.connect(
        host='localhost',
        user='postgres',
        password='delhivery123',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES;")
    dbs = [row['Database'] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return dbs



def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='your_user',
        password='your_password',
        database='your_database',
        cursorclass=pymysql.cursors.DictCursor
    )

def get_table_names(database_name):
    conn = pymysql.connect(
        host='localhost',
        user='your_user',
        password='your_password',
        database=database_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    key = f'Tables_in_{database_name}'
    tables = [row[key] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return tables

def fetch_data(query, database=None):
    conn = pymysql.connect(
        host='localhost',
        user='your_user',
        password='your_password',
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df


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
