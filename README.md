## global topics
``<V3>/sensor``
``<V3>/com2/web``
``<V3>/com2/car``
## local topics
``<local>/sensor``
``<local>/com2/car``
``<local>/com2/web``

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

## Json com2car Frame
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

## Json com2web Frame
```json
{
"timestamp":"number",
"tokenID":"string",
"login":"bool"
}
```

## Sensor data status
status|LIDAR|Humidity|SteeringAngle|Temperature|Speed|Altimeter|Acceleration|Magnetometer|Gyro|Measurement Period|
|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|----:|
|login|x|x|x|x|x|x|x|x|x|0.1s|
|logout||||x|||x||x|1s|

## Car Web Interface sequence diagram
![GitHub Logo](/images/WebCarInterface.png)
## Login Logout sequence diagram
![GitHub Logo](/images/loginlogout.png)
## Sensor publish sequence diagram
![GitHub Logo](/images/SensorLoop.png)

## SensorTask
## GUITask
## LoggerTask
## CommunicationTask
## RFIDTask
## TestTask
## constants 
## start.bat

## Python requirements
## Mqtt requrements
## IMU requrements

## Installation

## division of labor
||SensorTask|GUITask|LoggerTask|CommunicationTask|RFIDTask|TestTask|ReadTask|start.bat|sum
|:---------:|:-----:|:--------:|:---------------:|:------:|:------:|:------:|:-------:|:---:|:---:|
|Luginsland|10h||5h||2h||2h|1h|40h
|Casagranda||5h||10h||2h|3h|1h|40h
