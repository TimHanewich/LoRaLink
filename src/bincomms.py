import binary

pulse_call = binary.bits_to_byte([True, False, False, False, False, False, False, False]) # Single-byte representation of a pulse call.
pulse_echo = binary.bits_to_byte([True, True, False, False, False, False, False, False]) # Single-byte representation of a pulse echo.

class OperationalCommand:
    def __init__(self) -> None:
        self.throttle:float = 0.0
        self.steer:float = 0.0

    def __repr__(self) -> str:
        return str({"throttle": self.throttle, "steer": self.steer})
    
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

    def decode(self, bs:bytes) -> None:
        """Decodes a two-byte sequence into a OperationalCommand."""

        if len(bs) != 2:
            raise Exception("Provided bytes are not a valid OperationalCommand! Length must be 2 bytes.")
        
        # decode
        b1bits:list[bool] = binary.byte_to_bits(bs[0])
        b2bits:list[bool] = binary.byte_to_bits(bs[1])

        # check if the packet type identifier is correct (first two bytes)
        if b1bits[0] == True or b1bits[1] == True:
            raise Exception("Provided bytes are not an OperationalCommand! The packet type identifier did not match the OperationalCommand type.")
        
        # decode throttle
        throttle:int = binary.bits_to_byte([False, False, b1bits[3], b1bits[4], b1bits[5], b1bits[6], b1bits[7], b2bits[0]]) # convert the 6-bits into a value (lead with two empties)
        throttlef:float = throttle / 63 # convert back into float (percent) representation.
        if b1bits[2] == False: # if the direction bit is set to False, this means it is a negative throttle, so multiply by 1
            throttlef = throttlef * -1
        self.throttle = throttlef

        # decode steer
        steer:int = binary.bits_to_byte([False, False, b2bits[2], b2bits[3], b2bits[4], b2bits[5], b2bits[6], b2bits[7]]) # convert the 6-bits into a value (lead with two empties)
        steerf:float = steer / 63 # convert back into float (percent) representation.
        if b2bits[1] == False: # if the direction bit is set to False, this means it is a negative throttle, so multiply by 1
            steerf = steerf * -1
        self.steer = steerf



for x in range(-100, 100):
    percent = x / 100

    opcmd = OperationalCommand()
    opcmd.throttle = percent
    opcmd.steer = percent
    bs = opcmd.encode()
    print("For " + str(opcmd) + ": ")
    print(bs)

    opcmd2 = OperationalCommand()
    opcmd2.decode(bs)
    print("Decoded: " + str(opcmd2))
    print("--------")
    input()



