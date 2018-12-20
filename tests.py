#!/usr/bin/env python
# encoding: utf-8
import requests
import json
import sys

def performRequest(route, id, data = -1):
	baseURL = "http://127.0.0.1:5000/vehicles/"
	headers = {'Content-Type': 'application/json'}
	json_data = {}
	if data == -1: #if -1, we want to do a get without data being sent
		r = requests.get(baseURL + str(id) + route, headers=headers)
		json_data = json.loads(r.text)
	else: #if not -1 then we want to do a post with data
		dataJson = json.dumps(data)
		r = requests.post(baseURL + str(id) + route, data=dataJson, headers=headers)
		json_data = json.loads(r.text)
		
	return json_data


if __name__ == '__main__':
    #pass in the username of the account you want to download
	cars = []
	if len(sys.argv) == 1:
		cars = [1234, 1235]
	else:
		for i in range(1, len(sys.argv)):
			cars.append(sys.argv[i])

	for car in cars:
		print "_______ Car ID:" + str(car) + " _______";
		print "Info: "    + json.dumps( performRequest("", car)) 
		print "Doors: "   + json.dumps( performRequest("/doors", car))
		print "Fuel: "    + json.dumps( performRequest("/fuel", car))
		print "Battery: " + json.dumps( performRequest("/battery", car))
		data = {'action': 'START'}
		print "Car On: "  + json.dumps( performRequest("/engine", car, data))
		data = {'action': 'STOP'}
		print "Car Off: " + json.dumps(performRequest("/engine", car, data))
		
    



	


# "curl http://127.0.0.1:5000/vehicles/1235/engine -X POST -H 'Content-Type: application/json' -d '{'action': 'START'}'"
# curl http://127.0.0.1:5000/vehicles/1235/engine -X POST -H 'Content-Type: application/json' -d '{"action": "STOP"}'
# curl http://127.0.0.1:5000/vehicles/1234/engine -X POST -H 'Content-Type: application/json' -d '{"action": "START"}'
# curl http://127.0.0.1:5000/vehicles/1234/engine -X POST -H 'Content-Type: application/json' -d '{"action": "STOP"}'

