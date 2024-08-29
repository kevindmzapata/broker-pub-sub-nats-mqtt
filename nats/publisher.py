import asyncio
from pymodbus.client.tcp import ModbusTcpClient
from nats.aio.client import Client as NATS

# Modbus TCP server parameters
modbus_server = 'localhost'
port = 1502

# NATS parameters
nats_server = 'nats://localhost:4222'
nats_subject = 'openfmb.metermodule.MeterReadingProfile.modbus'

async def read_modbus_data(client, nc):
    while True:
        response = client.read_holding_registers(2998, 2, slave=1)

        if response.isError():
            print(f'Error: {response.message}')
        else:
            data = ', '.join(map(str, response.registers))

            # Publish the data to the NATS server
            await nc.publish(nats_subject, data.encode())
        
        # Wait for 1 second
        await asyncio.sleep(1)

async def run():
    # Create a new Modbus TCP client
    client = ModbusTcpClient(modbus_server, port)

    if not client.connect():
        print('Error: unable to connect to the Modbus TCP server')
        return
    else:
        print('Connected to the Modbus TCP server')

    # Create a new NATS client
    nc = NATS()

    # Connect to the NATS server
    await nc.connect(nats_server)

    if not nc.is_connected:
        print("Error: unable to connect to the NATS server")
        return
    else:
        print("Connected to the NATS server")

    try:
        await read_modbus_data(client, nc)
    except KeyboardInterrupt:
        print('Exiting...')
    finally:
        client.close()
        await nc.close()

if __name__ == "__main__":
    asyncio.run(run())
