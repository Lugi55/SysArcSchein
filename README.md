# SysArc

## Overview
![GitHub Logo](/images/UML.png)

## <a name="Tasks"></a> Tasks
|          |SensorTask|GUITask|LoggerTask|CommunicationTask|RFIDTask|
|:--------:|:--------:|:-----:|:--------:|:---------------:|:------:|
|language  |Python3   |Python3|Python3   |Python3          |Python2 |
|niceness   |-10       |0      |10        |-10              |0       |
|critical  |x         |       |          |x                |        |

Nicenes is a value to determinite the priority of python tasks. 
A negative value means a task with high priority.
Positive value are tasks lower priority.
Critical Task have to run and sould not be determied.
All other Task can be started any time and also determied.

## SensorTask
All sensor related Tasks are handeled here.
The main duty of the Task is to get muliple sensorvalues and build a json file with them.
There are two states in witch the Task can bee.
If no user is logged in to the system than only a few of the sensors will be avaluated. 
Also the frequency in witch the values are measured is decreased.
The reasoning behind that is that a parking car the most sensor values arent that interesting.
the folloing diagramm shows the main loop for publishing sensor datata to the local mqtt.
<br /><br />
<img src="/images/SensorTask_1.png" alt="drawing" width="300"/>
<br /><br />
There must be posibility for an user to login to a car.
The **RFIDTask** can publish an UserID witch the **SensorTask** subscribe to.
For validation of the UserId we have to ask the web databank.
There fore a request is been puflished after reciving an UserID.
The following diagramm shows callback function for an incoming mqtt message from the **RFIDTask**.
<br /><br />
<img src="/images/SensorTask_2.png" alt="drawing" width="200"/>
<br /><br />
The **SensorTask** subscribe to the topic ``<local>com2/car`` with is used to get response from the web.
The message can be triggerd by a request from the RFID UserID or a login via web.
The incoming Message contains information about the user, validation and if its an login or logout message.
The following diagramm shows the callback function triggerd by the topic ``<local>com2/car``
<br /><br />
<img src="/images/SensorTask_3.png" alt="drawing" width="200"/>
<br /><br />
The folloing table shows witch sensor value is puplished and the update rate when a user is logged in or not.
status|LIDAR|Humidity|SteeringAngle|Temperature|Speed|Altimeter|Acceleration|Magnetometer|Gyro|Measurement Period|
|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|----:|
|login|x|x|x|x|x|x|x|x|x|0.1s|
|logout||||x|||x||x|1s|

## GUITask

## LoggerTask
The Sensor values generated from the **SensorTask** are logged in this Task.
All json strings emmited by the **SensorTask** are dumped in to an file.
Every full hour a new file will be generated in the LoggerData directory.
The name of the file hints the time at witch the file has been created.
If the number of files is getting bigger than a maximal Value the last file is removed.
The maximal Number of files can be alterd by changing the variable ``maxFileNumber`` in **constants.py**. 
The LoggerTask subscibe to the topic <local>sensor and get periodicly a json file with sensor values.
The Task is only running in the callback function generated by an incoming mqtt message.
The following diagram shows the funktion of the callback function.
<br /><br />
<img src="/images/LoggerTask.png" alt="drawing" width="300"/>
<br /><br />
The sensor cheks if a new file must be created.
A new File must be created if the hour has incremented.
Every time a new file is beeing created we have to check the total amout of file.


## CommunicationTask


## RFIDTask
For login or logout via RFID this task is used. The **RFIDTask** implements an libary to read and RFID tag.
If a tag is detected a mqtt message is published to the topic ``<local>RFID``.
the following diagram shows the procedure.
<br /><br />
<img src="/images/RFIDTask.png" alt="drawing" width="300"/>
<br /><br />
To prevent mulible signal a timeout with each succefull detection is added. 

## constants
The python module ``constants.py`` is used to store values witch are used in mulitple tasks.
For example the updaterates of the **SensorTask** can be altered by changing variables here.

## IPC
For the local IPC mqtt is used.
#### local topics
``<local>/sensor``
``<local>/com2/car``
``<local>/com2/web``
``<local>/RFID``
The communication to the web also uses mqtt.
The global topics and local topics are almost the same.
Also messages trasmited over these topics are equal.
For infos about message types and payload refer to [Communication with web](#Communication with web)
The following sequence diagrams show the lokal IPC.
The first diagramm shows the sensorpublish procedure.
<br /><br />
<img src="/images/SensorLoop.png" alt="drawing" width="600"/>
<br /><br />
This diagramm shows the login logout procedure within the lokal domain.
<br /><br />
<img src="/images/loginlogout.png" alt="drawing" width="600"/>
<br /><br />



## <a name="Communication with web"></a> Communication with web
For Communication between web and car mqqt is used.
All messages that are transmitted to the must be bufferd. 
There fore an own Task is used. 
The **CommunicationTask** is responsible for the connection between local and global and buffering the output.
Over the global topics standardized json frames are transmited.


#### global topics
``<V3>/sensor``
``<V3>/com2/web``
``<V3>/com2/car``



### Json Sensor Frame
With this frame sensor values are transmited.
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
With this Frame the communication to the car from the web is handeld.
It is needed for the login procedure. 
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
With this frame the communication to the web from the car is handeld.
Main use is for tranmitting a tockenID for the login.
```json
{
"timestamp":"number",
"tokenID":"string",
"login":"bool"
}
```

## Car Web Interface sequence diagram
The following swquence diagramm shows the communication between web and car.
<img src="/images/WebCarInterface.png" alt="drawing" width="500"/>

## Python requirements
folowing modules are needed.

## Mqtt requirements
paho is needed 
<br />
link to guide

## IMU requirements
In the directory ``/IMU`` the libary for the sensor can be found.
I2C is needed for the communication.
<br />
link to guide

## RFID requirements
the python file ``balbal`` implements the funktion for the RFID 
SPI is needed for the communication.
<br />
link to guide

## Guide
To execude a task use ``python3 <TaskName>`` or ``python2 <TaskName>``.
<br /><br />
For task with a negative niceness value ``sudo`` is needed.
<br /><br />
All critcal Task have to run to ensure functionality.
All non critical Task can be started and determied at any time.
For infos go to [Tasks](#Tasks)

## division of labor
|           |SensorTask|GUITask|LoggerTask|CommunicationTask|RFIDTask|TestTask|TestRFID|Doku |Präsentation|WebCar Interface|sum|
|:---------:|:--------:|:-----:|:--------:|:---------------:|:------:|:------:|:------:|:---:|:----------:|:--------------:|:---:|
|Luginsland |10h        |2h     |5h        |                 |3h      |        |3h      |6h   |3h          |4h              |50h
|Casagranda |          |18h    |          |15h              |4h       |2h      |      |1h   |3h          |4h              |54h
