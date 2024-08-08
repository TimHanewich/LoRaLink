import binary

pulse_call = binary.bits_to_byte([True, False, False, False, False, False, False, False]) # Single-byte representation of a pulse call.
pulse_echo = binary.bits_to_byte([True, True, False, False, False, False, False, False]) # Single-byte representation of a pulse echo.