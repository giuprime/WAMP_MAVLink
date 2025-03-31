import asyncio
from pymavlink import mavutil

# Connessione al drone
master = mavutil.mavlink_connection("udp:localhost:14550")
print("Waiting the first message HEARTBEAT...")
master.wait_heartbeat()
print("drone connected")

# Funzione per armare il drone
def arm_drone():
    print("arming...")
    master.arducopter_arm()
    master.motors_armed_wait()
    print("drone armed")

# Funzione per il takeoff
def takeoff_drone(altitude=20000000):  # Altitudine predefinita 10m
    print(f"takeoff")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 0, 0, 0, 0, 0, 0, altitude
    )
    print("command takeoff sent")


#def arm_again():
#    print("Ri-armamento...")
#    master.arducopter_arm()
#    master.motors_armed_wait()
#    print("Drone ri-armato!")

# Funzione per l'atterraggio
def land_drone():
    print("land")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND,
        0, 0, 0, 0, 0, 0, 0, 0
    )
def disarm_drone():
    print("disarming")
    master.arducopter_disarm()
    #asyncio.sleep(1) 
    print("drone disarmed")

async def execute_commands():
    # Step 1: Arm
    arm_drone()
    # Step 2: Takeoff
    takeoff_drone(altitude=20000000)

    # Step 3: 
    print("wait 3 minutes before the land")
    await asyncio.sleep(180)  # 3 minuti di attesa

    # Step 4: Land
    land_drone()
    
    print("Wait 3 minutes before the disarm")
    await asyncio.sleep(180)
    # Step 5: Disarm
    disarm_drone()
 

# Esecuzione della sequenza di comandi
asyncio.run(execute_commands())

