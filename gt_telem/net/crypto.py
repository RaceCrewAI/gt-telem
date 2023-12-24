from __future__ import annotations

import struct

from salsa20 import Salsa20_xor


class PDEncyption:
    """
    PDEncyption class provides methods for decrypting ciphertext using Salsa20 stream cipher.
    Credit to https://github.com/Nenkai/PDTools

    Methods:
    - decrypt(ciphertext: bytes, is_gt7: bool = True) -> bytes:
        Decrypts the provided ciphertext using Salsa20 stream cipher.

        Parameters:
        - ciphertext (bytes): The encrypted data to be decrypted.
        - is_gt7 (bool): Flag indicating whether to use the GT7 key. Default is True.

        Returns:
        bytes: The decrypted plaintext.

    Example:
    ```python
    pd_encryption = PDEncyption()
    decrypted_data = pd_encryption.decrypt(encrypted_data, is_gt7=True)
    ```

    Note:
    The `is_gt7` parameter specifies whether the decryption should use the GT7 key.
    """

    _DEFAULT_KEY = b"Simulator Interface Packet ver 0.0"
    _GT7_KEY = b"Simulator Interface Packet GT7 ver 0.0"
    _IV_MASK: int = 0xDEADBEAF

    def __init__(self, is_gt7):
        self.is_gt7 = is_gt7

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypts the provided ciphertext using Salsa20 stream cipher.

        Parameters:
        - ciphertext (bytes): The encrypted data to be decrypted.
        - is_gt7 (bool): Flag indicating whether to use the GT7 key. Default is True.

        Returns:
        bytes: The decrypted plaintext.
        """
        seed = struct.unpack("<I", ciphertext[0x40:0x44])[0]
        iv = seed ^ self._IV_MASK
        iv = struct.pack("<II", iv, seed)
        return Salsa20_xor(
            ciphertext, iv, self._GT7_KEY[:32] if self.is_gt7 else self._DEFAULT_KEY[:32]
        )
