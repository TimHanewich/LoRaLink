import binary

pulse_call = binary.bits_to_byte([True, False, False, False, False, False, False, False]) # Single-byte representation of a pulse call.
pulse_echo = binary.bits_to_byte([True, True, False, False, False, False, False, False]) # Single-byte representation of a pulse echo.

class OperationalCommand:
    def __init__(self) -> None:
        self.throttle:float = 0.0
        self.steer:float = 0.0
    
    def encode(self) -> bytes:
        """Encodes the operational command into a series of two bytes."""
        
        # determine throttle direction
        bit_throttle_direction:bool = False
        if self.throttle >= 0: 
            bit_throttle_direction = True
        else:
            bit_throttle_direction = False

        # determine throttle bits
        throttleabs:float = abs(min(max(self.throttle, -1.0), 1.0))
        print(throttleabs)
        throttleval:int = int(throttleabs * 63)
        throttlevalbits:list[bool] = binary.byte_to_bits(throttleval)
        throttle0:bool = throttlevalbits[2]
        throttle1:bool = throttlevalbits[3]
        throttle2:bool = throttlevalbits[4]
        throttle3:bool = throttlevalbits[5]
        throttle4:bool = throttlevalbits[6]
        throttle5:bool = throttlevalbits[7]

        # determine steer direction
        bit_steer_direction:bool = False
        if self.steer >= 0: 
            bit_steer_direction = True
        else:
            bit_steer_direction = False

        # determine steer bits
        steerabs:float = abs(min(max(self.steer, -1.0), 1.0))
        steerval:int = int(steerabs * 63)
        steervalbits:list[bool] = binary.byte_to_bits(steerval)
        steer0:bool = steervalbits[2]
        steer1:bool = steervalbits[3]
        steer2:bool = steervalbits[4]
        steer3:bool = steervalbits[5]
        steer4:bool = steervalbits[6]
        steer5:bool = steervalbits[7]

        # pack!
        byte1:int = binary.bits_to_byte([False, False, bit_throttle_direction, throttle0, throttle1, throttle2, throttle3, throttle4])
        byte2:int = binary.bits_to_byte([throttle5, bit_steer_direction, steer0, steer1, steer2, steer3, steer4, steer5])

        return bytes([byte1, byte2])





opcmd = OperationalCommand()
opcmd.throttle = 0.877
opcmd.steer = -0.334
print(opcmd.encode())



