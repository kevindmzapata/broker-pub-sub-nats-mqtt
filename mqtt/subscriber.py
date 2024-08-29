import asyncio
import paho.mqtt.client as mqtt

broker_address = "localhost"
broker_port = 1883
topic = 'openfmb/metermodule/MeterReadingProfile/#'

cont = 0

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(topic)
    else:
        print(f"Falied to connect, return code {rc}")

def on_message(client, userdata, msg):
    global cont
    print(f"[{cont}] Received message: {msg.topic}: {msg.payload.decode()}")
    cont += 1

async def run():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Conectar al broker MQTT
    client.connect(broker_address, broker_port, 60)

    # Mantener el loop del cliente
    client.loop_forever()

if __name__ == "__main__":
    asyncio.run(run())