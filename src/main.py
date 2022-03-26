from flask import Flask, render_template
from data import DataConnector
from utils import *

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
data = DataConnector()
data.init_db()


@app.route('/')
def index():
    return render_template("index.html", page_title="Home")


@app.route('/scores/totals')
def total_points():
    result = get_df("""
        SELECT drivers.driverId, drivers.forename, drivers.surname, drivers.code, SUM(results.points) as TotalPoints
        FROM drivers, results
        WHERE drivers.driverId = results.driverId
        GROUP BY drivers.driverId
        ORDER BY TotalPoints DESC
    """)
    return render_template("overview/total_points.html", page_title="Totale punten", drivers=result)


@app.route('/teams/stats/races')
def team_races_won():
    result = get_df("""
        SELECT constructors.name as TeamName, constructors.constructorRef, COUNT(raceId) as TotalWins
        FROM constructors, results
        WHERE constructors.constructorId = results.constructorId AND results.position = 1
        GROUP BY constructors.name
        ORDER BY TotalWins DESC
    """)
    return render_template("overview/team_races_won.html", page_title="Races gewonnen per team", teams=result)


@app.route('/drivers')
def drivers():
    result = get_df("SELECT * FROM drivers")
    return render_template("overview/drivers.html", page_title="Coureurs", drivers=result)


@app.route('/drivers/<driver_id>')
def driver(driver_id: int):
    num_races = get_result("SELECT COUNT(*) FROM results WHERE driverId = ?", driver_id)
    num_won = get_result("SELECT COUNT(*) FROM results WHERE driverId = ? AND position = 1", driver_id)
    num_top3 = get_result("SELECT COUNT(*) FROM results WHERE driverId = ? AND results.position is not null AND results.position <= 3", driver_id)
    driver_result = get_df("SELECT * FROM drivers WHERE driverId = ?", driver_id)
    results = get_df("""
        SELECT results.*, races.name as RaceName, races.year, constructors.name as TeamName
        FROM results, races, constructors
        WHERE driverId = ? AND results.raceId = races.raceId AND results.constructorId = constructors.constructorId
    """, driver_id)
    return render_template("driver.html", page_title="Coureur", driver=driver_result.iloc[0], num_races=num_races[0][0], num_won=num_won[0][0], num_top3=num_top3[0][0], results=results)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
