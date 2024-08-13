# LoRaLink Remote Controller
A fully 3D-printed remote controller that uses Long Range (LoRa) radio communications to control an RC car.

## Onboard Components
LoRaLink has quite a few components that serve various functions, including control input, communication, GUI display, etc.:
- 1 [SSD-1306 OLED display](https://a.co/d/6dm97JF) (128x64)
- 3 [16MM Push Buttons](https://a.co/d/9F2s5Ny)
- 2 [B10K Potentiometers](https://a.co/d/18x64NA) (knobs)
- 1 [Toggle Power Switch](https://a.co/d/8mkSPU3)
- 1 Raspberry Pi Pico
- 1 [REYAX RYLR998 LoRa Module](https://a.co/d/5QcWzvi)
- 1 [MT3608 Boost Converter](https://a.co/d/7Znw4Il)
- 1 18650 Lithium-Ion battery
- 1 [TP4056 Charge Controller](https://a.co/d/eq3EDgR)

## Communication Protocol
I've designed a minimalistic, lightweight, robust communication protocol to allow communications between the LoRaLink controller and the device that it is being controller.

The following communication protocol will be followed:

### *Possible Packet Types*:
- 0 - operational command (throttle/steer)
- 1 - operational response (battery)
- 2 - pulse call
- 3 - pulse echo

### Pulse call (Controller sending an "are you there?" to the rover)
![pulse call](https://i.imgur.com/afdzPOR.png)
Packet type - 2 bits

### Pulse echo (rover responding "Yes, I am here. Ready to go." back to the controller in response)
![pulse echo](https://i.imgur.com/DlVSA38.png)
Packet type - 2 bits

### Operational Command (control command send from controller to rover)
![operational command](https://i.imgur.com/XDpZQ8i.png)
Packet type - 2 bits
Throttle direction - 1 bit (0 = reverse, 1 = forward)
Throttle - 6 bits
Steer direction - 1 bit (0 = left, 1 = right)
Steer - 6 bits

### Operational Response (periodic status update sent from the rover to the controller)
![operational response](https://i.imgur.com/ac1lFlh.png)
Packet type - 2 bits
Battery level - 6 bits

## Pivot Point Solutions
![solutions](https://i.imgur.com/kKECvYp.png)