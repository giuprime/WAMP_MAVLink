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

# Connessione al drone
master = mavutil.mavlink_connection("udp:localhost:14550")

# Variabile di stato per l'armamento
is_armed = False

# Funzione per armare il drone
def arm_drone():
    global is_armed  
    print("arming")
    master.arducopter_arm()
    master.motors_armed_wait()
    is_armed = True
    print("Drone armed")

# Funzione per il takeoff
def takeoff_drone(altitude=10):  
    print(f"takeoff")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 0, 0, 0, 0, 0, 0, altitude
    )
    print("takeoff sent")

# Funzione per il riarmamento
#def arm_again():
 #   global is_armed  # Dichiara la variabile come globale
 #   print("Ri-armamed...")
 #   master.arducopter_arm()
 #   master.motors_armed_wait()
 #   is_armed = True
 #   print("Drone ri-armato!")

# Funzione per l'atterraggio
def land_drone():
    print("land")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    print("land sent")

# Gestione dei comandi ricevuti
@component.on_join
async def on_join(session, details):
    print("connected to WAMP!")
    print("Waiting the first message HEARTBEAT...")
    master.wait_heartbeat()
    print("drone connected")

    async def handle_command(command):
        print(f"received command: {command}")

        parts = command.split(":")
        cmd = parts[0].strip().lower()
        param = float(parts[1]) if len(parts) > 1 else None

        if cmd == "arm" and not is_armed:
            arm_drone()
        elif cmd == "takeoff" and is_armed and param:
            takeoff_drone(param)
        elif cmd == "land" and is_armed:
            land_drone()
        elif cmd == "disarm" and is_armed:
             disarm_drone()
       # elif cmd == "arm" and is_armed:
       #     arm_again()  
        else:
            print("error: incorrect command")

    # Sottoscrizione ai comandi WAMP
    await session.subscribe(handle_command, "mavlink.command")
    print("subscribed to the WAMP topic: 'mavlink.command'")

# Avvia il client WAMP
if __name__ == "__main__":
    run(component)

