"""
Security Analysis and Attack Simulation Module
Course: Network and Information Security (CT-460 / CT-486)
Instructor: Dr. Shariq Mahmood Khan
Department of Computer Science & IT, NED University of Engineering & Technology, Karachi

Cryptanalytic Techniques:
1. Frequency Analysis & Index of Coincidence (IoC) against English baseline.
2. Known-Plaintext Attack (KPA) against Vigenere + Hill Hybrid Cipher.
"""

import time
from collections import Counter
from typing import Dict, List, Tuple, Optional, Any
from custom_cipher import clean_text, modinv, CustomHybridCipher

# Standard English letter frequencies (percentage)
ENGLISH_FREQ = {
    'A': 8.167, 'B': 1.492, 'C': 2.782, 'D': 4.253, 'E': 12.702,
    'F': 2.228, 'G': 2.015, 'H': 6.094, 'I': 6.966, 'J': 0.153,
    'K': 0.772, 'L': 4.025, 'M': 2.406, 'N': 6.749, 'O': 7.507,
    'P': 1.929, 'Q': 0.095, 'R': 5.987, 'S': 6.327, 'T': 9.056,
    'U': 2.758, 'V': 0.978, 'W': 2.360, 'X': 0.150, 'Y': 1.974,
    'Z': 0.074
}

ENGLISH_IC = 0.0667  # Index of Coincidence for natural English
RANDOM_IC = 0.0385   # Index of Coincidence for uniform random text


def _precompute_gl2() -> List[Tuple[int, int, int, int, int, int, int, int]]:
    """Precomputes all 157,248 invertible 2x2 matrices modulo 26 and their inverses."""
    gl2 = []
    for a in range(26):
        for b in range(26):
            for c_val in range(26):
                for d in range(26):
                    det = (a * d - b * c_val) % 26
                    inv_d = modinv(det, 26)
                    if inv_d is not None:
                        ia = (inv_d * d) % 26
                        ib = (inv_d * (-b)) % 26
                        ic = (inv_d * (-c_val)) % 26
                        id_val = (inv_d * a) % 26
                        gl2.append((ia, ib, ic, id_val, a, b, c_val, d))
    return gl2


# Global cached pool of invertible 2x2 matrices over Z_26
_GL2_CACHE = _precompute_gl2()


class FrequencyAnalyzer:
    """
    Performs letter frequency distribution and Index of Coincidence (IoC) calculations.
    """

    @staticmethod
    def calculate_frequencies(text: str) -> Dict[str, float]:
        cleaned = clean_text(text)
        n = len(cleaned)
        if n == 0:
            return {chr(c): 0.0 for c in range(65, 91)}
        counts = Counter(cleaned)
        return {chr(c): round((counts.get(chr(c), 0) / n) * 100.0, 3) for c in range(65, 91)}

    @staticmethod
    def calculate_ioc(text: str) -> float:
        """
        Calculates Index of Coincidence (IoC):
        IC = sum(f_i * (f_i - 1)) / (N * (N - 1))
        """
        cleaned = clean_text(text)
        n = len(cleaned)
        if n <= 1:
            return 0.0
        counts = Counter(cleaned)
        numerator = sum(f * (f - 1) for f in counts.values())
        return round(numerator / (n * (n - 1)), 5)

    @staticmethod
    def calculate_chi_squared(text: str) -> float:
        """
        Computes Chi-Squared statistic against standard English distribution.
        """
        cleaned = clean_text(text)
        n = len(cleaned)
        if n == 0:
            return 0.0
        counts = Counter(cleaned)
        chi_sq = 0.0
        for ch, expected_pct in ENGLISH_FREQ.items():
            observed = counts.get(ch, 0)
            expected = (expected_pct / 100.0) * n
            chi_sq += ((observed - expected) ** 2) / expected
        return round(chi_sq, 3)

    @classmethod
    def analyze(cls, plaintext: str, ciphertext: str) -> Dict[str, Any]:
        pt_clean = clean_text(plaintext)
        ct_clean = clean_text(ciphertext)

        return {
            "plaintext_length": len(pt_clean),
            "ciphertext_length": len(ct_clean),
            "plaintext_ioc": cls.calculate_ioc(pt_clean),
            "ciphertext_ioc": cls.calculate_ioc(ct_clean),
            "english_expected_ioc": ENGLISH_IC,
            "random_expected_ioc": RANDOM_IC,
            "plaintext_chi_sq": cls.calculate_chi_squared(pt_clean),
            "ciphertext_chi_sq": cls.calculate_chi_squared(ct_clean),
            "top_plaintext_letters": sorted(
                cls.calculate_frequencies(pt_clean).items(), key=lambda x: x[1], reverse=True
            )[:5],
            "top_ciphertext_letters": sorted(
                cls.calculate_frequencies(ct_clean).items(), key=lambda x: x[1], reverse=True
            )[:5],
        }


class KnownPlaintextAttacker:
    """
    Simulates Known-Plaintext Attack (KPA) against the Vigenere + Hill Hybrid Cipher.
    Follows Dr. Shariq Mahmood Khan's matrix formulation Y = K * x mod 26.
    """

    @classmethod
    def attack(
        cls,
        ciphertext: str,
        known_prefix: str,
        vigenere_key_len: int
    ) -> Dict[str, Any]:
        """
        Executes Known-Plaintext Attack using algebraic periodic constraint propagation.
        """
        start_time = time.perf_counter()
        c_clean = clean_text(ciphertext)
        p_clean = clean_text(known_prefix)

        L_V = vigenere_key_len
        c_nums = [ord(c) - 65 for c in c_clean]
        p_nums = [ord(c) - 65 for c in p_clean]

        known_even_len = (len(p_nums) // 2) * 2
        p_prefix = p_nums[:known_even_len]
        c_prefix = c_nums[:known_even_len]

        # Pack pairs for high-speed evaluation
        known_pairs = [
            (c_prefix[i], c_prefix[i + 1], p_prefix[i], p_prefix[i + 1], i, i + 1)
            for i in range(0, known_even_len, 2)
        ]

        matrices_evaluated = 0
        found = False
        recovered_hill = None
        recovered_vigenere_key = None

        # High-speed search through precomputed GL(2, Z_26) pool
        for ia, ib, ic, id_val, a, b, c_val, d in _GL2_CACHE:
            matrices_evaluated += 1

            consistent = True
            keystream = [None] * L_V

            for y1, y2, p1, p2, i1, i2 in known_pairs:
                # Invert Hill: x1 = (ia*y1 + ib*y2) mod 26
                x1 = (ia * y1 + ib * y2) % 26
                k1 = (x1 - p1) % 26
                pos1 = i1 % L_V
                if keystream[pos1] is not None and keystream[pos1] != k1:
                    consistent = False
                    break
                keystream[pos1] = k1

                # Invert Hill: x2 = (ic*y1 + id_val*y2) mod 26
                x2 = (ic * y1 + id_val * y2) % 26
                k2 = (x2 - p2) % 26
                pos2 = i2 % L_V
                if keystream[pos2] is not None and keystream[pos2] != k2:
                    consistent = False
                    break
                keystream[pos2] = k2

            if consistent and all(k is not None for k in keystream):
                found = True
                recovered_hill = (a, b, c_val, d, (ia, ib, ic, id_val))
                recovered_vigenere_key = "".join(chr(k + 65) for k in keystream)
                break

        elapsed = time.perf_counter() - start_time

        if not found or not recovered_hill:
            return {
                "success": False,
                "elapsed_seconds": elapsed,
                "matrices_evaluated": matrices_evaluated,
                "recovered_hill_mat": None,
                "recovered_vigenere_key": None,
                "recovered_full_plaintext": None,
            }

        ia, ib, ic, id_val = recovered_hill[4]

        # Full decryption using recovered parameters
        full_intermediate = []
        for b_idx in range(0, len(c_nums), 2):
            y1, y2 = c_nums[b_idx], c_nums[b_idx + 1]
            x1 = (ia * y1 + ib * y2) % 26
            x2 = (ic * y1 + id_val * y2) % 26
            full_intermediate.extend([x1, x2])

        full_plaintext = []
        for i, val in enumerate(full_intermediate):
            shift = ord(recovered_vigenere_key[i % L_V]) - 65
            p_val = (val - shift) % 26
            full_plaintext.append(chr(p_val + 65))

        return {
            "success": True,
            "elapsed_seconds": elapsed,
            "matrices_evaluated": matrices_evaluated,
            "recovered_hill_mat": recovered_hill[:4],
            "recovered_vigenere_key": recovered_vigenere_key,
            "recovered_full_plaintext": "".join(full_plaintext),
        }
