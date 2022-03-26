import sqlite3
import pandas as pd


def load(name, **kwargs):
    return pd.read_csv(f'data/{name}', na_values=r'\N', **kwargs)


class DataConnector:
    def __init__(self):
        self.circuits = load('circuits.csv', index_col=0)
        self.constructor_results = load('constructor_results.csv', index_col=0)
        self.constructors = load('constructors.csv', index_col=0)
        self.drivers = load('drivers.csv', index_col=0)
        self.driver_standings = load('driver_standings.csv', index_col=0)
        self.lap_times = load('lap_times.csv')
        self.pit_stops = load('pit_stops.csv')
        self.qualifying = load('qualifying.csv', index_col=0)
        self.races = load('races.csv', index_col=0)
        self.results = load('results.csv', index_col=0)
        self.seasons = load('seasons.csv', index_col=0)
        self.sprint_results = load('sprint_results.csv', index_col=0)
        self.status = load('status.csv', index_col=0)

    def init_db(self):
        conn = sqlite3.connect('data.db')
        self.circuits.to_sql("circuits", conn, if_exists='replace')
        self.constructor_results.to_sql("constructor_results", conn, if_exists='replace')
        self.constructors.to_sql("constructors", conn, if_exists='replace')
        self.drivers.to_sql("drivers", conn, if_exists='replace')
        self.driver_standings.to_sql("driver_standings", conn, if_exists='replace')
        self.lap_times.to_sql("lap_times", conn, if_exists='replace')
        self.pit_stops.to_sql("pit_stops", conn, if_exists='replace')
        self.qualifying.to_sql("qualifying", conn, if_exists='replace')
        self.races.to_sql("races", conn, if_exists='replace')
        self.results.to_sql("results", conn, if_exists='replace')
        self.seasons.to_sql("seasons", conn, if_exists='replace')
        self.sprint_results.to_sql("sprint_results", conn, if_exists='replace')
        self.status.to_sql("status", conn, if_exists='replace')
        conn.close()
