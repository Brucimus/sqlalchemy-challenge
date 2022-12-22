import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

def temp_dict_calc(temp_agg):
    temp_dict = {}
    temp_dict["min_temp"] = temp_agg[0][0]
    temp_dict["max_temp"] = temp_agg[0][1]
    temp_dict["avg_temp"] = temp_agg[0][2]
    return temp_dict

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    most_recent = session.query(Measurement).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.datetime.strptime(most_recent.date, '%Y-%m-%d') - dt.timedelta(days=365)
    previous_year_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>one_year_ago).all()
    print(previous_year_prcp)
    session.close()
    
    all_precipitation = []
    for date, prcp in previous_year_prcp:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        all_precipitation.append(precipitation_dict)
    
    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query all stations
    all_stations = session.query(Station.station).all()
    all_stations_list = list(np.ravel(all_stations))
    session.close()
    
    return jsonify(all_stations_list)

@app.route("/api/v1.0/tobs")
def temperature():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dictionary of dates and precipitation"""
    # Query dates and precipitation
    most_recent = session.query(Measurement).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.datetime.strptime(most_recent.date, '%Y-%m-%d') - dt.timedelta(days=365)

    station_activity = engine.execute('select station, count(*) from measurement group by station order by count(*) desc').fetchall()
    most_active_station =station_activity[0][0]

    most_active_station_list = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>one_year_ago).filter(Measurement.station == most_active_station).all()

    most_active_station_temp_list = []
    for date, prcp in most_active_station_list:
        temp_dict = {}
        temp_dict[date] = prcp
        most_active_station_temp_list.append(temp_dict)
    
    return jsonify(most_active_station_temp_list)

@app.route("/api/v1.0/<start>")
def date_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    temp_agg = session.execute(f'select min(tobs) as min_temp, max(tobs) as max_temp, avg(tobs) as avg_temp from measurement where date > "{start}"').fetchall()

    return jsonify(temp_dict_calc(temp_agg))

@app.route("/api/v1.0/<start>/<end>")
def date_start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    temp_agg = session.execute(f'select min(tobs) as min_temp, max(tobs) as max_temp, avg(tobs) as avg_temp from measurement where date > "{start}" and date <= "{end}"').fetchall()
    
    return jsonify(temp_dict_calc(temp_agg))   

if __name__ == '__main__':
    app.run(debug=True)
