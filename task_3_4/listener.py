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

# Connessione MAVLink via UDP
master = mavutil.mavlink_connection("udp:localhost:14550")
print("Waiting the first message HEARTBEAT...")
master.wait_heartbeat()
print("drone ok")
async def publish_drone_status(session):
    """Pubblica periodicamente lo stato della batteria e la posizione del drone."""
    while True:
        battery_msg = master.recv_match(type="BATTERY_STATUS", blocking=False)
        position_msg = master.recv_match(type="GLOBAL_POSITION_INT", blocking=False)

        data = {}

        if battery_msg:
            voltage = battery_msg.voltages[0] / 1000  # Converti in Volt
            current = battery_msg.current_battery  # Corrente in centiAmpere
            
            # Se il valore della corrente è -1, impostiamo a 0 o un valore nullo
            if current == -1:
                print("current not available")
                current = 0
            else:
                current /= 100  # Converti in Ampere se il valore è valido
            
            data["battery"] = {
                "voltage": voltage,
                "current": current,
            }

        if position_msg:
            data["position"] = {
                "lat": position_msg.lat / 1e7,
                "lon": position_msg.lon / 1e7,
                "alt": position_msg.alt / 1000,  # Converti in metri
            }

        if data:
            session.publish("drone.status", data)
            print(f"drone status: {data}")

        await asyncio.sleep(1)  # Pubblica ogni secondo

async def arm_drone():
    print("arming")
    master.arducopter_arm()
    master.motors_armed_wait()
    master.set_mode("OFFBOARD")
    print("drone armed!")
    return "Drone armed"

async def takeoff_drone():  
    """Esegue il decollo del drone"""
    print(f"takeoff")

    if not master.motors_armed():
        print("drone not armed, arm the drone before to fly")
        master.arducopter_arm()
        master.motors_armed_wait()
        print("drone armed")

    master.set_mode("OFFBOARD")
    await asyncio.sleep(1)  # Attendi per assicurarti che il cambio di modalità avvenga

    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,  
        0,  # Confirmation
        0,  # Minimum pitch (usato per fixed-wing, lasciare 0)
        0,  # Ignorato per multirotore
        0,  # Ignorato per multirotore
        0,  # Yaw angle (lasciare 0 per usare la direzione attuale)
        0,  # Latitudine (lasciare 0 per multirotore)
        0,  # Longitudine (lasciare 0 per multirotore)
        2000000  # Altitudine in millimetri (10m)
    )

    print("takeoff sent")
    return "Takeoff initiated"

async def land_drone():
    """Esegue l'atterraggio del drone"""
    print("land")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND,
        0, 0, 0, 0, 0, 0, 0, 0
    )
    print("command land sent")
    
    await asyncio.sleep(5)  # Attendi qualche secondo per completare l'atterraggio
    await disarm_drone()  # Disarma il drone automaticamente

    return "Landing initiated"

async def disarm_drone():
    """Disarma il drone dopo l'atterraggio"""
    print("disarming drone...")
    master.arducopter_disarm()
    print("drone disarmed")
    return "Drone disarmed"

@component.on_join
async def on_join(session, details):
    print("WAMP ok")
    await session.register(arm_drone, "drone.arm")
    await session.register(takeoff_drone, "drone.takeoff")
    await session.register(land_drone, "drone.land")
    await session.register(disarm_drone, "drone.disarm")  # Nuova procedura per disarmare il drone
    asyncio.create_task(publish_drone_status(session))  # Avvia il loop di pubblicazione dello stato

# Avvia il nodo centrale WAMP
if __name__ == "__main__":
    run(component)
