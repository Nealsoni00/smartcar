#!/usr/bin/env python
# encoding: utf-8
from flask import Flask
from flask import request

import requests
import json


# This is the network manager to send post requests to the GM servers and 
# get the return values as JSON data. This method is used by every function
#Inputs: 
# - route: the endpoint of the GM API to send the data to
# - id: The integer ID of the vehicle to perform the request on
# - command: a string that you pass to START or STOP the car. Only applicable
#            if you are starting or stoping the car engine. 
#Output: 
# - Raw JSON data from the request 
baseURL = "http://gmapi.azurewebsites.net"
def performRequest(route, id, command = -1):
	
	headers = {'Content-Type': 'application/json'}
	data = {'id': str(id), 'responseType': 'JSON'}
	if command != -1:
		data['command'] = command
	
	dataJson = json.dumps(data)
	r = requests.post(baseURL + route, data=dataJson, headers=headers)
	json_data = json.loads(r.text)
	return json_data

#This get the info (such as color, drivetrain, vin, and door count) of the car
#Inputs:
# - id: The integer ID of the vehicle to perform the request on
#Output: 
# - Smart Car formated JSON Info data. 
def info(id):
	json_data = performRequest("/getVehicleInfoService", id)
	if (json_data["status"] == "200"):
		data = json_data["data"] 
		# print(json_data["data"])
		info = {}
		info["color"]      = data["color"]["value"] if data["color"]["type"]           == "String" else "Error: Color data type mismatch"
		info["driveTrain"] = data["driveTrain"]["value"] if data["driveTrain"]["type"] == "String" else "Error: Drivetrain data type mismatch"
		info["vin"]  	   = data["vin"]["value"] if data["vin"]["type"]               == "String" else "Error: Vin data type mismatch"
		
		isFourDoorSedan = (True if data["fourDoorSedan"]["value"] == "True" else False) if data["fourDoorSedan"]["type"] == "Boolean" else "Error: four door data type mismatch" 
		isTwoDoorCoupe  = (True if data["twoDoorCoupe"]["value"] == "True" else False)  if data["twoDoorCoupe"]["type"]  == "Boolean" else "Error: two door data type mismatch" 
		info["doorCount"] = 4 if isFourDoorSedan else 2 if isTwoDoorCoupe else 0 #are there more options????
		
		return info
	else:
		return "Error: " + json_data["status"]

#This get the information about the doors of the car
#Inputs:
# - id: The integer ID of the vehicle to perform the request on
#Output: 
# - Smart Car formated JSON Door data. 
def doors(id):
	json_data = performRequest("/getSecurityStatusService", id)
	if (json_data["status"] == "200"):
		data = json_data["data"]["doors"]
		if data["type"] != "Array":
			return "Error: Data Type mismatch"
		security = []
		for door in data["values"]:
			temp = {}
			temp["location"] = door["location"]["value"]
			temp["locked"] = door["locked"]["value"]
			security.append(temp)
		return security
	else:
		return "Error: " + json_data["status"]

#This get the information about the energy information of the car
#Inputs:
# - id (Int): The ID of the vehicle to perform the request on
# - fuel (Boolean): true if you are performing a fuel request, false if battery request. 
#Output: 
# - Smart Car formated JSON energy data. 
def energy(id, fuel):
	json_data = performRequest("/getEnergyService", id)
	if (json_data["status"] == "200"):
		data = json_data["data"]
		energy = {}
		if fuel:
			energy["percent"] = data["tankLevel"]["value"]    if data["tankLevel"]["type"]    != "Null" else "Error: " + str(id) + " does not support fuel"
		else:
			energy["percent"] = data["batteryLevel"]["value"] if data["batteryLevel"]["type"] != "Null" else "Error: " + str(id) + " does not support battery"
		return energy;
	else:
		return "Error: " + json_data["status"]
#Wraper for energy request with fuel endpoint
def fuel(id):
	return energy(id, True)
#Wraper for energy request with battery endpoint
def battery(id):
	return energy(id, False)

#This get the information about the energy information of the car
#Inputs:
# - id (Int): The ID of the vehicle to perform the request on
# - start (String): either "START" or "STOP" for the car to start or stop the engine
#Output: 
# - Smart Car formated JSON engine data. 
def engine(id, start):
	engineResponse = performRequest("/actionEngineService", id, command=("START_VEHICLE" if start == "START" else "STOP_VEHICLE"))
	if (engineResponse["status"] == "200"): 
		status = {}
		status["status"] = "success" if engineResponse["actionResult"]["status"] == "EXECUTED" else "error"
		return status
	else:
		return "Error: " + engineResponse["status"]


#The flask server
app = Flask(__name__)

#The get routes performing their respective requests and returning the json data as a string
@app.route("/vehicles/<id>", methods=['GET'])
def vehicleRequest(id):
    return json.dumps(info(id))


@app.route("/vehicles/<id>/doors", methods=['GET'])
def doorsRequest(id):
    return json.dumps(doors(id))


@app.route("/vehicles/<id>/fuel", methods=['GET'])
def fuelRequest(id):
    return json.dumps(fuel(id))


@app.route("/vehicles/<id>/battery", methods=['GET'])
def batteryRequest(id):
    return json.dumps(battery(id))


#The post route for engine performing the post request to GM then returning the response JSON 
@app.route("/vehicles/<id>/engine", methods=['POST'])
def engineRequest(id):
	if request.method == 'POST':
		info = json.loads(request.data)["action"]
		return json.dumps(engine(id, info))

if __name__ == '__main__':
    app.run(debug=True)
    
#Initial Test Code:
# print info(1234)
# print info(1235)

# print doors(1234)
# print doors(1235)

# print fuel(1234)
# print fuel(1235)

# print battery(1234)
# print battery(1235)

# print engine(1234, "START")
# print engine(1235, "START")
# print engine(1234, "STOP")
# print engine(1235, "STOP")


