import machine
import ssd1306
import time
import WeightedAverageCalculator


class PageTracker:
    """A simple system purley for tracking where the user is in a GUI. Track pages and flags. Display generation based on the GUI position is handled separately."""

    def __init__(self) -> None:
        self._position:list[str] = []
        self._flags:list[tuple[str, str]] = []

    def advance(self, next:str) -> None:
        self._position.append(next)
        self._selection = None

    def retreat(self) -> None:
        if len(self._position) > 0:
            self._position.pop(len(self._position) - 1) # remove the last one
            self._selection = None

    @property
    def position(self) -> str:
        ToReturn:str = ""
        for pos in self._position:
            ToReturn = ToReturn + pos + "."
        if len(ToReturn) > 0:
            ToReturn = ToReturn[0:-1]
        return ToReturn
    
    def set_flag(self, name:str, value:str) -> None:
        """Add or update a flag."""
        self.remove_flag(name)
        self._flags.append((name, value))

    def remove_flag(self, name:str) -> None:
        """Remove a flag by name."""
        ToRemoveIndex:int = None
        for i in range(0, len(self._flags)):
            if self._flags[i][0] == name:
                print("This one matches! " + str(self._flags[i]) +  " at index " + str(i))
                ToRemoveIndex = i
        if ToRemoveIndex != None:
            self._flags.pop(ToRemoveIndex)

    def get_flag(self, name:str) -> str:
        """Retrieve flag value based on name."""
        for flag in self._flags:
            if flag[0] == name:
                return flag[1]
        return None
    
    def clear_flags(self) -> None:
        """Delete all flags."""
        self._flags = []

    def is_flag(self, name:str, value:str) -> bool:
        """Checks if a flag is set to a certain value."""
        flag:tuple[str, str] = self.get_flag(name)
        if flag == None:
            return False
        else:
            return flag == value

class DisplayController:
    def __init__(self, oled:ssd1306.SSD1306_I2C) -> None:
        self._oled = oled

        # set up PageTracker
        self.PageTracker = PageTracker()

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
        pos:str = self.PageTracker.position

        if pos == "home":

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

            # show carrot if stats is selected
            if self.PageTracker.is_flag("selection", "stats"):
                self._oled.text("+", 59, 32)
                self._oled.text("+", 107, 32)
            elif self.PageTracker.is_flag("selection", "config"):
                self._oled.text("+", 55, 44)
                self._oled.text("+", 111, 44)
            elif self.PageTracker.is_flag("selection", "info"):
                self._oled.text("+", 63, 56)
                self._oled.text("+", 103, 56)

            # horizontal line separating menu options
            self._oled.line(46, 28, 128, 28, 1)

            # throttle line
            self._oled.text("T", 50, 2)
            self._oled.text("S", 50, 15)

            # throttle rectangle outline
            self._oled.rect(60, 2, 68, 8, 1)

            # steer rectangle outline
            self._oled.rect(60, 15, 68, 8, 1)

            # throttle fill bar
            tbf:int = int(round(68 * self.throttle, 0)) # throttle bar fill. 68 is the range of the bar (width)
            self._oled.rect(60, 2, tbf, 8, 1, True)

            # steer bar
            steer_indicator_x:int = 60 + int(68 * self.steer) - 4
            self._oled.rect(steer_indicator_x, 15, 8, 8, 1, True)


        
        elif pos == "home.config":

            # print params
            oled.text("N: " + str(self.lora_networkid), 0, 0)
            oled.text("A: " + str(self.lora_address), 0, 12)
            oled.text("B: " + str(self.lora_band), 0, 24)
            oled.text("P: " + str(self.lora_rfparams).replace("(", "").replace(")", "").replace(" ",""), 0, 36)
            oled.text("S: " + str(self.lora_output_power), 0, 48) # S is short for "strength"

            # print back button (selected)
            oled.text("+back+", 80, 56)
        
        elif pos == "home.stats":

            mins:int = int(round(time.ticks_ms() / 60000, 0))

            # print stats
            oled.text("U: " + str(mins) + " min", 0, 0)
            oled.text("S: " + str(self.stat_sent), 0, 12)
            oled.text("R: " + str(self.stat_received), 0, 24)

            # print back button (selected)
            oled.text("+back+", 80, 56)

        elif pos == "home.info":
            vtxt:str = "v. " + self.info_version
            vtxtpos:int = int(round((128 - (len(vtxt) * 8)) / 2, 0))
            oled.text(vtxt, vtxtpos, 0)
            oled.text("made by", 36, 20)
            oled.text("Tim Hanewich", 16, 32)
            
            # back button (selected)
            if not self.PageTracker.is_flag("bootup", ""):
                oled.text("+back+", 40, 56)

        else:
            oled.text("?", 0, 0)

        # display!
        self._oled.show()

class ControllerBrain:

    def __init__(self, oled:ssd1306.SSD1306_I2C) -> None:
        self.DisplayController:DisplayController = DisplayController(oled)

    def boot(self) -> None:
        self.DisplayController.PageTracker._position = []
        self.DisplayController.PageTracker.advance("home")

# set up SSD-1306
i2c = machine.I2C(0, sda=machine.Pin(12), scl=machine.Pin(13))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# set up REYAX RYLR998
# import reyax
#u = machine.UART(0, baudrate=115200, tx=machine.Pin(16), rx=machine.Pin(17))
#r:reyax.RYLR998 = reyax.RYLR998(u)

# show boot up
dc = DisplayController(oled)
dc.PageTracker.advance("home")
dc.PageTracker.advance("info")
dc.PageTracker.set_flag("bootup", "") # add bootup flag so it doesn't print "+back+"
dc.display()
dc.PageTracker.clear_flags()
time.sleep(3)

# go back to home for start.
dc.PageTracker.retreat()
dc.display()

# set up potentiometers and buttons
pot1 = machine.ADC(machine.Pin(26)) # left pot
pot1_wac:WeightedAverageCalculator.WeightedAverageCalculator = WeightedAverageCalculator.WeightedAverageCalculator(0.75)
pot2 = machine.ADC(machine.Pin(27)) # right pot
pot2_wac = WeightedAverageCalculator.WeightedAverageCalculator = WeightedAverageCalculator.WeightedAverageCalculator(0.75)
button1 = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP) # left-most button
button2 = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP) # middle button
button3 = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP) # right-most button


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

    print("Button status: " + str(button1_pressed) + ", " + str(button2_pressed) + ", " + str(button3_pressed))

    # set pot values on the throttle + steer
    dc.throttle = pot1r
    dc.steer = pot2r
    
    # display and wait
    dc.display()
    time.sleep_ms(10)