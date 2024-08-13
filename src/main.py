import machine
import ssd1306
import time
import WeightedAverageCalculator
import reyax
import bincomms
import framebuf
import tools

# set up SSD-1306
i2c = machine.I2C(0, sda=machine.Pin(12), scl=machine.Pin(13))
if 60 not in i2c.scan():
    led = machine.Pin("LED", machine.Pin.OUT)
    while True:
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
oled.text("Loading...", 0, 0)
oled.show()

# set up ADC for reading internal battery level
battery_adc = machine.ADC(machine.Pin(28))

# HIJACK! BATTERY TESTING!
# wac = WeightedAverageCalculator.WeightedAverageCalculator()
# while True:
#     reading:int = battery_adc.read_u16()
#     readingf:float = wac.feed(reading)
#     oled.fill(0)
#     oled.text(str(round(readingf, 0)), 0, 24)
#     oled.show()
#     time.sleep(0.25)

# Set up LoRa RYLR998 Module and pulse it to check that it is connected
oled.fill(0)
ba_wifi = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00?\x80\x00\x00?\xf8\x00\x00?\xfe\x00\x00?\xff\x80\x00?\xff\xe0\x00?\xff\xf0\x00\x00\x7f\xf8\x00\x00\x0f\xfc\x00\x00\x07\xfe\x000\x01\xff\x00?\x80\xff\x80?\xf0\x7f\xc0?\xf8?\xc0?\xfe\x1f\xe0?\xff\x0f\xe0\x07\xff\x87\xf0\x00\xff\x87\xf0\x00?\xc3\xf8\x00\x1f\xe3\xf8\x0f\x8f\xe1\xf8\x1f\xc7\xe1\xf8?\xc7\xf0\xfc?\xe3\xf0\xfc?\xe3\xf0\xfc?\xe3\xf0\xfc?\xe1\xf8\xfc\x1f\xc1\xf8\xfc\x0f\x81\xf8\xfc\x00\x00\x00\x00\x00\x00\x00\x00')
fb_wifi = framebuf.FrameBuffer(ba_wifi, 32, 32, framebuf.MONO_HLSB)
oled.blit(fb_wifi, 48, 0)
oled.text("Pulsing LoRa", 16, 38)
u = machine.UART(0, baudrate=115200, tx=machine.Pin(16), rx=machine.Pin(17))
lora:reyax.RYLR998 = reyax.RYLR998(u)
LoraConfirmed:bool = False
LoraPulseAttempts:int = 0
while LoraPulseAttempts < 10:
    
    oled.rect(0, 50, 128, 14, 0, True) # clear out the attempt #

    # print attempt #
    attempt_number_text:str = "Attempt " + str(LoraPulseAttempts + 1)
    attempt_number_pos_x:int = int((128 - (len(attempt_number_text) * 8)) / 2)
    oled.text(attempt_number_text, attempt_number_pos_x, 50)

    if lora.pulse == False:
        LoraPulseAttempts = LoraPulseAttempts + 1
        time.sleep(0.5)
    else:
        LoraConfirmed = True
        break
if LoraConfirmed:
    oled.rect(0, 50, 128, 14, 0, True) # clear out the attempt #
    oled.text("LoRa connected!", 4, 50)
    oled.show()
    time.sleep(0.5)
else:
    oled.rect(0, 50, 128, 14, 0, True) # clear out the attempt #
    oled.text("LoRa not con!", 12, 50)
    oled.show()
    exit()

# configure RYLR998
oled.rect(0, 38, 128, 26, 0, True) # clear out both the "Pulsing LoRa" line and the attempt # line
oled.text("Configuring LoRa", 0, 38)
oled.show()
try:
    lora.networkid = 18
    lora.address = 0
    lora.output_power = 22
    lora.band = 960000000 # set band to highest (fastest)
    lora.rf_parameters = (7, 9, 1, 8) # Spreadig Factor of 7, Bandwidth of 500 KHz, Coding Rate of 1, Programmed Preamble of 8
except:
    oled.fill(0)
    oled.text("FAILED", 40, 50)
    oled.show()
    exit()

# before proceeding, send out comms initiation to the rover... wait until we hear confirmation from the rover that it hears us and is ready.
ba_controller:bytearray = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xf0\x0f\xe0\x0f\xff\xff\xf0\x1f\x7f\xff\xf8\x1c\x07\xe0<9\xc0\x03\x1c;\xe0\x07\x9cw\xf0\x07\x8e\x7fx\x1f\xeeo8<\xf7\xefx<\xf7\xefx\x1f\xe7\xe7\xf0\x07\x87\xc3\xe0\x07\x83\xc1\xc0\x03\x03\xc0\x1f\xf8\x03\xc0\x7f\xfe\x03\xc0\xfc?\x03\xc1\xe0\x07\x83\xc7\xc0\x03\xc3\xff\x80\x01\xff\xfe\x00\x00\x7f|\x00\x00>\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
ba_car:bytearray = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xf0\x00\x00\xff\xff\x00\x03\xff\xff\xc0\x07\xff\xff\xe0\x07\xc0\x03\xe0\x0f\x00\x00\xf0\x0f\x00\x00\xf0\xfe\x00\x00\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xfe\xfc\xff\xff?\xf8\x7f\xfe\x1f\xf8\x7f\xfe\x1f|\xff\xff>\x7f\xff\xff\xfe\x7f\xff\xff\xfe?\xff\xff\xfc?\xff\xff\xfc?\x00\x00\xfc?\x00\x00\xfc\x1f\x00\x00\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
fb_controller = framebuf.FrameBuffer(ba_controller, 32, 32, framebuf.MONO_HLSB)
fb_car = framebuf.FrameBuffer(ba_car, 32, 32, framebuf.MONO_HLSB)
oled.fill(0)
oled.text("connecting", 24, 0)
oled.blit(fb_controller, 6, 10) # controller
oled.blit(fb_car, 90, 10) # car
oled.hline(42, 26, 44, 1) # horizontal line
pulse_attempt:int = 1
while True:

    oled.rect(0, 44, 128, 20, 0, True) # delete the status portion of the screen (Attempt #, listening/calling)
    
    # print attempt #
    attempt_number_text:str = "Attempt " + str(pulse_attempt)
    attempt_number_pos_x:int = int((128 - (len(attempt_number_text) * 8)) / 2)
    oled.text(attempt_number_text, attempt_number_pos_x, 44)

    # print calling
    oled.text("calling", 36, 56)
    oled.show()
    
    # send pulse
    lora.send(1, bytes([bincomms.pulse_call]))
    time.sleep(0.2)

    # print listening
    oled.rect(0, 56, 128, 8, 0, True) # clear out the "calling" on the bottom
    oled.text("listening", 28, 56)
    oled.show()

    # continuously read for messages
    received_msg:reyax.ReceivedMessage = None
    started_at:int = time.ticks_ms()
    while (time.ticks_ms() - started_at) < 5000 and received_msg == None:
        time.sleep(0.25)
        received_msg = lora.receive()
    
    # was a message received?
    if received_msg != None:
        if received_msg.data[0] == bincomms.pulse_echo: # if the data we received was an echo
            pulse_echoed = True
            break
        else:
            oled.fill(0)
            oled.text("Resp received", 0, 0)
            oled.text("But incorrect", 0, 12)
            oled.show()
            time.sleep(2)
     
    # increment
    pulse_attempt = pulse_attempt + 1

# set up potentiometers and buttons
oled.fill(0)
oled.text("Controls...", 0, 0)
oled.show()
pot1 = machine.ADC(machine.Pin(26)) # left pot
pot1_wac:WeightedAverageCalculator.WeightedAverageCalculator = WeightedAverageCalculator.WeightedAverageCalculator(0.75)
pot2 = machine.ADC(machine.Pin(27)) # right pot
pot2_wac = WeightedAverageCalculator.WeightedAverageCalculator = WeightedAverageCalculator.WeightedAverageCalculator(0.75)
button1 = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP) # left-most button
button2 = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP) # middle button
button3 = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP) # right-most button

# tracking of button status on last loop
button1_pressed_last:bool = False
button2_pressed_last:bool = False
button3_pressed_last:bool = False

# Set up controller!
oled.fill(0)
oled.text("Boot...", 0, 0)
oled.show()
CONTROLLER:tools.ControllerBrain = tools.ControllerBrain(oled, lora, battery_adc)
CONTROLLER.goto("home.stats") # start on home page

# infinite loop!
while True:

    # get reading of pots
    pot1r:float = (65535 - pot1.read_u16()) / 65535 # get reading of pot1 as a percentage
    pot2r:float = (65535 - pot2.read_u16()) / 65535 # get reading of pot2 as a percentage
    pot1r = pot1_wac.feed(pot1r) # pass pot1 reading through weighted average filter
    pot2r = pot2_wac.feed(pot2r) # pass pot2 reading through weighted average filter

    # get button push status
    button1_pressed:bool = not button1.value()
    button2_pressed:bool = not button2.value()
    button3_pressed:bool = not button3.value()

    # were the buttons just last let go from a push?
    if button1_pressed == False and button1_pressed_last == True:
        CONTROLLER.push_button1()
    if button2_pressed == False and button2_pressed_last == True:
        CONTROLLER.push_button2()
    if button3_pressed == False and button3_pressed_last == True:
        CONTROLLER.push_button3()

    # set pot values on the throttle + steer
    CONTROLLER.set_pot1(pot1r)
    CONTROLLER.set_pot2(pot2r)

    # tend to - send/receive, do whatever you have to do
    CONTROLLER.tendto()

    # display
    CONTROLLER.display()

    # set button last pressed status
    button1_pressed_last = button1_pressed
    button2_pressed_last = button2_pressed
    button3_pressed_last = button3_pressed
    
    # wait (small delay)
    time.sleep_ms(10)