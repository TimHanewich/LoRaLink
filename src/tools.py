import machine
import ssd1306
import time
import reyax
import bincomms

class DisplayController:
    def __init__(self, oled:ssd1306.SSD1306_I2C) -> None:
        self._oled = oled

        # a unique identifier string establishing the setting or "screen status" that is currently being displayed
        self.page:str = "home"

        # for home page - battery levels, throttle, steer, etc.
        self.controller_soc:float = 0.0 # controller battery state of charge, as a percentage
        self.drone_soc:float = 0.0 # controller battery state of charge, as a percentage
        self.throttle:float = 0.5 # throttle as percentage
        self.steer:float = 0.5 # steer as a percentage
        self.no_response:bool = False # if flipped to true, means it has been a prolonged amount of time since we heard a packet returned from the drone

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

            # no response
            if self.no_response:
                self._oled.rect(0, 46, 46, 18, 1, True)
                self._oled.text("NO", 15, 48, 0)
                self._oled.text("RESP", 7, 56, 0)

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
            self._oled.text("N: " + str(self.lora_networkid), 0, 0)
            self._oled.text("A: " + str(self.lora_address), 0, 12)
            self._oled.text("B: " + str(self.lora_band), 0, 24)
            self._oled.text("P: " + str(self.lora_rfparams).replace("(", "").replace(")", "").replace(" ",""), 0, 36)
            self._oled.text("S: " + str(self.lora_output_power), 0, 48) # S is short for "strength"

            # print back button (selected)
            self._oled.text("+back+", 80, 56)
        
        elif pos == "stats":

            mins:int = int(round(time.ticks_ms() / 60000, 0))

            # print stats
            self._oled.text("U: " + str(mins) + " min", 0, 0)
            self._oled.text("S: " + str(self.stat_sent), 0, 12)
            self._oled.text("R: " + str(self.stat_received), 0, 24)

            # print back button (selected)
            self._oled.text("+back+", 80, 56)

        elif pos == "info":
            vtxt:str = "v. " + self.info_version
            vtxtpos:int = int(round((128 - (len(vtxt) * 8)) / 2, 0))
            self._oled.text(vtxt, vtxtpos, 0)
            self._oled.text("made by", 36, 20)
            self._oled.text("Tim Hanewich", 16, 32)
            
            # back button (selected)
            self._oled.text("+back+", 40, 56)

        else:
            self._oled.text("?", 0, 0)

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
        rm:reyax.ReceivedMessage = self.lora.receive()
        if rm != None:
            self.DisplayController.stat_received += 1 # increment # of messages received

            if len(rm.data) == len(bincomms.OperationalResponse().encode()):
                opresp = bincomms.OperationalResponse()
                opresp.decode(rm.data)
                self.DisplayController.drone_soc = opresp.battery
            else:
                print("Unknown message of length " + str(len(rm.data)) + " received. Ignoring.")