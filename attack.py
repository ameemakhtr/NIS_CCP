"""
Security Analysis and Attack Simulation Module
Course: Network and Information Security (CT-486) - Dr. Shariq Mahmood Khan
Complex Computing Problem [CLO3]

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
        """
        Compares plaintext vs ciphertext statistical metrics.
        """
        pt_clean = clean_text(plaintext)
        ct_clean = clean_text(ciphertext)

        pt_ioc = cls.calculate_ioc(pt_clean)
        ct_ioc = cls.calculate_ioc(ct_clean)
        pt_chi = cls.calculate_chi_squared(pt_clean)
        ct_chi = cls.calculate_chi_squared(ct_clean)

        return {
            "plaintext_length": len(pt_clean),
            "ciphertext_length": len(ct_clean),
            "plaintext_ioc": pt_ioc,
            "ciphertext_ioc": ct_ioc,
            "english_expected_ioc": ENGLISH_IC,
            "random_expected_ioc": RANDOM_IC,
            "plaintext_chi_sq": pt_chi,
            "ciphertext_chi_sq": ct_chi,
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
    
    Attack Scenario:
    The adversary captures full ciphertext C and possesses a known segment of the
    original plaintext P_known (e.g., standard protocol header or greeting).
    
    Recovery Mechanism:
    Evaluates invertible 2x2 Hill matrices modulo 26.
    Inverts candidate Hill transformations on known ciphertext prefix and checks for
    strict keystream periodicity of length L_V (Vigenere period).
    Recovers both the Hill matrix and the Vigenere key, then decrypts the full message.
    """

    @classmethod
    def attack(
        cls,
        ciphertext: str,
        known_prefix: str,
        vigenere_key_len: int,
        target_hill_mat: Optional[Tuple[int, int, int, int]] = None
    ) -> Dict[str, Any]:
        """
        Executes Known-Plaintext Attack.
        
        Args:
            ciphertext: Full intercepted ciphertext.
            known_prefix: Known plaintext segment (must cover at least 2 * vigenere_key_len).
            vigenere_key_len: Length of Vigenere key (>= 10).
            target_hill_mat: Optional hint to fast-path or search around target matrix.
        """
        start_time = time.perf_counter()
        c_clean = clean_text(ciphertext)
        p_clean = clean_text(known_prefix)

        L_V = vigenere_key_len
        c_nums = [ord(c) - 65 for c in c_clean]
        p_nums = [ord(c) - 65 for c in p_clean]

        # Use an even length for block processing
        known_even_len = (len(p_nums) // 2) * 2
        p_prefix = p_nums[:known_even_len]
        c_prefix = c_nums[:known_even_len]

        matrices_evaluated = 0
        found = False
        recovered_hill = None
        recovered_vigenere_key = None

        # Loop through candidate 2x2 matrices
        for a in range(26):
            for b in range(26):
                for c_val in range(26):
                    for d in range(26):
                        matrices_evaluated += 1
                        det = (a * d - b * c_val) % 26
                        inv_d = modinv(det, 26)
                        if inv_d is None:
                            continue

                        # Candidate inverse matrix
                        ia = (inv_d * d) % 26
                        ib = (inv_d * (-b)) % 26
                        ic = (inv_d * (-c_val)) % 26
                        id_val = (inv_d * a) % 26

                        # Invert Hill on known blocks and check Vigenere keystream periodicity
                        consistent = True
                        keystream = [None] * L_V

                        for b_idx in range(0, known_even_len, 2):
                            y1, y2 = c_prefix[b_idx], c_prefix[b_idx + 1]
                            x1 = (y1 * ia + y2 * ic) % 26
                            x2 = (y1 * ib + y2 * id_val) % 26

                            # Check element 1
                            k1 = (x1 - p_prefix[b_idx]) % 26
                            kpos1 = b_idx % L_V
                            if keystream[kpos1] is not None and keystream[kpos1] != k1:
                                consistent = False
                                break
                            keystream[kpos1] = k1

                            # Check element 2
                            k2 = (x2 - p_prefix[b_idx + 1]) % 26
                            kpos2 = (b_idx + 1) % L_V
                            if keystream[kpos2] is not None and keystream[kpos2] != k2:
                                consistent = False
                                break
                            keystream[kpos2] = k2

                        if consistent and all(k is not None for k in keystream):
                            found = True
                            recovered_hill = (a, b, c_val, d, (ia, ib, ic, id_val))
                            recovered_vigenere_key = "".join(chr(k + 65) for k in keystream)
                            break
                    if found:
                        break
                if found:
                    break
            if found:
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

        # Decrypt full ciphertext using recovered parameters
        full_intermediate = []
        for b_idx in range(0, len(c_nums), 2):
            y1, y2 = c_nums[b_idx], c_nums[b_idx + 1]
            x1 = (y1 * ia + y2 * ic) % 26
            x2 = (y1 * ib + y2 * id_val) % 26
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
