## Onboard Components
- Control Components
    - 1 SSD1306
    - 3 push buttons: 16.5mm
    - 2 B10K potentiometers: 7.5mm hole.    
    - Power toggle switch: 21mm   
- Raspberry Pi Pico
- REYAX RYLR998
- MT3608 boost converter
- 18650 battery and holder
- TP4056 charge controller, mounted with port accessible
    - Enclosure? https://cults3d.com/en/3d-model/gadget/tp4056-enclosure

## Communication Protocol
The following communication protocol will be followed:

### *Possible Packet Types*:
- 0 - operational command (throttle/steer)
- 1 - operational response (battery)
- 2 - pulse call
- 3 - pulse echo

### Pulse call (Controller sending an "are you there?" to the rover)
Packet type - 2 bits

### Pulse echo (rover responding "Yes, I am here. Ready to go." back to the controller in response)
Packet type - 2 bits

### Operational Command (control command send from controller to rover)
Packet type - 2 bits
Throttle - 7 bits
Steer - 7 bits

### Operational Response (periodic status update sent from the rover to the controller)
Packet type - 2 bits
Battery level - 6 bits