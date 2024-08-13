import machine
import ssd1306
import time
import WeightedAverageCalculator
import reyax
import bincomms
import framebuf

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

class DisplayController:
    def __init__(self, oled:ssd1306.SSD1306_I2C) -> None:
        self._oled = oled

        # a unique identifier string establishing the setting or "screen status" that is currently being displayed
        self.page:str = "home"

        # for home page - battery levels
        self.controller_soc:float = 0.0 # controller battery state of charge, as a percentage
        self.drone_soc:float = 0.0 # controller battery state of charge, as a percentage
        self.throttle:float = 0.5 # throttle as percentage
        self.steer:float = 0.5 # steer as a percentage

        # for RF config page - RYLR998 configuration
        self.lora_networkid:int = 18
        self.lora_address:int = 0
        self.lora_band:int = 915000000
        self.lora_rfparams:tuple[int, int, int, int] = (0, 0, 0, 0)
        self.lora_output_power:int = 22

        # for stat page - statistics
        self.stat_sent:int = 0 # how many messages have been sent so far.
        self.stat_received:int = 0 # how many messages have been received so far.

        # for info page - info about version
        self.info_version:str = "1.2.3"

    def display(self) -> None:
        """Displays current GUI 'position' on display."""

        # preliminary
        self._oled.fill(0)
        pos:str = self.page

        if pos[0:4] == "home":

            # determine state of charge display value and ensure each are at least 3 characters
            controller_soc_value_display:str = str(int(round(min(max(self.controller_soc, 0.0), 0.99) * 100, 0))) + "%"
            drone_soc_value_display:str = str(int(round(min(max(self.drone_soc, 0.0), 0.99) * 100, 0))) + "%"
            while len(controller_soc_value_display) < 3:
                controller_soc_value_display = " " + controller_soc_value_display
            while len(drone_soc_value_display) < 3:
                drone_soc_value_display = " " + drone_soc_value_display

            # show
            self._oled.text("C " + controller_soc_value_display, 0, 0)
            self._oled.text("D " + drone_soc_value_display, 0, 12)

            # Draw vertical line to separate info pane!
            self._oled.line(46, 0, 46, 64, 1)

            # menu options
            self._oled.text("stats", 67, 32) # see statistics being tracked (packets, time alive, etc.)
            self._oled.text("config", 63, 44) # See RF parameters
            self._oled.text("info", 71, 56) # info screen (system version, etc.)

            # Put selection on selection if there is any
            if self.page == "home.stats":
                self._oled.text("+", 59, 32)
                self._oled.text("+", 107, 32)
            elif self.page == "home.config":
                self._oled.text("+", 55, 44)
                self._oled.text("+", 111, 44)
            elif self.page == "home.info":
                self._oled.text("+", 63, 56)
                self._oled.text("+", 103, 56)

            # horizontal line separating menu options
            self._oled.line(46, 28, 128, 28, 1)

            # throttle line
            self._oled.text("T", 50, 2)
            self._oled.text("S", 50, 15)

            # throttle rectangle outline
            self._oled.rect(60, 2, 68, 8, 1) # X, Y, Width, Heigt, Color

            # steer rectangle outline
            self._oled.rect(60, 15, 68, 8, 1) # X, Y, Width, Heigt, Color

            # throttle fill bar
            tbf:int = int(round(68 * self.throttle, 0)) # throttle bar fill. 68 is the range of the bar (width)
            self._oled.rect(60, 2, tbf, 8, 1, True)

            # steer bar
            steer_indicator_x:int = 60 + int(60 * self.steer)
            self._oled.rect(steer_indicator_x, 15, 8, 8, 1, True)


        
        elif pos == "config":

            # print params
            oled.text("N: " + str(self.lora_networkid), 0, 0)
            oled.text("A: " + str(self.lora_address), 0, 12)
            oled.text("B: " + str(self.lora_band), 0, 24)
            oled.text("P: " + str(self.lora_rfparams).replace("(", "").replace(")", "").replace(" ",""), 0, 36)
            oled.text("S: " + str(self.lora_output_power), 0, 48) # S is short for "strength"

            # print back button (selected)
            oled.text("+back+", 80, 56)
        
        elif pos == "stats":

            mins:int = int(round(time.ticks_ms() / 60000, 0))

            # print stats
            oled.text("U: " + str(mins) + " min", 0, 0)
            oled.text("S: " + str(self.stat_sent), 0, 12)
            oled.text("R: " + str(self.stat_received), 0, 24)

            # print back button (selected)
            oled.text("+back+", 80, 56)

        elif pos == "info":
            vtxt:str = "v. " + self.info_version
            vtxtpos:int = int(round((128 - (len(vtxt) * 8)) / 2, 0))
            oled.text(vtxt, vtxtpos, 0)
            oled.text("made by", 36, 20)
            oled.text("Tim Hanewich", 16, 32)
            
            # back button (selected)
            oled.text("+back+", 40, 56)

        else:
            oled.text("?", 0, 0)

        # display!
        self._oled.show()

class ControllerBrain:

    def __init__(self, oled:ssd1306.SSD1306_I2C, lora:reyax.RYLR998) -> None:
        self.lora = lora

        # set up DisplayController
        self.DisplayController:DisplayController = DisplayController(oled)   

        # set up last time sent
        self.last_time_sent_ticks_ms:int = 0

    def display(self) -> None:
        self.DisplayController.display()

    @property
    def page(self) -> str:
        return self.DisplayController.page

    def goto(self, page:str) -> None:
        if page== "config": # RYLR998 config, so need to update those params
            self.DisplayController.lora_networkid = self.lora.networkid
            self.DisplayController.lora_address = self.lora.address
            self.DisplayController.lora_band = self.lora.band
            self.DisplayController.lora_output_power = self.lora.output_power
            self.DisplayController.lora_rfparams = self.lora.rf_parameters

        # go to the page
        self.DisplayController.page = page

    def set_pot1(self, reading:float) -> None:
        if self.page[0:4] == "home":
            self.DisplayController.throttle = reading
        
    def set_pot2(self, reading:float) -> None:
        if self.page[0:4] == "home":
            self.DisplayController.steer = reading

    def push_button1(self) -> None:
        if self.page[0:4] == "home":
            extension:str = self.page[5:]
            if extension == "stats":
                self.goto("home.info")
            elif extension == "config":
                self.goto("home.stats")
            elif extension == "info":
                self.goto("home.config")
            else:
                self.goto("home.stats")

    def push_button2(self) -> None:
        if self.page == "home.stats":
            self.goto("stats")
        elif self.page == "home.config":
            self.goto("config")
        elif self.page == "home.info":
            self.goto("info")
        elif self.page == "config":
            self.goto("home.stats")
        elif self.page == "stats":
            self.goto("home.stats")
        elif self.page == "info":
            self.goto("home.stats")

    def push_button3(self) -> None:
        if self.page[0:4] == "home":
            extension:str = self.page[5:]
            if extension == "stats":
                self.goto("home.config")
            elif extension == "config":
                self.goto("home.info")
            elif extension == "info":
                self.goto("home.stats")
            else:
                self.goto("home.stats")

    def tendto(self) -> None:

        # send?
        if self.page.startswith("home"): # are we on home?
            if (time.ticks_ms() - self.last_time_sent_ticks_ms) >= 250: # is it time to send?

                # send the ControlCommand!
                opcmd = bincomms.OperationalCommand()
                opcmd.throttle = self.DisplayController.throttle
                opcmd.steer = self.DisplayController.steer
                to_send:bytes = opcmd.encode()
                self.lora.send(1, to_send)

                # increment sent counter
                self.DisplayController.stat_sent += 1

                # mark last sent time
                self.last_time_sent_ticks_ms = time.ticks_ms()
        
        # try to receive
        rm:reyax.ReceivedMessage = lora.receive()
        if rm != None:
            self.DisplayController.stat_received += 1 # increment # of messages received

            if len(rm.data) == len(bincomms.OperationalResponse().encode()):
                opresp = bincomms.OperationalResponse()
                opresp.decode(rm.data)
                self.DisplayController.drone_soc = opresp.battery
            else:
                print("Unknown message of length " + str(len(rm.data)) + " received. Ignoring.")




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
CONTROLLER:ControllerBrain = ControllerBrain(oled, lora)
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