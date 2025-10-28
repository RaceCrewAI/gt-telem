import struct

from Crypto.Cipher import Salsa20


class PDEncyption:
    """
    PDEncyption class provides methods for decrypting ciphertext using Salsa20 stream cipher.
    Credit to https://github.com/Nenkai/PDTools
    """

    _DEFAULT_KEY = b"Simulator Interface Packet ver 0.0"
    _GT7_KEY = b"Simulator Interface Packet GT7 ver 0.0"
    _IV_MASK_A: int = 0xDEADBEAF  # Standard "A" heartbeat
    _IV_MASK_B: int = 0xDEADBEEF  # Extended "B" heartbeat with motion data
    _IV_MASK_TILDE: int = 0x55FABB4F  # "~" heartbeat with extended data

    def __init__(self, is_gt7, heartbeat_type: str = "A"):
        self.is_gt7 = is_gt7
        self.heartbeat_type = heartbeat_type

        # Set the appropriate IV mask based on heartbeat type
        if heartbeat_type == "A":
            self._iv_mask = self._IV_MASK_A
        elif heartbeat_type == "B":
            self._iv_mask = self._IV_MASK_B
        elif heartbeat_type == "~":
            self._iv_mask = self._IV_MASK_TILDE
        else:
            raise ValueError(f"Unsupported heartbeat type: {heartbeat_type}")

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypts the provided ciphertext using Salsa20 stream cipher.

        Parameters:
        - ciphertext (bytes): The encrypted data to be decrypted.

        Returns:
        bytes: The decrypted plaintext.
        """
        seed = struct.unpack("<I", ciphertext[0x40:0x44])[0]
        iv = seed ^ self._iv_mask
        iv_bytes = struct.pack("<II", iv, seed)

        # Use pycryptodome Salsa20
        key = self._GT7_KEY[:32] if self.is_gt7 else self._DEFAULT_KEY[:32]
        cipher = Salsa20.new(key=key, nonce=iv_bytes)
        return cipher.decrypt(ciphertext)
