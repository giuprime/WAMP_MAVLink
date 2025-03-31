import asyncio
from autobahn.asyncio.component import Component, run

REALM = "realm1"
ROUTER_URL = "ws://localhost:8181/ws"

component = Component(
    transports=ROUTER_URL,
    realm=REALM
)

AVAILABLE_COMMANDS = ["arm", "takeoff", "disarm", "land"]

@component.on_join
async def on_join(session, details):
    print("connected to WAMP!")

    # Funzione asincrona per ricevere i comandi dall'utente senza bloccare il server
    async def get_command():
        while True:
            print("\nPossible command: arm, takeoff, land, disarm, exit")
            command = input("Insert the command: ").strip().lower()

            if command == "exit":
                print("programm closed")
                await session.leave()
                break  

            if command not in AVAILABLE_COMMANDS and not command.startswith("takeoff:"):
                print("command not sent")
            elif command.startswith("takeoff:"):
                # Verifica che il comando takeoff contenga un'altezza
                try:
                    altitude = float(command.split(":")[1])  # Estrae l'altitudine dal comando
                    # Invia il comando takeoff con l'altitudine
                    session.publish("mavlink.command", f"takeoff:{altitude}")
                    print(f"takeoff sent")
                except ValueError:
                    print("errore: incorrect height")
            else:
                # Invia il comando direttamente
                session.publish("mavlink.command", command)
                print(f"command sent: {command}")

    # Avvia il ciclo di input dell'utente in modo asincrono
    asyncio.create_task(get_command())

# Avvia il client WAMP
if __name__ == "__main__":
    run(component)
