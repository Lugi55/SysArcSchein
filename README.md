# Topics
## global
``<V3>/sensor``
``<V3>/com2/web``
``<V3>/com2/car``
## local
``<local>/sensor``
``<local>/com2/car``
``<local>/com2/web``

# Json Frames
## Json Sensor Frame
```json
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

## Json Com2Car Frame
```json
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

## Json Com2Web Frame
```json
{
"timestamp":"number",
"tokenID":"string",
"login":"bool"
}
```

# Sensor data status
status|LIDAR|Humidity|SteeringAngle|Temperature|Speed|Altimeter|Acceleration|Magnetometer|Gyro|Measurement Period|
|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|----:|
|login|x|x|x|x|x|x|x|x|x|0.1s|
|logout||||x|||x||x|1s|

# Car Web Interface sequence diagram
![GitHub Logo](/images/WebCarInterface.png)
# Login Logout sequence diagram
![GitHub Logo](/images/loginlogout.png)
# Sensor publish sequence diagram
![GitHub Logo](/images/SensorLoop.png)
