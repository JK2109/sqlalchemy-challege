import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import pandas as pd
import datetime as dt

from flask import Flask, jsonify

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
# reflect the tables

Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station_table = Base.classes.station


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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"Please insert (start date) in YYYY-MM-DD format<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
        f"Please insert (start date) and (end date) in YYYY-MM-DD format<end>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
     # Convert query results to a dictionary using date as the key and prcp as the value
     # Return the JSON representation of your dictionary
     
    query_data = session.query(measurement.date, measurement.prcp).order_by(measurement.date.asc()).all()
    session.close()
    
    data=[]
    for date, prcp in query_data:
        data_dict ={}
        data_dict["Date"] = date
        data_dict["Prcp"] = prcp
        data.append(data_dict)

    return jsonify(data)


@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset
    session = Session(engine)
      
    query_data = session.query(station_table.station, station_table.name).all()
    
    session.close()

    station_data=[]
    for station, name in query_data:
        data_dict ={}
        data_dict["Station"] = station
        data_dict["Name"] = name
        station_data.append(data_dict)

    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations of the most active station for the last year of data.
    # Return a JSON list of temperature observations (TOBS) for the previous year
    
    session = Session(engine)
    station_active= session.query(measurement.station, func.count(measurement.id)).\
                group_by(measurement.station).\
                order_by(func.count(measurement.date).desc()).first()
    
    # query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    query_date = "2016-08-23"
    
    
    # Perform a query to retrieve the data and precipitation scores
    data = session.query(measurement.date, measurement.tobs).\
            filter(measurement.station==station_active[0]).\
            filter(measurement.date >= query_date).\
            order_by(measurement.date.asc()).all()
    session.close()

    active_station_data=[]
    for date, tobs in data:
        data_dict ={}
        data_dict["Date"] = date
        data_dict["Temperature"] = tobs
        active_station_data.append(data_dict)
    
    return jsonify(active_station_data)
    
@app.route("/api/v1.0/<start>")
def start(start):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
    session = Session(engine)
      
    temp_data= session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
                filter(measurement.date >= start).\
                order_by(measurement.date.asc()).all()
    
    session.close()

    temp_start=[]
    for tmin, tmax, tavg in temp_data:
        data_dict ={}
        data_dict["TMIN"] = tmin
        data_dict["TMAX"] = tmax
        data_dict["TAVG"] = tavg
        temp_start.append(data_dict)

    return jsonify(temp_start)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
    session = Session(engine)
      
    temp_data= session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
                filter(measurement.date >= start).\
                filter(measurement.date <= end).\
                order_by(measurement.date.asc()).all()
    
    session.close()

    temp_startend=[]
    for tmin, tmax, tavg in temp_data:
        data_dict ={}
        data_dict["TMIN"] = tmin
        data_dict["TMAX"] = tmax
        data_dict["TAVG"] = tavg
        temp_startend.append(data_dict)

        if start <= end:
            return jsonify(temp_startend)
    #creating error when illogical date range is being used
    return jsonify({"error":"Illogical Date Range."}), 404

if __name__ == "__main__":
    app.run(debug=True)
