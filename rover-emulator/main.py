import reyax
import machine
import time
import bincomms
import random

u = machine.UART(0, tx=machine.Pin(16), rx=machine.Pin(17), baudrate=115200)
lora = reyax.RYLR998(u)
print("Pulse: " + str(lora.pulse))

# config
print("Configuring...")
lora.networkid = 18
lora.address = 1
lora.output_power = 22
lora.band = 960000000 # set band to highest (fastest)
lora.rf_parameters = (7, 9, 1, 8) # Spreadig Factor of 7, Bandwidth of 500 KHz, Coding Rate of 1, Programmed Preamble of 8
print("Configured!")

# infinite loop
operational_status_last_sent:int = time.ticks_ms()
while True:
    print("Trying to receive a message...")

    # try to receive
    rm:reyax.ReceivedMessage = lora.receive()
    if rm != None:
        print("Recieved: " + str(rm))
        if rm.data[0] == 128:
            print("It is a pulse call!")
            print("Sending back pulse echo...")
            lora.send(rm.address, bytes([192]))
        elif len(rm.data) == len(bincomms.OperationalCommand().encode()):
            opcmd = bincomms.OperationalCommand()
            opcmd.decode(rm.data)
            print("It is an operational command: " + str(opcmd))
        else:
            print("But it wasn't a pulse call!")

    # time to send out op status?
    if (time.ticks_ms() - operational_status_last_sent) > 15000:
        battery:float = random.randint(0, 100) / 100
        opstatus:bincomms.OperationalResponse = bincomms.OperationalResponse()
        opstatus.battery = battery
        lora.send(0, opstatus.encode())
        print("Just sent '" + str(opstatus.encode()) + "'!")
        operational_status_last_sent = time.ticks_ms()

    time.sleep_ms(100)