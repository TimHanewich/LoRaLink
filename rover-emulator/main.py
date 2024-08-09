import reyax
import machine
import time
import bincomms

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

while True:
    print("Trying to receive a message...")
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

    time.sleep_ms(100)