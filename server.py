#!/usr/bin/env python
# encoding: utf-8
from flask import Flask
from flask import request

import requests
import json

def performRequest(route, id, command = -1):
	baseURL = "http://gmapi.azurewebsites.net"
	headers = {'Content-Type': 'application/json'}
	data = {'id': str(id), 'responseType': 'JSON'}
	if command != -1:
		data = {'id': str(id), 'responseType': 'JSON', 'command': command}
	
	dataJson = json.dumps(data)
	r = requests.post(baseURL + route, data=dataJson, headers=headers)
	json_data = json.loads(r.text)
	return json_data


def info(id):
	json_data = performRequest("/getVehicleInfoService", id)
	data = json_data["data"] 
	if (json_data["status"] == "200"):
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

def fuel(id):
	return energy(id, True)

def battery(id):
	return energy(id, False)


def engine(id, start):
	engineResponse = performRequest("/actionEngineService", id, command=("START_VEHICLE" if start == "START" else "STOP_VEHICLE"))
	if (engineResponse["status"] == "200"): 
		status = {}
		status["status"] = "success" if engineResponse["actionResult"]["status"] == "EXECUTED" else "error"
		return status
	else:
		return "Error: " + engineResponse["status"]

app = Flask(__name__)

@app.route("/vehicles/<id>")
def vehicleRequest(id):
    return json.dumps(info(id))


@app.route("/vehicles/<id>/doors")
def doorsRequest(id):
    return json.dumps(doors(id))


@app.route("/vehicles/<id>/fuel")
def fuelRequest(id):
    return json.dumps(fuel(id))


@app.route("/vehicles/<id>/battery")
def batteryRequest(id):
    return json.dumps(battery(id))


@app.route("/vehicles/<id>/engine", methods=['POST'])
def engineRequest(id):
	if request.method == 'POST':
		info = json.loads(request.data)["action"]
		return json.dumps(engine(id, info))

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


