import asyncio
from pymodbus.client.tcp import ModbusTcpClient
import paho.mqtt.client as mqtt

# Modbus TCP server parameters
modbus_server = 'localhost'
port = 1502

# Configuración del cliente MQTT
broker_address = "localhost"
broker_port = 1883
topic = 'openfmb/metermodule/MeterReadingProfile/modbus'

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)

async def read_modbus_data(client, mqtt_client):
    while True:
        response = client.read_holding_registers(2998, 2, slave=1)

        if response.isError():
            print(f'Error: {response.message}')
        else:
            data = ', '.join(map(str, response.registers))

            # Publish the data to the MQTT broker
            mqtt_client.publish(topic, data)
        
        # Wait for 1 second
        await asyncio.sleep(1)

async def run():
    client = ModbusTcpClient(modbus_server, port)
    
    if not client.connect():
        print('Error: unable to connect to the Modbus TCP server')
        return
    else:
        print('Connected to the Modbus TCP server')

    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(broker_address, broker_port)
    mqtt_client.loop_start()

    try:
        await read_modbus_data(client, mqtt_client)
    except KeyboardInterrupt:
        print('Exiting...')
    finally:
        client.close()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    asyncio.run(run())
