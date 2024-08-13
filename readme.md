# LoRaLink RC Remote Controller
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

## Wiring
The wiring diagram for the LoRaLink controller is included below. However, you can open [the schematic file](./schematic.drawio) on [draw.io](https://draw.io) as well (may be a bit easier to read).

![wiring](https://i.imgur.com/a1LYTrq.png)

## Assembly
I've provided the STL files for this design that you can 3D-print yourself on Thingiverse [here](https://www.thingiverse.com/thing:6729642). Altogether, there are three parts you'll need to print:

|Name|Description|Grams of PLA (20% infill)|
|-|-|-|
|bottom.stl|The "box" of the controller, that each electronic component will go into|40|
|top.stl|The top plate of the controller that the power switch, SSD-1306, potentiometers, and buttons will be mounted to|12|
|18650_frame.stl|A frame to hold the 18650 battery. Wrap wires around both ends to touch each terminal. Screw this into the bottom.stl|9|

## Communication Protocol
I've designed a minimalistic, lightweight, robust communication protocol to allow communications between the LoRaLink controller and the device that it is being controller.

All encoding/decoding of these packets into their binary representation is handled by the [bincomms.py](./src/bincomms.py) module, but I further describe the communication protocol below.

The LoRaLink controller and the device being controlled will use a pre-established protocol for communicating with each message being stored as a *packet*. There for **four** packet types:
- Packet Type **0** = Operational Command
- Packet Type **1** = Operational Response
- Packet Type **2** = Pulse Call
- Packet Type **3** = Pulse Echo

These packets are further described below:

### The "Pulse Call" Packet
When the LoRaLink controller boots up, it first aims to establish communication with the controlled device via a "pulse" check. The LoRaLink controller sends out this packet to the device and then awaits a response, confirming the presence of the controlled device.

The **Pulse Call** packet is only a single byte:

![pulse call](https://i.imgur.com/afdzPOR.png)

### The "Pulse Echo" Packet
When the controlled device (likely an RC car) boots up, it continuously listens for the **Pulse Call** packet above. Once it receives it, it confirms its presence by responding with the **Pulse Echo** packet, only a single byte:

![pulse echo](https://i.imgur.com/DlVSA38.png)

### The "Operational Command" Packet
Once communicatation is established via the Pulse Call/Echo packets above, The LoRaLink controller then begins continuously sending a stream of control commands to the controlled device using the **Operational Command** packet, consisting of two bytes, and described below:

![operational command](https://i.imgur.com/XDpZQ8i.png)

A value of **1** in the *Throttle Direction* bit means the throttle is positive (forward) while a value of **0** means the throttle is negative (reversing). The same applies to the steering: **0** is a left turn, **1** is a right turn, for the *Steering Direction* bit.

The throttle value and steering value are encoded as 6-bit values as seen above.

### The "Operational Response" Packet
Occasionally, during normal operation, the controlled device will send this packet back to the controller as a "I'm still alive" message, but also to inform it of its battery level (which will be displayed on the LoRaLink controller).

![operational response](https://i.imgur.com/ac1lFlh.png)

As seen above, the remaining 6 bits not used as a packet identifier are used to carry data about the battery. 