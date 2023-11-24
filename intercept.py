import asyncio
from alsa_midi import AsyncSequencerClient, WRITE_PORT, READ_PORT, EventType, Address


async def send_note_events(client: AsyncSequencerClient, queue):
    korg_port = client.create_port('output', READ_PORT)
    korg_address = Address('24:0')
    korg_port.connect_to(korg_address)

    while True:
        event = await queue.get()

        event.channel = 2
        event.dest = korg_address

        await client.event_output(event)
        await client.drain_output()


async def get_note_events(client: AsyncSequencerClient, queue):
    impulse_port = client.create_port('input', WRITE_PORT)
    impulse_address = Address('28:0')
    impulse_port.connect_from(impulse_address)

    while True:
        event = await client.event_input()

        if event.type in (EventType.NOTEON, EventType.NOTEOFF):
            await queue.put(event)


client = AsyncSequencerClient('giga')
loop = asyncio.get_event_loop()

queue = asyncio.Queue()

loop.run_until_complete(asyncio.gather(get_note_events(client, queue),
                                       send_note_events(client, queue)))


