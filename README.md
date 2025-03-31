# WAMP_MAVLink
This section details the implementation strategy employed in this thesis to establish
an effective MAVLink-WAMP bridge, ensuring seamless interoperability between the
two protocols while preserving the critical performance and security requirements of
OT environments.
The first operation that has been done is related with the installation of different and
important components that are:

• PX4 Autopilot;

• ROS2 Humble Hawksbill;

• Gazebo;

• QGroundControl;

For the installation of the previous components you can go [here](https://github.com/Andrewww00/Project_PX4_IIoT)

• Docker;

• Docker Container with Crossbar.io

For the installation of the previous components you can go [here](https://github.com/lucadagati/lab_industrial_iot)

The project is divided in five tasks.

## Task 1
Implement receiving WAMP commands and converting them into MAVLink messages Currently, the system receives data from MAVLink and forwards them on WAMP. Now it is necessary to implement the reverse flow: receive commands via WAMP and translate them into the corresponding MAVLink commands to control the drone.
A WAMP topic must then be defined to receive commands from a client, e.g. to arm the drone or make it take off. Once the command is received, the system must convert it into a MAVLink message and send it to the vehicle via the MAVLink protocol.

## Task 2
Create a mapping between WAMP and MAVLink commands. Since WAMP and MAVLink use different data formats and structures, it is necessary to establish a correspondence between the messages received on WAMP and the actual MAVLink commands. This requires identifying the main MAVLink control commands that should be supported, such as arming the drone, taking off, landing and changing flight modes. Once identified, a clear data structure must be created to automatically translate WAMP messages into the relevant MAVLink commands.

## Task 3
Create a central WAMP node for controlling the drone. To facilitate the management of communication between multiple clients and the drone, it is useful to implement a central WAMP node to act as a single access point for controlling the drone. This node will have to provide an API based on WAMP (Remote Procedure Call), allowing clients to send commands and receive updates on the status of the drone. In this way, it will be possible to separate the control logic of the WAMP network from the MAVLink management logic.
The central node will have to manage both the publication of events to transmit the status of the drone to the WAMP clients and the registration of remote procedures to allow commands to be sent to the drone.

## Task 4
Create a test client to verify communication from WAMP to MAVLink. To verify that the system is working correctly, it is useful to create a simple test client that can send commands to the WAMP node and receive responses. This client will simulate the interactions that end users would have with the system, ensuring that commands sent on WAMP are correctly translated into MAVLink instructions and transmitted to the drone.
The test client will need to be able to connect to the WAMP router, send commands such as arming and take-off and display the response received from the drone. This phase is crucial to identify any communication problems before developing a more advanced user interface.

## Task 5 
Creating a dashboard (also in flask) for remote control of the drone. Once the central WAMP node has been completed and the functioning of the system has been verified with a test client, we can move on to the development of a graphic interface that allows users to control the drone intuitively.
This dashboard should include buttons for arming, take-off and landing, as well as a system for displaying the status of the drone in real time. It might be useful to integrate a display of GPS position and battery status to enhance the user experience. The interface could be developed as a web page, with a WAMP client that connects to the central node and allows users to send commands and monitor the aircraft.



