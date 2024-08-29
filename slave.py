# Script for Modbus TCP Slave Emulator
# Author: Kevin D. Martinez Zapata
# Date: 2024-08-05
# Version: 2.2

import asyncio
from pymodbus.server.async_io import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
import logging
import random
import struct

# Constants
N_REGS = 5000                   # Number of registers
IP_ADDRESS = 'localhost'        # IP address of the server
PORT = 1502                     # Port number of the server
SLEEP_TIME = 1                  # Sleep time in seconds

# Config de logging
logging.basicConfig()           # Configure logging
log = logging.getLogger()       # Get logger
log.setLevel(logging.DEBUG)     # Set log level to debug

# Initialize the data store with records 0 to 13 set to zero
store = {
    1: ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*N_REGS),  # Discrete Inputs (not used here)
        co=ModbusSequentialDataBlock(0, [0]*N_REGS),  # Coils (not used here)
        hr=ModbusSequentialDataBlock(0, [0]*N_REGS),  # Holding Registers
        ir=ModbusSequentialDataBlock(0, [0]*N_REGS)   # Input Registers (not used here)
    ),
}

# Create server context with slaves and datastore
context = ModbusServerContext(slaves=store, single=False)

# Optional: Initialize server identity
identity = ModbusDeviceIdentification()                         # Create identity object
identity.VendorName = 'Pymodbus'                                # Set vendor name
identity.ProductCode = 'PM'                                     # Set product code
identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'    # Set vendor URL
identity.ProductName = 'Pymodbus Server'                        # Set product name
identity.ModelName = 'Pymodbus Server'                          # Set model name
identity.MajorMinorRevision = '1.0'                             # Set major.minor.revision

def clear():
    import os
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

# Function for converting a floating value to two 16-bit registers
def float_to_registers(value):
    packed = struct.pack('<f', value)       # Pack floating value in 4 bytes in big-endian
    return struct.unpack('<HH', packed)     # Unpack 4 bytes in two 16-bit registers

# Asynchronous function for updating Modbus registers
async def update_registers():
    while True: # Infinite loop
        # Generate random values within specified ranges
        current_value = random.uniform(3, 4)                                # Current in Amperes
        frequency_value = random.uniform(59, 61)                            # Frequency in Hertz
        voltage_value = random.uniform(123, 126)                            # Voltage in Volts
        PF_value = random.uniform(0, 1)                                     # Power Factor
        aparent_power = current_value * voltage_value                       # Aparent Power in VA
        active_power = aparent_power * PF_value                             # Active Power in Watts
        reactive_power = (aparent_power**2 - active_power**2)**0.5          # Reactive Power in VAr

        # Convert floating values to 16-bit registers
        current_registers = float_to_registers(current_value)
        frequency_registers = float_to_registers(frequency_value)
        voltage_registers = float_to_registers(voltage_value)
        PF_registers = float_to_registers(PF_value)
        aparent_power_registers = float_to_registers(aparent_power)
        active_power_registers = float_to_registers(active_power)
        reactive_power_registers = float_to_registers(reactive_power)

        # Write values to the registers for each slave
        for i in range(1, 3):
            context[i].setValues(3, 2998, list(current_registers))
            context[i].setValues(3, 3108, list(frequency_registers))
            context[i].setValues(3, 3026, list(voltage_registers))
            context[i].setValues(3, 3082, list(PF_registers))
            context[i].setValues(3, 3074, list(aparent_power_registers))
            context[i].setValues(3, 3058, list(active_power_registers))
            context[i].setValues(3, 3066, list(reactive_power_registers))

        # Wait for 1 second
        await asyncio.sleep(SLEEP_TIME)

# Function for running the Modbus TCP server
async def run_server():
    update_task = asyncio.create_task(update_registers())   # Create task for updating registers
    await StartAsyncTcpServer(context,                      # Server context
                              identity,                     # Server identity
                              address=(                     # Server address
                                  IP_ADDRESS,               # IP address
                                  PORT                      # Port number
                                )
                            )
    await update_task                                       # Wait for update task to finish

# Main function
if __name__ == '__main__':
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        pass
    finally:
        clear()
        log.debug('Server stopped')
