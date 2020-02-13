#!/usr/bin/env python

import os 
import time
import decimal
from decimal import *
import os.path
import requests

from pyModbusTCP.client import ModbusClient

# set file namem for output
filename = "/home/pi/automation/solar/emc.data.txt"

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

# arrays
control_state_array= ["Start","Night Check","Disconnect","Night","Fault","Bulk","Absorption","Float","Equalize","Unknown"]
alarm_fault_array= ["","Overcurrent","FET short","Software","HVD","TriStar hot","DIP sw changed","Setting edit","reset?","Miswire","RTS shorted","RTS disconnected","12","13","14","15","No Faults"]
alarm_alert_array= ["","RTS shorted","RTS disconnected","Ths disconnected","TriStar hot","Current limit","Current offset","Battery Sense","Batt Sense disc","Uncalibrated","RTS miswire","HVD","high d","miswire","FET open","P12*","Load Disc.*","19","20","21","22","23","24","No Alerts"]
# alert(0) & fault(0) are blanked as I couldn't figure out how to retrieve a no-fault state
# fault(0) is actually "external short"
# alert(0) is actually "RTS open"

# TCP auto connect on first modbus request
c = ModbusClient(host="{ipaddr_or_hostname}", port=502, auto_open=True)

# gather values of interest 
# read_holding_registers will return an array even if pulling just 1 value
batt_voltage_reg = c.read_holding_registers(8, 1)
control_state_reg = c.read_holding_registers(27, 1)
load_voltage_reg = c.read_holding_registers(10, 1)
batt_temp_reg = c.read_holding_registers(15, 1)
duty_cycle_reg = c.read_holding_registers(28, 1)
solar_current_reg = c.read_holding_registers(11, 1)
load_current_reg = c.read_holding_registers(12, 1)
alarm_alert_reg = c.read_holding_registers(23, 1)
alarm_fault_reg = c.read_holding_registers(24, 1)

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


#print ("alert: %s ... fault: %s" %(alarm_alert_reg[0],alarm_fault_reg[0]))


# add a header if the file doesn't exist at the moment
# this will create a new file
if not os.path.isfile(filename):
	#print("date_time,battery voltage,load voltage,battery temp,duty cycle,control state,alarm,fault\r\n")
	file_object = open(filename, 'w+')
	file_object.write("date,time,load voltage,battery voltage,battery temp,duty cycle,control state,alarm,fault\r\n")
	file_object.close()


# open file (append to end)
file_object = open(filename, 'a')
#print("%s,%s,%s,%s,%s,%s,%s,%s\r" %(date_time,load_voltage_num,batt_voltage_num,batt_temp_num,duty_cycle_num,control_state_array[control_state_num],alarm_alert_array[alarm_alert_num],alarm_fault_array[alarm_fault_num]))
file_object.write("%s,%s,%s,%s,%s,%s,%s,%s\r\n" %(date_time,load_voltage_num,batt_voltage_num,batt_temp_num,duty_cycle_num,control_state_array[control_state_num],alarm_alert_array[alarm_alert_num],alarm_fault_array[alarm_fault_num]))
file_object.close()


# send voltage level to isy994 (can only store integers, so multiply by 100)
url = 'http://{uid}:{pwd}@{ipadd_or_hostname}/rest/vars/set/2/{var_num}/%s' %(batt_voltage_num*100)
r = requests.get(url)


# sleep for 60 seconds
time.sleep(60)


# start the next instance of the program to log the data from the next minute
execfile('/home/pi/automation/solar/scrape.emc.py')
