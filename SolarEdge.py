#!/usr/bin/env python3
"""
Modbus reader of SolarEdge Inverter
"""

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import struct
import time
import datetime

def print_scaled(name, value, scale_factor):
    print(name, round(value*10**scale_factor,3))

def run_binary_payload_ex():
    # ----------------------------------------------------------------------- #
    # We are going to use a simple client to send our requests
    # ----------------------------------------------------------------------- #
    client = ModbusClient('192.168.2.75', port=1502)
    client.connect()

    address = 40000
    count = 109
    result = client.read_holding_registers(address, count,  unit=1)
    client.close()

    print("-" * 60)

    buf = result.encode()

    sunSpec_ID = struct.unpack_from('4s',buf,(1-1)*2+1)[0].decode().strip('\0')
    print("sunSpec_ID=",sunSpec_ID)

    sunSpec_DID=struct.unpack_from('>H', buf, (3-1)*2+1)[0]
    print("sunSpec_DID=",sunSpec_DID)

    sunSpec_Length=struct.unpack_from('>H', buf, (4-1)*2+1)[0]
    print("sunSpec_Length=",sunSpec_Length)

    Manufacturer=struct.unpack_from('32s',buf,(5-1)*2+1)[0].decode().strip('\0')
    print("Manufacturer=",Manufacturer)

    Model=struct.unpack_from('32s',buf,(21-1)*2+1)[0].decode().strip('\0')
    print("Model=",Model)

    Version=struct.unpack_from('16s',buf,(45-1)*2+1)[0].decode().strip('\0')
    print("Version=",Version)

    SerialNumber=struct.unpack_from('32s',buf,(53-1)*2+1)[0].decode().strip('\0')
    print("SerialNumber=",SerialNumber)

    DeviceAddress=struct.unpack_from('>H', buf, (69-1)*2+1)[0]
    print("DeviceAddress=",DeviceAddress)

    sunSpec_DID=struct.unpack_from('>H', buf, (70-1)*2+1)[0]
    print("sunSpec_DID=",sunSpec_DID)

    sunSpec_Length=struct.unpack_from('>H', buf, (71-1)*2+1)[0]
    print("sunSpec_Length=",sunSpec_Length)

    print("\n")

    AC_Current_SF=struct.unpack_from('>h', buf, (76-1)*2+1)[0]
    print("AC_Current_SF=",AC_Current_SF)

    AC_Current=struct.unpack_from('>H', buf, (72-1)*2+1)[0]
    print_scaled("AC_Current=",AC_Current, AC_Current_SF)

    AC_CurrentA=struct.unpack_from('>H', buf, (73-1)*2+1)[0]
    print_scaled("AC_CurrentA=",AC_CurrentA, AC_Current_SF)

    AC_CurrentB=struct.unpack_from('>H', buf, (74-1)*2+1)[0]
    print_scaled("AC_CurrentB=",AC_CurrentB, AC_Current_SF)

    AC_CurrentC=struct.unpack_from('>H', buf, (75-1)*2+1)[0]
    print_scaled("AC_CurrentC=",AC_CurrentC, AC_Current_SF)

    print ("\n")

    AC_Voltage_SF=struct.unpack_from('>h', buf, (83-1)*2+1)[0]
    print("AC_Voltage_SF=",AC_Voltage_SF)

    AC_VoltageAB=struct.unpack_from('>H', buf, (77-1)*2+1)[0]
    print_scaled("AC_VoltageAB=",AC_VoltageAB,AC_Voltage_SF)

    AC_VoltageBC=struct.unpack_from('>H', buf, (78-1)*2+1)[0]
    print_scaled("AC_VoltageBC=",AC_VoltageBC,AC_Voltage_SF)

    AC_VoltageCA=struct.unpack_from('>H', buf, (79-1)*2+1)[0]
    print_scaled("AC_VoltageCA=",AC_VoltageCA,AC_Voltage_SF)

    AC_VoltageAN=struct.unpack_from('>H', buf, (80-1)*2+1)[0]
    print_scaled("AC_VoltageAN=",AC_VoltageAN,AC_Voltage_SF)

    AC_VoltageBN=struct.unpack_from('>H', buf, (81-1)*2+1)[0]
    print_scaled("AC_VoltageBN=",AC_VoltageBN,AC_Voltage_SF)

    AC_VoltageCN=struct.unpack_from('>H', buf, (82-1)*2+1)[0]
    print_scaled("AC_VoltageCN=",AC_VoltageCN,AC_Voltage_SF)

    print ("\n")

    AC_Power_SF=struct.unpack_from('>h', buf, (85-1)*2+1)[0]
    print("AC_Power_SF=",AC_Power_SF)


    AC_Power=struct.unpack_from('>h', buf, (84-1)*2+1)[0]
    power=AC_Power*10**AC_Power_SF
    print("AC_Power=",power)

    print ("\n")

    AC_Frequency=struct.unpack_from('>h', buf, (86-1)*2+1)[0]
    print("AC_Frequency",AC_Frequency)

    AC_Frequency_SF=struct.unpack_from('>h', buf, (87-1)*2+1)[0]
    print("AC_Frequency_SF=",AC_Frequency_SF)

    print ("\n")

    AC_Energy_WH=struct.unpack_from('>I', buf, (94-1)*2+1)[0]
    print("AC_Energy_WH=",AC_Energy_WH)

    AC_Energy_WH_SF=struct.unpack_from('>h', buf, (96-1)*2+1)[0]
    print("AC_Energy_WH_SF=",AC_Energy_WH_SF)

    print ("\n")

    DC_Current=struct.unpack_from('>H', buf, (97-1)*2+1)[0]
    print("DC_Current=",DC_Current)

    DC_Current_SF=struct.unpack_from('>h', buf, (98-1)*2+1)[0]
    print("DC_Current_SF=",DC_Current_SF)

    print ("\n")

    DC_Voltage=struct.unpack_from('>H', buf, (99-1)*2+1)[0]
    print("DC_Voltage=",DC_Voltage)

    DC_Voltage_SF=struct.unpack_from('>h', buf, (100-1)*2+1)[0]
    print("DC_Voltage_SF=",DC_Voltage_SF)

    print ("\n")

    DC_Power=struct.unpack_from('>H', buf, (101-1)*2+1)[0]
    print("DC_Power=",DC_Power)

    DC_Power_SF=struct.unpack_from('>h', buf, (102-1)*2+1)[0]
    print("DC_Power_SF=",DC_Power_SF)

    print ("\n")

    Temp=struct.unpack_from('>h', buf, (104-1)*2+1)[0]
    print("Temp=",Temp)

    Temp_SF=struct.unpack_from('>h', buf, (107-1)*2+1)[0]
    print("Temp_SF=",Temp_SF)

    print ("\n")

    Status=struct.unpack_from('>H', buf, (108-1)*2+1)[0]
    print("Status=",Status)

    Status_Vendor=struct.unpack_from('>H', buf, (109-1)*2+1)[0]
    print("Status_Vendor=",Status_Vendor)
 
    print("-" * 60)
    print("\n\n")

    return power


if __name__ == "__main__":
    reading=1
    powerMax=0.0
    while True:
        print("-"*60)
        print("Reading ",reading, " at ", datetime.datetime.now(), " prevMaxPower=", powerMax)
        try:
            currentPower=run_binary_payload_ex()
            if currentPower > powerMax:
                powerMax=currentPower
        except Exception as err:
            print("Caught exception ", err)
            print("-"*60)
        reading=reading+1
        time.sleep(30)


