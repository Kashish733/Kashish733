def bytes_to_bits(data: bytes):
    bits = []
    for b in data:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    return bits


def bits_to_bytes(bits):
    if len(bits) % 8 != 0:
        raise ValueError("Bit count must be multiple of 8.")

    out = bytearray()
    for i in range(0, len(bits), 8):
        val = 0
        for bit in bits[i:i + 8]:
            val = (val << 1) | bit
        out.append(val)
    return bytes(out)


def int_to_32_bits(n: int):
    if n < 0:
        raise ValueError("Negative length is invalid.")
    if n > 0xFFFFFFFF:
        raise ValueError("Payload too large for 32-bit header.")
    return [(n >> i) & 1 for i in range(31, -1, -1)]


def bits_to_int(bits):
    n = 0
    for bit in bits:
        n = (n << 1) | bit
    return n


def period_sequence(base_period: int, mode: str):
    mode = mode.lower().strip()

    if mode == "fixed":
        seq = [base_period]
    elif mode == "cycle81628":
        seq = [8, 16, 28]
    elif mode == "cycle24816":
        seq = [2, 4, 8, 16]
    else:
        raise ValueError("Unsupported mode.")

    idx = 0
    while True:
        yield seq[idx]
        idx = (idx + 1) % len(seq)


def embed_payload(carrier_bytes: bytes, payload_bytes: bytes, start_bit: int, period_bits: int, mode: str):
    if start_bit < 0:
        raise ValueError("Start bit must be >= 0.")
    if period_bits <= 0:
        raise ValueError("Period must be > 0.")
    if not carrier_bytes:
        raise ValueError("Carrier file is empty.")
    if not payload_bytes:
        raise ValueError("Payload file is empty.")

    carrier_bits = bytes_to_bits(carrier_bytes)
    payload_bits = bytes_to_bits(payload_bytes)

    if start_bit >= len(carrier_bits):
        raise ValueError(
            f"Start bit {start_bit} is outside the carrier. Carrier has {len(carrier_bits)} bits."
        )

    all_bits = int_to_32_bits(len(payload_bytes)) + payload_bits

    pos = start_bit
    gen = period_sequence(period_bits, mode)

    for i, bit in enumerate(all_bits):
        if pos >= len(carrier_bits):
            raise ValueError(
                f"Carrier too small for payload. Failed at hidden bit #{i}, "
                f"carrier position {pos}, carrier length {len(carrier_bits)}."
            )
        carrier_bits[pos] = bit
        step = next(gen)
        if step <= 0:
            raise ValueError(f"Invalid step size: {step}")
        pos += step

    return bits_to_bytes(carrier_bits)


def extract_payload(stego_bytes: bytes, start_bit: int, period_bits: int, mode: str):
    if start_bit < 0:
        raise ValueError("Start bit must be >= 0.")
    if period_bits <= 0:
        raise ValueError("Period must be > 0.")
    if not stego_bytes:
        raise ValueError("Stego file is empty.")

    bits = bytes_to_bits(stego_bytes)

    if start_bit >= len(bits):
        raise ValueError("Start bit is outside the stego file.")

    pos = start_bit
    gen = period_sequence(period_bits, mode)

    header_bits = []
    for _ in range(32):
        if pos >= len(bits):
            raise ValueError("Cannot extract payload length.")
        header_bits.append(bits[pos])
        pos += next(gen)

    payload_len = bits_to_int(header_bits)

    payload_bits = []
    for _ in range(payload_len * 8):
        if pos >= len(bits):
            raise ValueError("Cannot extract full payload.")
        payload_bits.append(bits[pos])
        pos += next(gen)

    return bits_to_bytes(payload_bits)