import binary

@property
def pulse_call() -> int:
    """Returns the single-byte representation of a pulse call."""
    return binary.bits_to_byte([True, False, False, False, False, False, False, False])

@property
def pulse_echo() -> int:
    """Returns the single-byte representation of a pulse echo."""
    return binary.bits_to_byte([True, True, False, False, False, False, False, False])