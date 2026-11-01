"""
Custom Hybrid Classical Cipher Implementation
Course: Network and Information Security (CT-486)
CLO: Complex Computing Problem [CLO3]

Cipher Design:
Stage 1: Polyalphabetic Substitution (Vigenère Cipher) - provides Confusion.
Stage 2: Permutation / Columnar Transposition - provides Diffusion.
Both stages incorporate keys with length >= 10 characters.
"""

from typing import Tuple, List
import math


def clean_text(text: str) -> str:
    """Preprocess input text: uppercase A-Z only."""
    return "".join([c.upper() for c in text if c.isalpha()])


class ShiftCipher:
    """
    Standard single-stage classical Shift (Caesar) Cipher for baseline comparison.
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
    Two-Stage Classical Cipher:
    1. Vigenère Cipher (Substitution Stage)
    2. Columnar Transposition Cipher (Transposition Stage)
    """

    def __init__(self, sub_key: str = "CRYPTOGRAPHY", trans_key: str = "PERMUTATION"):
        """
        Initializes the cipher with substitution and transposition keys.
        Enforces minimum key length of 10 characters per assignment specification.
        """
        self.sub_key = clean_text(sub_key)
        self.trans_key = clean_text(trans_key)

        if len(self.sub_key) < 10:
            raise ValueError(f"Substitution key must be at least 10 characters! Got: {len(self.sub_key)}")
        if len(self.trans_key) < 10:
            raise ValueError(f"Transposition key must be at least 10 characters! Got: {len(self.trans_key)}")

    # ------------------ STAGE 1: VIGENÈRE SUBSTITUTION ------------------
    def _vigenere_encrypt(self, text: str) -> str:
        result = []
        k_len = len(self.sub_key)
        for i, ch in enumerate(text):
            shift = ord(self.sub_key[i % k_len]) - 65
            c = chr((ord(ch) - 65 + shift) % 26 + 65)
            result.append(c)
        return "".join(result)

    def _vigenere_decrypt(self, text: str) -> str:
        result = []
        k_len = len(self.sub_key)
        for i, ch in enumerate(text):
            shift = ord(self.sub_key[i % k_len]) - 65
            p = chr((ord(ch) - 65 - shift) % 26 + 65)
            result.append(p)
        return "".join(result)

    # ---------------- STAGE 2: COLUMNAR TRANSPOSITION ------------------
    def _get_transposition_order(self, key: str) -> List[int]:
        """
        Derives column read order based on alphabetical sorting of the key.
        Handles repeated characters stably.
        """
        indexed_key = [(ch, idx) for idx, ch in enumerate(key)]
        sorted_key = sorted(indexed_key, key=lambda x: (x[0], x[1]))
        # order maps rank -> original column index
        order = [item[1] for item in sorted_key]
        return order

    def _columnar_transposition_encrypt(self, text: str, key: str) -> str:
        """
        Writes text row-by-row into a grid of width = len(key),
        then reads out columns in alphabetical order of key characters.
        """
        col_count = len(key)
        order = self._get_transposition_order(key)
        
        # Build columns
        columns = [[] for _ in range(col_count)]
        for i, ch in enumerate(text):
            col_idx = i % col_count
            columns[col_idx].append(ch)

        # Read out columns according to alphabetical order
        ciphertext_chars = []
        for col_idx in order:
            ciphertext_chars.extend(columns[col_idx])

        return "".join(ciphertext_chars)

    def _columnar_transposition_decrypt(self, text: str, key: str) -> str:
        """
        Reconstructs the grid from columnar ciphertext and reads row-by-row.
        """
        total_len = len(text)
        col_count = len(key)
        order = self._get_transposition_order(key)

        num_full_rows = total_len // col_count
        remainder = total_len % col_count

        # Determine length of each column in the original matrix
        col_lengths = {}
        for c in range(col_count):
            col_lengths[c] = num_full_rows + (1 if c < remainder else 0)

        # Distribute ciphertext into columns following read order
        columns = {}
        curr_idx = 0
        for col_idx in order:
            length = col_lengths[col_idx]
            columns[col_idx] = list(text[curr_idx:curr_idx + length])
            curr_idx += length

        # Read out row-by-row
        result = []
        max_rows = num_full_rows + (1 if remainder > 0 else 0)
        for r in range(max_rows):
            for c in range(col_count):
                if r < len(columns[c]):
                    result.append(columns[c][r])

        return "".join(result)

    # ------------------ END-TO-END INTERFACE ------------------
    def encrypt(self, plaintext: str) -> str:
        """
        Two-stage encryption:
        Input -> [Stage 1: Vigenère Substitution] -> Intermediate -> [Stage 2: Columnar Transposition] -> Ciphertext
        """
        cleaned = clean_text(plaintext)
        if not cleaned:
            return ""
        stage1_output = self._vigenere_encrypt(cleaned)
        stage2_output = self._columnar_transposition_encrypt(stage1_output, self.trans_key)
        return stage2_output

    def decrypt(self, ciphertext: str) -> str:
        """
        Two-stage decryption:
        Ciphertext -> [Reverse Stage 2: Inverted Transposition] -> Intermediate -> [Reverse Stage 1: Reverse Vigenère] -> Plaintext
        """
        cleaned = clean_text(ciphertext)
        if not cleaned:
            return ""
        stage2_reversed = self._columnar_transposition_decrypt(cleaned, self.trans_key)
        original_plaintext = self._vigenere_decrypt(stage2_reversed)
        return original_plaintext
