# DeVisor

DEVice SupraVISOR

The [DeVisor](https://gitlab/envot/devisor) is a python software to control, monitor and configure devices in a [EoT](https://envot.io).

                    __________________________
                    |                        |
                    |          MQTT          |
                    |         Broker         |
                    |________________________|
                     /\      /\         /\
                     /        \          \
                    /          \          \ 
                   /            \          \
              ___ \/_____   ___ \/_____   _\/_______
              |         |   |         |   |         |                                  
              |         |   |         |   |         |                                  
              | DeVisor |<=>| Device1 |   | Device2 |  0 0 0
              |         |   |         |   |         |                                  
              |_________|   |_________|   |_________|                                  
                     /\                     /\ 
                      \=====================/

The program's main section part is communicating with an [MQTT](https://mqtt.org) Broker specified at the startup following the [Homie convention](https://homieiot.github.io/).
For every device an extra thread with an extra connection to the Broker is created, which can be controlled, monitored and configured via the MQTT Broker.
