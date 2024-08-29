import asyncio
from nats.aio.client import Client as NATS

# NATS parameters
nats_server = 'nats://localhost:4222'
nats_subject = 'openfmb.metermodule.MeterReadingProfile.*'

cont = 1

async def run():

    # Create an instance of the NATS client
    nc = NATS()

    # Connect to the NATS server
    await nc.connect(nats_server)

    # Define the message handler function for the subscription
    async def message_handler(msg):
        global cont
        print(f'[{cont}] Received a message: {msg.data.decode()}')
        cont += 1

    # Subscribe to the NATS subject
    await nc.subscribe(nats_subject, cb=message_handler)

    # Wait for the subscription to finish
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(run())
