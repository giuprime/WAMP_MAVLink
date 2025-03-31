import asyncio
import json
import threading
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from autobahn.asyncio.component import Component
from pymavlink import mavutil

# Configurazione Flask
app = Flask(__name__, template_folder="templates")
socketio = SocketIO(app, async_mode="threading")

# Configurazione WAMP
REALM = "realm1"
ROUTER_URL = "ws://localhost:8181/ws"

# Client WAMP
component = Component(
    transports=ROUTER_URL,
    realm=REALM,
)

# Connessione MAVLink via UDP
print("Waiting for the first HEARTBEAT message...")
master = mavutil.mavlink_connection("udp:localhost:14550")
master.wait_heartbeat()
print("drone connected")

# Variabile per salvare lo stato del drone
drone_status = {
    "battery": {"voltage": 0, "current": 0},
    "position": {"lat": 0, "lon": 0, "alt": 0}
}

# Funzione per aggiornare lo stato del drone e inviarlo alla dashboard
def update_drone_status(status):
    global drone_status
    drone_status.update(status)
    socketio.emit("update_status", drone_status)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send_command", methods=["POST"])
def send_command():
    data = request.get_json()
    if not data or "command" not in data:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    command = data["command"]
    altitude = int(float(data.get("altitude", 0)) * 1000)  # Conversione in mm
    latitude = int(float(data.get("latitude", 0)) * 1e7)  # Conversione in degE7
    longitude = int(float(data.get("longitude", 0)) * 1e7)  # Conversione in degE7

    print(f"Command received: {command} with altitude {altitude} mm, lat {latitude}, lon {longitude}")

    socketio.emit("send_command", {
        "command": command,
        "altitude": altitude,
        "latitude": latitude,
        "longitude": longitude
    })

    return jsonify({"status": "OK", "command": command})

@component.on_join
async def on_join(session, details):
    print("ok WAMP")

    async def publish_drone_status():
        while True:
            battery_msg = master.recv_match(type="BATTERY_STATUS", blocking=False)
            position_msg = master.recv_match(type="GLOBAL_POSITION_INT", blocking=False)

            data = {}

            if battery_msg:
                data["battery"] = {
                    "voltage": battery_msg.voltages[0] / 1000,
                    "current": battery_msg.current_battery / 100
                }

            if position_msg:
                data["position"] = {
                    "lat": position_msg.lat / 1e7,
                    "lon": position_msg.lon / 1e7,
                    "alt": position_msg.alt / 1000
                }

            if data:
                session.publish("drone.status", data)
                print(f"status: {data}")
                update_drone_status(data)

            await asyncio.sleep(1)

    asyncio.create_task(publish_drone_status())
    await session.subscribe(handle_command, "mavlink.command")
    print("subscribed to WAMP topic: 'mavlink.command'")

@socketio.on("send_command")
def handle_socket_command(data):
    command = data["command"]
    altitude = int(float(data.get("altitude", 0)) * 1000)
    latitude = int(float(data.get("latitude", 0)) * 1e7)
    longitude = int(float(data.get("longitude", 0)) * 1e7)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(handle_command(command, altitude, latitude, longitude))
    loop.close()

async def handle_command(command, altitude, latitude, longitude):
    print(f"received command: {command} with altitude {altitude} mm, lat {latitude}, lon {longitude}")

    if command == "arm":
        print("arm drone")
        master.arducopter_arm()
        master.motors_armed_wait()
        result = "Drone armed!"

    elif command == "takeoff":
        print("takeoff")
        master.mav.command_long_send(
            master.target_system, master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0, 0, 0, 0, 0, latitude, longitude, altitude  # Decollo con latitudine e longitudine
        )
        result = "takeoff initiated!"

    elif command == "land":
        print("landing")
        master.mav.command_long_send(
            master.target_system, master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND,
            0, 0, 0, 0, 0, 0, 0, 0
        )
        result = "landing initiated!"

    elif command == "disarm":
        print("disarming drone...")
        master.arducopter_disarm()
        result = "drone disarmed!"

    else:
        result = "unknown command!"

    print(f"command result {command}: {result}")
    socketio.emit("command_result", {"command": command, "result": result})

# Funzione per eseguire WAMP e Flask in parallelo
def run_wamp():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(component.start())

def run_flask():
    socketio.run(app, host="127.0.0.1", port=5000, debug=True, use_reloader=False)

if __name__ == "__main__":
    threading.Thread(target=run_wamp, daemon=True).start()
    run_flask()

