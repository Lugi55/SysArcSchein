# sensor task parameter
measurementPeriodLogin = 0.5
measurementPeriodLogout = 5

# communication task parameter
sensorBufferSize = 100
loginBufferSize = 10

# rfid parameter
RFIDTimeout = 2

# gui parameter
value_format = '{:10.4f}'
timestamp_format = '{:16.6f}'
loginStatusPeriod = 0.2

# mqtt parameter
local_sensor_topic      = 'local/sensor'
local_com2_car_topic    = 'local/com2/car'
local_com2_web_topic    = 'local/com2/web'
local_RFID_topic        = 'local/RFID'
local_subscription      = 'local/#'

extern_sensor_topic     = '/SysArch/V3/sensor'
extern_com2_car_topic   = '/SysArch/V3/com2/car'
extern_com2_web_topic   = '/SysArch/V3/com2/web'
extern_subscription     = '/SysArch/V3/#'

extern_host             = '192.168.200.165'
extern_port             = 8883
extern_user             = 'V3'
extern_password         = 'DE5' 
