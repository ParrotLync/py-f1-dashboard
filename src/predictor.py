from datetime import datetime

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from data import DataConnector


class Predictor:
    def __init__(self):
        self.data = DataConnector()
        df = pd.merge(self.data.results, self.data.races, on='raceId')
        df = pd.merge(df, self.data.drivers, on='driverId')
        df = pd.merge(df, self.data.driver_standings, on='driverId')
        df = pd.merge(df, self.data.constructors, on='constructorId')
        self.df = pd.merge(df, self.data.status, on='statusId')
        self.categorical = []
        self.numerical = []
        self.df_finished = None
        self.encoders = {}
        self.x = None
        self.y = None
        self.model = None

    def init(self):
        self.clean_columns()
        self.convert_types()
        self.split_cat_num()
        self.filter()
        self.remove_outliers()
        self.encode_labels()
        self.setup_model()

    def clean_columns(self):
        self.df['driverName'] = self.df['forename'] + ' ' + self.df['surname']

        self.df = self.df.drop(['url', 'url_x', 'position_x', 'fastestLapTime', 'positionText_x', 'time_x', 'time_y',
                                'driverRef','constructorRef', 'nationality_y', 'url_y', 'positionText_y', 'raceId_y',
                                'points_y', '?', '?.1','?.2', '?.3', '?.4', '?.5', '?.6', '?.7', '?.8', '?.9',
                                'forename', 'surname'], axis=1)

        new_names = {
            'number_x': 'number',
            'name_x': 'grandPrix',
            'number_y': 'driverNumber',
            'code': 'driverCode',
            'nationality_x': 'nationality',
            'name_y': 'company',
            'raceId_x': 'raceId',
            'points_x': 'points',
            'position_y': 'position'
        }

        self.df.rename(columns=new_names, inplace=True)

    def convert_types(self):
        pd.to_datetime(self.df.date)
        self.df['dob'] = pd.to_datetime(self.df['dob'])
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['age'] = round((datetime.today() - self.df['dob']).dt.days / 365)

        nums = ['number', 'milliseconds', 'fastestLap', 'rank', 'fastestLapSpeed', 'driverNumber']
        for i in nums:
            self.df[i] = pd.to_numeric(self.df[i], errors='coerce')
        self.df.drop('driverNumber', axis=1, inplace=True)

    def split_cat_num(self):
        for i in self.df.columns:
            if self.df[i].dtypes == 'object':
                self.categorical.append(i)
            else:
                self.numerical.append(i)

    def filter(self):
        self.df_finished = self.df[self.df['status'] == 'Finished']
        mean = self.df.fastestLapSpeed.mean()
        self.df = self.df_finished[self.df_finished['fastestLapSpeed'] > mean]
        self.df = self.df[(self.df['age'] < self.df['age'].mean()) & (self.df['year'] > 2012)]
        self.df.drop(['date', 'dob', 'statusId'], axis=1, inplace=True)
        self.numerical.remove('date')
        self.numerical.remove('dob')
        self.numerical.remove('statusId')

    def remove_outliers(self):
        q1 = self.df.quantile(0.25)
        q3 = self.df.quantile(0.75)
        iqr = q3 - q1
        self.df = self.df[~((self.df < (q1 - 1.5 * iqr)) | (self.df > (q3 + 1.5 * iqr))).any(axis=1)]

    def encode_labels(self):
        for i in self.categorical:
            encoder = LabelEncoder()
            self.df[i] = encoder.fit_transform(self.df[i])
            self.encoders[i] = encoder

    def setup_model(self):
        self.x = self.df.drop('driverName', axis=1)
        self.y = self.df.driverName
        self.model = RandomForestClassifier()
        self.x = self.x[["year", "circuitId", "grandPrix", "position"]]
        self.model.fit(self.x, self.y)

    def predict(self, year, circuit_id, grand_prix):
        try:
            pred = self.model.predict([[year, circuit_id, self.encoders['grandPrix'].transform([grand_prix]), 1]])
            return self.encoders['driverName'].inverse_transform(pred)
        except:
            return "No prediction available. Please try a different value."


