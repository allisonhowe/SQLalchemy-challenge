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
        f"Available Routes in the Hawaii Weather API:<br/><br/>"
        f"Returns a list of precipitation data from the last year: /api/v1.0/precipitation<br/><br/>"
        f"Returns the list of Hawaii stations used in this dataset: /api/v1.0/stations<br/><br/>"
        f"Returns the daily temperature observations made by the most active station (station USC00519281): /api/v1.0/tobs<br/><br/>"
        f"Returns the minimum, average,and maximum temperature recorded for each day, beginning with the date entered (enter as yyyy-mm-dd): /api/v1.0/startdate<br/><br/>"
        f"Returns the minimum, average,and maximum temperature recorded for each day between the 2 dates entered (enter as yyyy-mm-dd): /api/v1.0/startdate/enddate")


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


@app.route("/api/v1.0/<start>")
def start_only(start):
    """ Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start
    range. Calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date."""
    session = Session(engine)
    start_date = dt.date.fromisoformat(start)
    start_temps = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).\
        group_by(measurement.date).all()
    session.close()
    temps = []
    for date, min_tobs, avg_tobs, max_tobs in start_temps:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["minimum_temp"] = min_tobs
        temp_dict["average_temp"] = avg_tobs
        temp_dict["maximum_temp"] = max_tobs
        temps.append(temp_dict)
    return jsonify(temps)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    """ Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start end
    range. Calculate `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive."""
    session = Session(engine)
    start_date = dt.date.fromisoformat(start)
    end_date = dt.date.fromisoformat(end)
    start_end_temps = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).\
        filter(measurement.date <= end_date).\
        group_by(measurement.date).all()
    session.close()
    temps = []
    for date, min_tobs, avg_tobs, max_tobs in start_end_temps:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["minimum_temp"] = min_tobs
        temp_dict["average_temp"] = avg_tobs
        temp_dict["maximum_temp"] = max_tobs
        temps.append(temp_dict)
    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)
