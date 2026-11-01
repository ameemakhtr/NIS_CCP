"""
Custom Hybrid Classical Cipher Implementation
Course: Network and Information Security (CT-486) - Dr. Shariq Mahmood Khan
Complex Computing Problem [CLO3]

Classical Ciphers Used (from Course Lectures):
1. Stage 1: Polyalphabetic Substitution (Vigenere Cipher - 3-Vigenere-Cipher.pdf)
2. Stage 2: Polygraphic Block Transformation (Hill Cipher - 7-Hill-Ciphers.pdf)
3. Baseline: Shift (Caesar) Cipher (2-Shift-Cipher.pdf)
"""

from typing import Tuple, List, Optional
import math


def clean_text(text: str) -> str:
    """Preprocess text: uppercase A-Z only."""
    return "".join([c.upper() for c in text if c.isalpha()])


def egcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean Algorithm to find modular inverse."""
    if a == 0:
        return (b, 0, 1)
    g, y, x = egcd(b % a, a)
    return (g, x - (b // a) * y, y)


def modinv(a: int, m: int = 26) -> Optional[int]:
    """Computes modular multiplicative inverse of a modulo m."""
    g, x, _ = egcd(a % m, m)
    if g != 1:
        return None
    return x % m


class ShiftCipher:
    """
    Standard single-stage classical Shift Cipher (2-Shift-Cipher.pdf)
    Used for baseline efficiency and security comparison.
    """
    def __init__(self, shift: int = 3):
        self.shift = shift % 26

    def encrypt(self, plaintext: str) -> str:
        cleaned = clean_text(plaintext)
        return "".join([chr((ord(c) - 65 + self.shift) % 26 + 65) for c in cleaned])

    def decrypt(self, ciphertext: str) -> str:
        cleaned = clean_text(ciphertext)
        return "".join([chr((ord(c) - 65 - self.shift) % 26 + 65) for c in cleaned])


class CustomHybridCipher:
    """
    Two-Stage Hybrid Classical Cipher combining:
    - Stage 1: Vigenere Cipher (Polyalphabetic Substitution) [3-Vigenere-Cipher.pdf]
    - Stage 2: 2x2 Hill Cipher (Polygraphic Block Transformation) [7-Hill-Ciphers.pdf]

    Enforces minimum key length of 10 characters.
    """

    def __init__(self, vigenere_key: str = "CRYPTOGRAPHYKEY", hill_key: str = "HILLCIPHERKEY"):
        """
        Initializes the hybrid cipher with keys from course classical techniques.
        Both keys must have length >= 10 characters.
        """
        self.vigenere_key = clean_text(vigenere_key)
        self.hill_key_phrase = clean_text(hill_key)

        if len(self.vigenere_key) < 10:
            raise ValueError(f"Vigenere key must be at least 10 characters! Got: {len(self.vigenere_key)}")
        if len(self.hill_key_phrase) < 10:
            raise ValueError(f"Hill key phrase must be at least 10 characters! Got: {len(self.hill_key_phrase)}")

        # Construct 2x2 Hill Key Matrix from key phrase
        self.hill_mat = self._derive_hill_matrix(self.hill_key_phrase)
        self.hill_inv = self._invert_hill_matrix(self.hill_mat)

    def _derive_hill_matrix(self, key_phrase: str) -> Tuple[int, int, int, int]:
        """
        Derives an invertible 2x2 matrix modulo 26 from the 10+ character key phrase.
        If initial letters are singular modulo 26, shifts until gcd(det, 26) == 1.
        """
        # Take first 4 characters as base matrix values
        vals = [ord(c) - 65 for c in key_phrase[:4]]
        a, b, c, d = vals[0], vals[1], vals[2], vals[3]

        # Ensure det is invertible mod 26
        det = (a * d - b * c) % 26
        offset = 1
        while modinv(det, 26) is None:
            # Adjust d slightly using remaining key entropy
            d = (d + offset) % 26
            det = (a * d - b * c) % 26
            offset += 1

        return (a, b, c, d)

    def _invert_hill_matrix(self, mat: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """Calculates matrix inverse modulo 26 for decryption."""
        a, b, c, d = mat
        det = (a * d - b * c) % 26
        inv_det = modinv(det, 26)
        if inv_det is None:
            raise ValueError("Matrix determinant is not invertible modulo 26!")

        ia = (inv_det * d) % 26
        ib = (inv_det * (-b)) % 26
        ic = (inv_det * (-c)) % 26
        id_val = (inv_det * a) % 26
        return (ia, ib, ic, id_val)

    # ------------------ STAGE 1: VIGENERE SUBSTITUTION ------------------
    def _vigenere_encrypt(self, text: str) -> List[int]:
        res = []
        k_len = len(self.vigenere_key)
        for i, ch in enumerate(text):
            shift = ord(self.vigenere_key[i % k_len]) - 65
            c = (ord(ch) - 65 + shift) % 26
            res.append(c)
        return res

    def _vigenere_decrypt(self, nums: List[int]) -> str:
        res = []
        k_len = len(self.vigenere_key)
        for i, val in enumerate(nums):
            shift = ord(self.vigenere_key[i % k_len]) - 65
            p = (val - shift) % 26
            res.append(chr(p + 65))
        return "".join(res)

    # ------------------ STAGE 2: HILL CIPHER (POLYGRAPHIC) ------------------
    def _hill_encrypt(self, nums: List[int]) -> List[int]:
        a, b, c, d = self.hill_mat
        res = []
        # Pad with 'X' (23) if odd length (standard Hill convention)
        if len(nums) % 2 != 0:
            nums = nums + [ord('X') - 65]

        for i in range(0, len(nums), 2):
            x1, x2 = nums[i], nums[i + 1]
            y1 = (x1 * a + x2 * c) % 26
            y2 = (x1 * b + x2 * d) % 26
            res.extend([y1, y2])
        return res

    def _hill_decrypt(self, nums: List[int]) -> List[int]:
        ia, ib, ic, id_val = self.hill_inv
        res = []
        for i in range(0, len(nums), 2):
            y1, y2 = nums[i], nums[i + 1]
            x1 = (y1 * ia + y2 * ic) % 26
            x2 = (y1 * ib + y2 * id_val) % 26
            res.extend([x1, x2])
        return res

    # ------------------ END-TO-END INTERFACE ------------------
    def encrypt(self, plaintext: str) -> str:
        """
        Two-stage encryption:
        Input -> [Stage 1: Vigenere Substitution] -> Intermediate -> [Stage 2: Hill Transformation] -> Ciphertext
        """
        cleaned = clean_text(plaintext)
        if not cleaned:
            return ""
        # Pad plaintext to even length with 'X' so original length is preserved cleanly
        if len(cleaned) % 2 != 0:
            cleaned += 'X'

        stage1_output = self._vigenere_encrypt(cleaned)
        stage2_output = self._hill_encrypt(stage1_output)
        return "".join(chr(val + 65) for val in stage2_output)

    def decrypt(self, ciphertext: str) -> str:
        """
        Two-stage decryption:
        Ciphertext -> [Reverse Stage 2: Inverse Hill] -> Intermediate -> [Reverse Stage 1: Inverse Vigenere] -> Plaintext
        """
        cleaned = clean_text(ciphertext)
        if not cleaned:
            return ""
        nums = [ord(c) - 65 for c in cleaned]
        stage2_reversed = self._hill_decrypt(nums)
        original_plaintext = self._vigenere_decrypt(stage2_reversed)
        return original_plaintext
