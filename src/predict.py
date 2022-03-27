import pandas as pd

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import SGDClassifier


from sklearn.preprocessing import RobustScaler, StandardScaler, MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn import tree

from src.data import DataConnector
from datetime import datetime


# Load data
from src.utils import get_df

data = DataConnector()


# Merge dataframes into one
df = pd.merge(data.results, data.races, on='raceId')
df = pd.merge(df, data.drivers, on='driverId')
df = pd.merge(df, data.driver_standings, on='driverId')
df = pd.merge(df, data.constructors, on='constructorId')
df = pd.merge(df, data.status, on='statusId')


# Perform clean-up on columns
df['driverName'] = df['forename'] + ' ' + df['surname']

df = df.drop(['url', 'url_x', 'position_x', 'fastestLapTime', 'positionText_x', 'time_x', 'time_y', 'driverRef',
              'constructorRef', 'nationality_y', 'url_y', 'positionText_y', 'raceId_y', 'points_y', '?', '?.1',
              '?.2', '?.3', '?.4', '?.5', '?.6', '?.7', '?.8', '?.9', 'forename', 'surname'], axis=1)

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

df.rename(columns=new_names, inplace=True)


# Convert data types
pd.to_datetime(df.date)
df['dob'] = pd.to_datetime(df['dob'])
df['date'] = pd.to_datetime(df['date'])
df['age'] = round((datetime.today() - df['dob']).dt.days / 365)

nums = ['number', 'milliseconds', 'fastestLap', 'rank', 'fastestLapSpeed', 'driverNumber']
for i in nums:
    df[i] = pd.to_numeric(df[i], errors='coerce')
df.drop('driverNumber', axis=1, inplace=True)


# Categorical and numerical values
categorical = []
numerical = []
for i in df.columns:
    if df[i].dtypes == 'object':
        categorical.append(i)
    else:
        numerical.append(i)


# Data filtration
df_finished = df[df['status'] == 'Finished']
mean = df.fastestLapSpeed.mean()
mean2 = df.fastestLap.mean()

df = df_finished[df_finished['fastestLapSpeed'] > mean]
df = df[(df['age'] < df['age'].mean()) & (df['year'] > 2012)]
df.drop(['date', 'dob', 'statusId'], axis=1, inplace=True)
numerical.remove('date')
numerical.remove('dob')
numerical.remove('statusId')


# Outlier removal
Q1 = df.quantile(0.25)
Q3 = df.quantile(0.75)
IQR = Q3 - Q1
df = df[~((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]


# Label encoding
encoders = {}
encoder = LabelEncoder()
for i in categorical:
    encoder = LabelEncoder()
    encoders[i] = encoder
    df[i] = encoder.fit_transform(df[i])
    print(list(encoder.classes_))

x = df.drop('driverName', axis=1)
y = df.driverName


# Modelling
lr = LogisticRegression(solver='sag')
dt = DecisionTreeClassifier()
rn = RandomForestClassifier()
knn = KNeighborsClassifier()
gb = GaussianNB()
sgd = SGDClassifier()

# scaler = RobustScaler().fit(x[["year", "circuitId", "grandPrix", "position"]])
# x_scaled = scaler.transform(x[["year", "circuitId", "grandPrix", "position"]])

x = x[["year", "circuitId", "grandPrix", "position"]]
# scaler = StandardScaler()
# scaler.fit(x)
# x = scaler.transform(x)

selected_model = rn

selected_model.fit(x, y)

prediction_df = pd.DataFrame()
data_df = get_df("""
SELECT races.year, races.circuitId, races.name, drivers.forename, drivers.surname
FROM drivers, results, races
WHERE results.driverId = drivers.driverId AND results.raceId = races.raceId AND races.year >= 2012 AND results.position = 1
""")
for i, row in data_df.iterrows():
    try:
        print([[row['year'], row['circuitId'], encoders['grandPrix'].transform([row['name']]), 1]])
        pred = selected_model.predict(
            [[row['year'], row['circuitId'], encoders['grandPrix'].transform([row['name']]), 1]])
    except:
        continue

    try:
        pred_name = encoders['driverName'].inverse_transform(pred)
    except:
        pred_name = "-"

    df_row = pd.DataFrame({
        'year': row['year'],
        'circuitId': row['circuitId'],
        'grandPrix': row['name'],
        'prediction_val': pred,
        'prediction': pred_name,
        'real': row['forename'] + ' ' + row['surname']
    })

    prediction_df = pd.concat([prediction_df, df_row], ignore_index=True, axis=0)

prediction_df.to_csv('predictions.csv')


# models = [lr, sgd, knn, gb, rn, dt]
# scores = {}
# for i in models:
#     i.fit(x_train_scaled, y_train)
#     y_prediction = i.predict(x_test_scaled)
#     print(f"Prediction: {y_prediction} | Test: {y_test}")
#     print(encoder.inverse_transform([y_prediction[0]]))
#     print(f"{i}: {accuracy_score(y_prediction, y_test) * 100}")
#     scores.update({str(i): i.score(x_test_scaled, y_test) * 100})
