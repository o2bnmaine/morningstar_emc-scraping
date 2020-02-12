#!/usr/bin/env python

import time
import decimal
from decimal import *

from pyModbusTCP.client import ModbusClient

#constants
scalar_root = decimal.Decimal(2)**decimal.Decimal(-15);
v_scale = decimal.Decimal(96.6667)*scalar_root;
i_scale = decimal.Decimal(139.15)*scalar_root;

# TCP auto connect on first modbus request
c = ModbusClient(host="192.168.86.60", port=502, auto_open=True)

# gather values of interest 
# read_holding_registers will return an array even if pulling just 1 value
batt_voltage_array = c.read_holding_registers(8, 1)
control_state_array = c.read_holding_registers(27, 1)
load_voltage_array = c.read_holding_registers(10, 1)
batt_temp_array = c.read_holding_registers(15, 1)
duty_cycle_array = c.read_holding_registers(28, 1)

getcontext().prec = 4
batt_voltage_num = batt_voltage_array[0]*decimal.Decimal(v_scale);
control_state_num = control_state_array[0];
load_voltage_num = load_voltage_array[0]*decimal.Decimal(i_scale);
batt_temp_num = batt_temp_array[0];
duty_cycle_num = duty_cycle_array[0]/255*100;

control_state_array= ["start","Night Check","Disconnect","Night","Fault","Bulk","Absorption","Float","Equalize"]
	
print("Battery Voltage: %s -- Control State: %s" %(batt_voltage_num,control_state_array[control_state_num]))

print("Load/Array Voltage: %s"%(load_voltage_num))
print("Battery Temperature: %s degrees"%(batt_temp_num))
print("PWM Duty Cycle: %s%%"%(duty_cycle_num))

