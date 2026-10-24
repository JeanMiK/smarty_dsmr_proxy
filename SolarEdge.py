#!/usr/bin/env python3
"""
Modbus reader of SolarEdge Inverter
"""

#from pyModbusTCP.client import ModbusClient
from pymodbus.client import ModbusTcpClient as ModbusClient 


import struct
import time
import threading
import datetime
from datetime import date

import paho.mqtt.client as mqtt


class MqttRetained:
    topics = ["SolarEdge/PowerMax","SolarEdge/PowerMaxCurrentDay","SolarEdge/EnergyAtStartOfDay","SolarEdge/CurrentDate"]
    def __init__(self, mqttClient):
        self.currentDate=''
        self.powerMax=0.0
        self.powerMaxCurrentDay=0.0
        self.energyAtStartOfDay=None
        self.lock=threading.Lock()
        self.allowUpdate=False
        self.mqttClient=mqttClient
        self.received=[False, False, False, False]
        self.newDay=False
        self.reading=0

    def tryInitFromBroker(self):
        def on_message(client, userdata, msg):
            userdata.lock.acquire()
            if userdata.allowUpdate == True:
               if msg.topic == MqttRetained.topics[0]:
                  userdata.powerMax=float(msg.payload)
                  userdata.received[0]=True
               elif msg.topic == MqttRetained.topics[1]:
                  userdata.powerMaxCurrentDay=float(msg.payload)
                  userdata.received[1]=True
               elif msg.topic == MqttRetained.topics[2]:
                  userdata.energyAtStartOfDay=float(msg.payload)
                  userdata.received[2]=True
               elif msg.topic == MqttRetained.topics[3]:
                  userdata.currentDate=msg.payload
                  userdata.received[3]=True
            else:
               print("Message received for topic ", msg.topic, " after initialization phase")
            userdata.lock.release()
        self.allowUpdate=True
        self.mqttClient.on_message=on_message
        self.mqttClient.subscribe([(x,0) for x in MqttRetained.topics])
        time.sleep(5)
        self.lock.acquire()
        self.allowUpdate=False
        self.mqttClient.unsubscribe(MqttRetained.topics)
        self.lock.release()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    if  userdata == None:
        pass
    elif userdata.allowUpdate == True:
        client.subscribe([(x,0) for x in MqttRetained.topics])

client = mqtt.Client()
client.on_connect = on_connect

retained = MqttRetained(client)
client.user_data_set(retained)

client.connect("localhost", 1883, 60)

client.loop_start()

retained.tryInitFromBroker()


def print_scaled(name, value, scale_factor):
    scaled_value=round(value*10**scale_factor,3)
    print(name, scaled_value, sep='')
    return scaled_value


def read_and_publish_SolarEdge(retained):
    # ----------------------------------------------------------------------- #
    # We are going to use a simple client to send our requests
    # ----------------------------------------------------------------------- #
    client = ModbusClient(host='192.168.2.45', port=1502) # could use symbolic name SolarEdge.local
    client.connect()

    address = 40000
    count = 109
    # result = client.read_holding_registers(address, count,  unit=1)
    result = client.read_holding_registers(address=40000, count=109)
    client.close()

    print("-" * 60)
    retained.reading = retained.reading+1
    print("Reading",retained.reading, "at", datetime.datetime.now())

    buf = result.encode()

    sunSpec_ID = struct.unpack_from('4s',buf,(1-1)*2+1)[0].decode().strip('\0')
    print("sunSpec_ID=",sunSpec_ID, sep='')

    sunSpec_DID=struct.unpack_from('>H', buf, (3-1)*2+1)[0]
    print("sunSpec_DID=",sunSpec_DID, sep='')

    sunSpec_Length=struct.unpack_from('>H', buf, (4-1)*2+1)[0]
    print("sunSpec_Length=",sunSpec_Length, sep='')

    Manufacturer=struct.unpack_from('32s',buf,(5-1)*2+1)[0].decode().strip('\0')
    print("Manufacturer=",Manufacturer, sep='')

    Model=struct.unpack_from('32s',buf,(21-1)*2+1)[0].decode().strip('\0')
    print("Model=",Model, sep='')

    Version=struct.unpack_from('16s',buf,(45-1)*2+1)[0].decode().strip('\0')
    print("Version=",Version, sep='')

    SerialNumber=struct.unpack_from('32s',buf,(53-1)*2+1)[0].decode().strip('\0')
    print("SerialNumber=",SerialNumber, sep='')

    DeviceAddress=struct.unpack_from('>H', buf, (69-1)*2+1)[0]
    print("DeviceAddress=",DeviceAddress, sep='')

    sunSpec_DID=struct.unpack_from('>H', buf, (70-1)*2+1)[0]
    print("sunSpec_DID=",sunSpec_DID, sep='')

    sunSpec_Length=struct.unpack_from('>H', buf, (71-1)*2+1)[0]
    print("sunSpec_Length=",sunSpec_Length, sep='')

    print("\n")

    AC_Current_SF=struct.unpack_from('>h', buf, (76-1)*2+1)[0]
    print("AC_Current_SF=",AC_Current_SF, sep='')

    AC_Current=struct.unpack_from('>H', buf, (72-1)*2+1)[0]
    scaled=print_scaled("AC_Current=",AC_Current, AC_Current_SF)
    retained.mqttClient.publish("SolarEdge/AC_Current", scaled)

    AC_CurrentA=struct.unpack_from('>H', buf, (73-1)*2+1)[0]
    scaled=print_scaled("AC_CurrentA=",AC_CurrentA, AC_Current_SF)
    retained.mqttClient.publish("SolarEdge/AC_CurrentA", scaled)


    AC_CurrentB=struct.unpack_from('>H', buf, (74-1)*2+1)[0]
    scaled=print_scaled("AC_CurrentB=",AC_CurrentB, AC_Current_SF)
    retained.mqttClient.publish("SolarEdge/AC_CurrentB", scaled)

    AC_CurrentC=struct.unpack_from('>H', buf, (75-1)*2+1)[0]
    scaled=print_scaled("AC_CurrentC=",AC_CurrentC, AC_Current_SF)
    retained.mqttClient.publish("SolarEdge/AC_CurrentC", scaled)

    print ("\n")

    AC_Voltage_SF=struct.unpack_from('>h', buf, (83-1)*2+1)[0]
    print("AC_Voltage_SF=",AC_Voltage_SF, sep='')

    AC_VoltageAB=struct.unpack_from('>H', buf, (77-1)*2+1)[0]
    scaled=print_scaled("AC_VoltageAB=",AC_VoltageAB,AC_Voltage_SF)
    retained.mqttClient.publish("SolarEdge/AC_VoltageAB", scaled)

    AC_VoltageBC=struct.unpack_from('>H', buf, (78-1)*2+1)[0]
    scaled=print_scaled("AC_VoltageBC=",AC_VoltageBC,AC_Voltage_SF)
    retained.mqttClient.publish("SolarEdge/AC_VoltageBC", scaled)

    AC_VoltageCA=struct.unpack_from('>H', buf, (79-1)*2+1)[0]
    scaled=print_scaled("AC_VoltageCA=",AC_VoltageCA,AC_Voltage_SF)
    retained.mqttClient.publish("SolarEdge/AC_VoltageCA", scaled)

    AC_VoltageAN=struct.unpack_from('>H', buf, (80-1)*2+1)[0]
    scaled=print_scaled("AC_VoltageAN=",AC_VoltageAN,AC_Voltage_SF)
    retained.mqttClient.publish("SolarEdge/AC_VoltageAN", scaled)

    AC_VoltageBN=struct.unpack_from('>H', buf, (81-1)*2+1)[0]
    scaled=print_scaled("AC_VoltageBN=",AC_VoltageBN,AC_Voltage_SF)
    retained.mqttClient.publish("SolarEdge/AC_VoltageBN", scaled)

    AC_VoltageCN=struct.unpack_from('>H', buf, (82-1)*2+1)[0]
    scaled=print_scaled("AC_VoltageCN=",AC_VoltageCN,AC_Voltage_SF)
    retained.mqttClient.publish("SolarEdge/AC_VoltageCN", scaled)

    print ("\n")

    AC_Power_SF=struct.unpack_from('>h', buf, (85-1)*2+1)[0]
    print("AC_Power_SF=",AC_Power_SF, sep='')


    AC_Power=struct.unpack_from('>h', buf, (84-1)*2+1)[0]
    power=round(float(AC_Power)*10**AC_Power_SF,3)
    print("AC_Power=",power, sep='')
    retained.mqttClient.publish("SolarEdge/AC_Power", power)


    if retained.newDay or power>retained.powerMaxCurrentDay:
        retained.powerMaxCurrentDay=power
        retained.mqttClient.publish("SolarEdge/PowerMaxCurrentDay", power, retain=True)

    if power>retained.powerMax:
        retained.powerMax=power
        retained.mqttClient.publish("SolarEdge/PowerMax", power, retain=True)



    print ("\n")

    AC_Frequency=struct.unpack_from('>h', buf, (86-1)*2+1)[0]
    print("AC_Frequency=",AC_Frequency, sep='')

    AC_Frequency_SF=struct.unpack_from('>h', buf, (87-1)*2+1)[0]
    print("AC_Frequency_SF=",AC_Frequency_SF, sep='')

    print ("\n")

    AC_Energy_WH_SF=struct.unpack_from('>h', buf, (96-1)*2+1)[0]
    print("AC_Energy_WH_SF=",AC_Energy_WH_SF, sep='')

    AC_Energy_WH=struct.unpack_from('>I', buf, (94-1)*2+1)[0]
    scaled=print_scaled("AC_Energy_WH=",AC_Energy_WH, AC_Energy_WH_SF)
    retained.mqttClient.publish("SolarEdge/EnergyTotal", scaled)

    if retained.newDay:
        retained.energyAtStartOfDay=scaled
        retained.mqttClient.publish("SolarEdge/EnergyAtStartOfDay", scaled, retain=True)

    energyCurrentDay=scaled-retained.energyAtStartOfDay
    print("EnergyCurrentDay=", energyCurrentDay)
    retained.mqttClient.publish("SolarEdge/EnergyCurrentDay", energyCurrentDay)


    print ("\n")

    DC_Current=struct.unpack_from('>H', buf, (97-1)*2+1)[0]
    print("DC_Current=",DC_Current, sep='')

    DC_Current_SF=struct.unpack_from('>h', buf, (98-1)*2+1)[0]
    print("DC_Current_SF=",DC_Current_SF, sep='')

    print ("\n")

    DC_Voltage=struct.unpack_from('>H', buf, (99-1)*2+1)[0]
    print("DC_Voltage=",DC_Voltage, sep='')

    DC_Voltage_SF=struct.unpack_from('>h', buf, (100-1)*2+1)[0]
    print("DC_Voltage_SF=",DC_Voltage_SF, sep='')

    print ("\n")

    DC_Power=struct.unpack_from('>H', buf, (101-1)*2+1)[0]
    print("DC_Power=",DC_Power, sep='')

    DC_Power_SF=struct.unpack_from('>h', buf, (102-1)*2+1)[0]
    print("DC_Power_SF=",DC_Power_SF, sep='')

    print ("\n")

    Temp=struct.unpack_from('>h', buf, (104-1)*2+1)[0]
    print("Temp=",Temp, sep='')

    Temp_SF=struct.unpack_from('>h', buf, (107-1)*2+1)[0]
    print("Temp_SF=",Temp_SF, sep='')

    print ("\n")

    Status=struct.unpack_from('>H', buf, (108-1)*2+1)[0]
    print("Status=",Status, sep='')

    Status_Vendor=struct.unpack_from('>H', buf, (109-1)*2+1)[0]
    print("Status_Vendor=",Status_Vendor, sep='')

    print("-" * 60)
    print("\n\n")


    if retained.newDay:
        retained.mqttClient.publish("SolarEdge/CurrentDate", retained.currentDate, retain=True)
        retained.newDay=False

    return power


while True:
    now=date.today().strftime('%Y-%m-%d')
    if retained.currentDate != now:
        print("-"*60)
        print("Observed a change of day from '", retained.currentDate, "' to '",now,"'", sep='')
        retained.currentDate = now
        retained.newDay=True;

    print("-"*60)
    try:
        read_and_publish_SolarEdge(retained)
    except Exception as err:
            print("Caught exception", err)
            print("-"*60)

    print("New powerMaxCurrentDay:", retained.powerMaxCurrentDay)
    print("New powerMax:", retained.powerMax)
    time.sleep(30)

