# IPC
## Topics
``<sensorTask>``
``<com2>/web``
``<com2/web``


## Json Sensor Frame
```javascript
{
"SensorValue1": [
{"name":"LIDAR","timestamp":"number","value":"number",},
{"name":"Humidity","timestamp":"number","value":"number"},
{"name":"SteeringAngle","timestamp":"number","value":"number"},
{"name":"Temperature","timestamp":"number","value":"number"},
{"name":"Speed","timestamp":"number","value":"number"},
{"name":"Altimeter","timestamp":"number","value":"number"}
],
"SensorValue3": [
{"name":"Acceleration","timestamp":"number","valueX":"number", "valueY":"number", "valueZ":"number"},
{"name":"Magnetometer","timestamp":"number","valueX":"number", "valueY":"number", "valueZ":"number"},
{"name":"Gyro","timestamp":"number","valueX":"number", "valueY":"number", "valueZ":"number"}
]
}
```

## Json Com2Car
```javascript
{
"timestamp":"number",
"login":"bool",
"certified":"bool",
"tokenID":"string",
"user":{	
	"userName":"string",
	"fullName":"string",
	"email":"string"
}
}
```

## Json Com2Web
```javascript
{
"timestamp":"number",
"tokenID":"string",
"login":"bool"
}
```

# Car Web Interface sequence diagram
![GitHub Logo](/images/WebCarInterface.png)
# Login Logout sequence diagram
![GitHub Logo](/images/loginlogout.png)
# Sensor publish sequence diagram
![GitHub Logo](/images/SensorLoop.png)
