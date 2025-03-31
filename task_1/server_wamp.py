import asyncio
from autobahn.asyncio.component import Component, run
from pymavlink import mavutil

# Configurazione WAMP
REALM = "realm1"
ROUTER_URL = "ws://localhost:8181/ws"

component = Component(
    transports=ROUTER_URL,
    realm=REALM,
)

# Connessione al drone (variabile globale per usarla in handle_command)
master = mavutil.mavlink_connection("udp:localhost:14550")

@component.on_join
async def on_join(session, details):
    print("Connected to WAMP!")

    print("Waiting the first message  HEARTBEAT...")
    master.wait_heartbeat()
    print("Drone connected!")

    async def handle_command(command):
        print(f"Received command: {command}")

        if command == "arm":
            print("Arming")
            master.arducopter_arm()
            master.motors_armed_wait()
            print("Drone armed!")
        elif command.startswith("takeoff:"):
            try:
                altitude = float(command.split(":")[1])  # Estrae l'altitudine dal comando
                print(f"Takeoff")

                # Invia il comando di decollo con l'altitudine specificata
                master.mav.command_long_send(
                    master.target_system, master.target_component,
                    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                    0, 0, 0, 0, 0, 0, 0, altitude
                )
                print("Send takeoff")
            except ValueError:
                print("Error: not valid height!")

        elif command == "land":
            print("land")
            master.mav.command_long_send(
                master.target_system, master.target_component,
                mavutil.mavlink.MAV_CMD_NAV_LAND,
                0, 0, 0, 0, 0, 0, 0, 0
            )
            print("land sent")

        elif command == "disarm":
            print("Disarming")
            master.arducopter_disarm()
            await asyncio.sleep(1) 
            print("Drone disarmed")

        else:
            print("Error: bad command")

    # Sottoscrizione ai comandi WAMP
    await session.subscribe(handle_command, "mavlink.command")
    print("subscribed to WAMP topic: 'mavlink.command'")

# Avvia il nodo centrale WAMP
if __name__ == "__main__":
    run(component)
