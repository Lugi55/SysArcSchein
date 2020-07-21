# SysArc

## Overview
![GitHub Logo](/images/UML.png)

## Tasks
|          |SensorTask|GUITask|LoggerTask|CommunicationTask|RFIDTask|
|:--------:|:--------:|:-----:|:--------:|:---------------:|:------:|
|language  |Python3   |Python3|Python3   |Python3          |Python2 |
|nicenes   |-10       |0      |10        |-10              |0       |
|crucial   |x         |       |          |x                |        |

### SensorTask
![GitHub Logo](/images/SensorTask_1.png)
![GitHub Logo](/images/SensorTask_2.png)
![GitHub Logo](/images/SensorTask_3.png)

status|LIDAR|Humidity|SteeringAngle|Temperature|Speed|Altimeter|Acceleration|Magnetometer|Gyro|Measurement Period|
|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|----:|
|login|x|x|x|x|x|x|x|x|x|0.1s|
|logout||||x|||x||x|1s|

### GUITask
### LoggerTask
![GitHub Logo](/images/LoggerTask.png)
### CommunicationTask
### RFIDTask
![GitHub Logo](/images/RFIDTask.png)
### constants 

## Communication
### global topics
``<V3>/sensor``
``<V3>/com2/web``
``<V3>/com2/car``
### local topics
``<local>/sensor``
``<local>/com2/car``
``<local>/com2/web``
``<local>/RFID``

### Json Sensor Frame
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

### Json com2car Frame
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
### Json com2web Frame
```json
{
"timestamp":"number",
"tokenID":"string",
"login":"bool"
}
```

## Car Web Interface sequence diagram
![GitHub Logo](/images/WebCarInterface.png)
## Login Logout sequence diagram
![GitHub Logo](/images/loginlogout.png)
## Sensor publish sequence diagram
![GitHub Logo](/images/SensorLoop.png)



## Python requirements
## Mqtt requrements
## IMU requrements

## Installation

## division of labor
||SensorTask|GUITask|LoggerTask|CommunicationTask|RFIDTask|TestTask|RFIDTest|start.bat|sum
|:---------:|:-----:|:--------:|:---------------:|:------:|:------:|:------:|:-------:|:---:|:---:|
|Luginsland|10h||5h||2h||2h|1h|35h
|Casagranda||15h||20h||6h|1h|1h|42h
