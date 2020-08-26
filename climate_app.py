import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes in the Hawaii Weather API:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>")


@app.route("/api/v1.0/precipitation")
def precip():
    """Convert precipitation query results to dictionary & return as JSON representation."""
    session = Session(engine)
    lastdate = session.query(measurement.date).order_by(measurement.date.desc()).first().date
    year_ago = dt.date.fromisoformat(lastdate) - dt.timedelta(days=365)
    sel = [measurement.date, measurement.prcp]
    last12 = session.query(*sel).filter(measurement.date > year_ago).order_by(measurement.date).all()
    session.close()
    prec_dict = dict(last12)
    return jsonify(prec_dict)


@app.route("/api/v1.0/stations")
def all_stations():
    """Return a JSON list of stations from the dataset"""
    session = Session(engine)
    all_stations = session.query(measurement.station).group_by(measurement.station).all()
    session.close()
    all_stations_list = list(np.ravel(all_stations))
    return jsonify(all_stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most active station for the last year of data, then return a
        JSON list of that station's TOBS for the previous year."""
    session = Session(engine)
    lastdate = session.query(measurement.date).order_by(measurement.date.desc()).first().date
    year_ago = dt.date.fromisoformat(lastdate) - dt.timedelta(days=365)
    active_station = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).all()
    last12_temp = session.query(measurement.date, measurement.station, measurement.tobs).\
        filter(measurement.station == active_station[0][0]).\
        filter(measurement.date > year_ago).\
        order_by(measurement.date).all()
    session.close()
    temps = []
    for date, station, tobs in last12_temp:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["station"] = station
        temp_dict["tobs"] = tobs
        temps.append(temp_dict)
    return jsonify(temps)


# @app.route("/api/v1.0/<start>")



if __name__ == '__main__':
    app.run(debug=True)
