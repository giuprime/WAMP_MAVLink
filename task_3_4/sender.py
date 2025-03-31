import asyncio
from autobahn.asyncio.component import Component, run

# Configurazione WAMP
REALM = "realm1"
ROUTER_URL = "ws://localhost:8181/ws"

component = Component(
    transports=ROUTER_URL,
    realm=REALM,
)

@component.on_join
async def on_join(session, details):
    print("connected to WAMP! Test of the RPC\n")

    # Test della procedura 'drone.arm'
    print("arming drone")
    result = await session.call("drone.arm")
    print(f"Result: {result}\n")

    # Attendere 10 secondi prima di procedere
    await asyncio.sleep(10)

    # Test della procedura 'drone.takeoff'
    print("Takeoff")
    result = await session.call("drone.takeoff")
    print(f"result: {result}\n")

    # Attendere 60 secondi in volo prima di atterrare
    await asyncio.sleep(60)

    # Test della procedura 'drone.land'
    print("landing")
    result = await session.call("drone.land")
    print(f"result: {result}\n")

    # Attendere qualche secondo per garantire l'atterraggio
    await asyncio.sleep(5)

    # Test della procedura 'drone.disarm'
    print("disarming drone...")
    result = await session.call("drone.disarm")
    print(f"result: {result}\n")

    print("Finish")
    await session.leave()

if __name__ == "__main__":
    run(component)
