#!/usr/bin/env python

import os 
import time
import decimal
from decimal import *
import os.path
import requests
import mysql.connector

from pyModbusTCP.client import ModbusClient

# set date time
cur_time = time.localtime()
date_time = time.strftime("%Y%m%d,%H:%M", cur_time)

#print("Date, Time: %s" %(date_time))


# constants
scalar_root = decimal.Decimal(2)**decimal.Decimal(-15);
v_scale = decimal.Decimal(96.6667)*scalar_root;
i_scale = decimal.Decimal(139.15)*scalar_root;
c_scale = decimal.Decimal(66.6667)*scalar_root;
l_scale = decimal.Decimal(316.6667)*scalar_root;


# TCP auto connect on first modbus request
c = ModbusClient(host="192.x.x.x", port=xxx, auto_open=True)

# gather values of interest 
# read_holding_registers will return an array even if pulling just 1 value
batt_voltage_reg   = c.read_holding_registers(8, 1)
control_state_reg  = c.read_holding_registers(27, 1)
load_voltage_reg   = c.read_holding_registers(10, 1)
batt_temp_reg      = c.read_holding_registers(15, 1)
duty_cycle_reg     = c.read_holding_registers(28, 1)
solar_current_reg  = c.read_holding_registers(11, 1)
load_current_reg   = c.read_holding_registers(12, 1)
alarm_alert_reg    = c.read_holding_registers(23, 1)
alarm_fault_reg    = c.read_holding_registers(24, 1)

# set precision to 4, includes digits on both sides of decimal
getcontext().prec = 4

# convert with scalar
# remove array
# load voltage is a placeholder for when I determine the correct value to track/calculate
if batt_voltage_reg:
	batt_voltage_num =  batt_voltage_reg[0]*decimal.Decimal(v_scale);

if control_state_reg:
	control_state_num = control_state_reg[0];

if load_voltage_reg:
	load_voltage_num =  load_voltage_reg[0]*decimal.Decimal(i_scale);

if batt_temp_reg:
	batt_temp_num =     batt_temp_reg[0];

if duty_cycle_reg:
	duty_cycle_num =    decimal.Decimal((duty_cycle_reg[0]*100)/255);

if solar_current_reg:
	solar_current_num = solar_current_reg[0]*decimal.Decimal(c_scale);

if load_current_reg:
	load_current_num =  load_current_reg[0]*decimal.Decimal(l_scale);

if alarm_alert_reg:
	alarm_alert_num =   alarm_alert_reg[0];

if alarm_fault_reg:
	alarm_fault_num =   alarm_fault_reg[0];

# api key is a publicly available dev key
url = 'https://swd.weatherflow.com/swd/rest/observations/station/1234?api_key=20c70eae-e62f-4d3b-b3a4-8586e90f3ac8'
web_output = requests.get(url)
web_output.content

# split using commas separation
web_output_array = web_output.content.split(',')

# grab 66, 67, 68 from array and split by colon
solar_radiation_array=web_output_array[66].split(":")
uv_index_array=web_output_array[67].split(":")
brightness_array=web_output_array[68].split(":")

# grab 2nd value in resulting arrays
solar_radiation_num=solar_radiation_array[1]
uv_index_num=uv_index_array[1]
brightness_num=brightness_array[1]


# connect to database on server
cnx = mysql.connector.connect(
  user='user', 
  password='password', 
  host='192.x.x.x', 
  port='xxxx', 
  database='solar')

cursor = cnx.cursor()

# data_time will be set via the SQL DDL
insert = ("INSERT INTO log (uv_index,brightness,solar_radiation,voltage,temperature,duty_cycle,control_state,alarm,fault) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
data = (uv_index_num,brightness_num,solar_radiation_num,batt_voltage_num,batt_temp_num,duty_cycle_num,control_state_num,alarm_alert_num,alarm_fault_num)

cursor.execute(insert,data)
cnx.commit()

cursor.close()
cnx.close()


# send voltage level to isy994
# isy994 has logic to check if there are problems based on the following variables
# if 'night' starts 15 minutes after sunrise and 15 minutes before sunset 
# there is probably a problem with the circuit breakers
url = 'http://admin:watahataho@192.x.x.x/rest/vars/set/2/24/%s' %(batt_voltage_num*100)
r = requests.get(url)

url = 'http://admin:watahataho@192.x.x.x/rest/vars/set/2/26/%s' %(control_state_num)
r = requests.get(url)

url = 'http://admin:watahataho@192.x.x.x/rest/vars/set/2/27/%s' %(time.strftime("%H%M", cur_time))
r = requests.get(url)
