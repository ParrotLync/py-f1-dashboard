import sqlite3
import pandas as pd


def get_df(query: str, *args):
    conn = sqlite3.connect("data.db")
    df = pd.read_sql_query(query, conn, params=args)
    conn.close()
    return df


def get_result(query: str, *args):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute(query, args)
    result = cursor.fetchall()
    conn.close()
    return result
