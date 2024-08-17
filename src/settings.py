# VERSION NUMBER
VERSION:str = "0.2.0"

# I2C settings (for the SSD-1306 OELD display)
i2c_bus:int = 0
i2c_sda:int = 12
i2c_scl:int = 13

# ADC GPIO's
battery_adc_gpio:int = 28
left_pot_adc_gpio:int = 26
right_pot_adc_gpio:int = 27

# buttons
left_button_gpio:int = 0
middle_button_gpio:int = 1
right_button_gpio:int = 2

# UART settings (for REYAX RYLR998)
uart_bus:int = 0
uart_baudrate:int = 115200
uart_tx:int = 16
uart_rx:int = 17

# boot up options
handshake:bool = False # Establish digital "handshake" with rover before proceeding to transmit data packets (normal operatiation)
neutralization:bool = True # neutralize inputs for safety before proceeding to send out control commands (make user put knobs in neutral position for safety purposes)