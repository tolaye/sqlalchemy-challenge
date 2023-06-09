from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

app = Flask (__name__)

# connect to the database
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# home route
@app.route("/")
def home():
    return(
        f"<center><h2>Welcome to the Hawaii Climate Analysis Local API</h2></center>"
        f"<center><h3>Select from one of the following routes:</h3></center>"
        f"<center>/api/v1.0/precipitation</center>"
        f"<center>/api/v1.0/stations</center>"
        f"<center>/api/v1.0/tobs</center>"
        f"<center>/api/v1.0/start/end</center>"
        )

@app.route("/api/v1.0/precipitation")
def precip():
    #return as a json
    # Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the date and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previousYear).all()
    session.close()
    #dictionary with the date as the key and precipitation as the value
    precipitation = {date: prcp for date, prcp in results}
    # convert to json
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Perform a query to retrieve the stations
    results = session.query(Station.station).all()
    session.close()

    stationList = list(np.ravel(results))

    #convert to json
    return jsonify(stationList)

@app.route("/api/v1.0/tobs")
def temps():
    #return previous year temp
    # Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the temperature
    results = session.query(Measurement.tobs).\
            filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= previousYear).all()
    session.close()

    TempList = list(np.ravel(results))
    #convert to json
    return jsonify(TempList)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateState(start = None, end = None):
    # select statement
    selection = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    if not end:
        startDate = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*selection).filter(Measurement.date >= startDate).all()
        session.close()

        TempList = list(np.ravel(results))
        #convert to json
        return jsonify(TempList)
    else:
        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(end, "%m%d%Y")
        results = session.query(*selection)\
            .filter(Measurement.date >= startDate)\
            .filter(Measurement.date <= endDate).all()
        session.close()

        TempList = list(np.ravel(results))
        #convert to json
        return jsonify(TempList)

# app launcher
if __name__ == '__main__':
    app.run(debug=True)