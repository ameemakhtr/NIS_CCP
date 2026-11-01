"""
Security Analysis and Attack Simulation Module
Course: Network and Information Security (CT-486)
CLO: Complex Computing Problem [CLO3]

Provides:
1. Frequency Analysis & Index of Coincidence (IoC) evaluation vs. English standards.
2. Automated Known-Plaintext Attack (KPA) Engine using branch-and-bound constraint solver.
"""

import itertools
import math
import time
from collections import Counter
from typing import Dict, List, Tuple, Optional, Any
from custom_cipher import clean_text, CustomHybridCipher

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
    Performs monographic frequency distribution and Index of Coincidence (IoC) calculations.
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
    Simulates a Known-Plaintext Attack (KPA) against the Custom Hybrid Cipher.
    
    Attack Scenario:
    The adversary captures full ciphertext C and possesses a known segment of the
    original plaintext P_known (e.g. from the start of the message, common headers,
    standard protocol preamble).
    
    Reconstructs:
    1. Transposition column assignments.
    2. Vigenère keyword.
    3. Complete plaintext message for the remainder of the ciphertext.
    """

    @classmethod
    def attack(
        cls,
        ciphertext: str,
        known_prefix: str,
        trans_key_len: int,
        sub_key_len: int,
        max_branch_evals: int = 500000
    ) -> Dict[str, Any]:
        """
        Executes Known-Plaintext Attack using constraint-guided backtracking.
        
        Args:
            ciphertext: Intercepted ciphertext string.
            known_prefix: Known plaintext prefix string (at least 2.5 * trans_key_len).
            trans_key_len: Candidate columnar transposition width (>= 10).
            sub_key_len: Candidate Vigenère key length (>= 10).
            max_branch_evals: Guard against infinite loops.
        """
        start_time = time.perf_counter()
        c_clean = clean_text(ciphertext)
        p_clean = clean_text(known_prefix)

        W = trans_key_len
        L_sub = sub_key_len
        total_len = len(c_clean)
        known_len = len(p_clean)

        if known_len < W:
            raise ValueError(f"Known prefix must be at least {W} characters to establish initial constraints!")

        num_full = total_len // W
        rem = total_len % W

        branch_evaluations = 0
        found = False
        recovered_result = None

        # Slices partitioning:
        # In the ciphertext, exactly 'rem' slices have length (num_full + 1),
        # and (W - rem) slices have length num_full.
        # We test combinations of slice indices that have length (num_full + 1).
        comb_generator = itertools.combinations(range(W), rem) if rem > 0 else [()]

        for long_slice_indices in comb_generator:
            slice_lengths = [num_full + 1 if i in long_slice_indices else num_full for i in range(W)]
            slices = []
            curr = 0
            for l in slice_lengths:
                slices.append(c_clean[curr:curr + l])
                curr += l

            slices_used = [False] * W
            key_array = [None] * L_sub
            col_to_slice = [None] * W

            def dfs(col: int) -> bool:
                nonlocal branch_evaluations
                if col == W:
                    return True

                branch_evaluations += 1
                if branch_evaluations > max_branch_evals:
                    return False

                # Column c has length (num_full + 1) if c < rem else num_full
                req_len = num_full + 1 if col < rem else num_full
                known_rows = [r for r in range(req_len) if r * W + col < known_len]

                for s_idx in range(W):
                    if slices_used[s_idx] or slice_lengths[s_idx] != req_len:
                        continue

                    candidate_slice = slices[s_idx]
                    compatible = True
                    newly_set_keys = []

                    # Verify key consistency against known plaintext positions
                    for r in known_rows:
                        idx = r * W + col
                        p_ch = p_clean[idx]
                        c_ch = candidate_slice[r]
                        # In Stage 1: C_1 = (P + K) mod 26  ==>  K = (C_1 - P) mod 26
                        k_val = (ord(c_ch) - ord(p_ch)) % 26
                        k_pos = idx % L_sub

                        if key_array[k_pos] is not None:
                            if key_array[k_pos] != k_val:
                                compatible = False
                                break
                        else:
                            key_array[k_pos] = k_val
                            newly_set_keys.append(k_pos)

                    if compatible:
                        slices_used[s_idx] = True
                        col_to_slice[col] = s_idx

                        if dfs(col + 1):
                            return True

                        # Backtrack
                        slices_used[s_idx] = False
                        col_to_slice[col] = None

                    for k_pos in newly_set_keys:
                        key_array[k_pos] = None

                return False

            if dfs(0):
                found = True
                recovered_result = (list(col_to_slice), list(key_array), slices)
                break

        elapsed = time.perf_counter() - start_time

        if not found or not recovered_result:
            return {
                "success": False,
                "elapsed_seconds": elapsed,
                "branch_evaluations": branch_evaluations,
                "recovered_sub_key": None,
                "recovered_full_plaintext": None,
            }

        rec_col_to_slice, rec_key, rec_slices = recovered_result

        # Reconstruct full Vigenère key
        # In case some positions were not covered by known_len, fill from recovered pattern
        recovered_key_str = "".join(
            chr(k + 65) if k is not None else "?" for k in rec_key
        )

        # Reconstruct intermediate text
        max_rows = num_full + (1 if rem > 0 else 0)
        reconstructed_intermediate = []
        for r in range(max_rows):
            for c_idx in range(W):
                s_idx = rec_col_to_slice[c_idx]
                s = rec_slices[s_idx]
                if r < len(s):
                    reconstructed_intermediate.append(s[r])
        intermediate_str = "".join(reconstructed_intermediate)

        # Decrypt full message with recovered key
        recovered_full_pt = []
        for i, ch in enumerate(intermediate_str):
            k_char = rec_key[i % L_sub]
            if k_char is not None:
                orig_c = chr((ord(ch) - 65 - k_char) % 26 + 65)
                recovered_full_pt.append(orig_c)
            else:
                recovered_full_pt.append("?")

        return {
            "success": True,
            "elapsed_seconds": elapsed,
            "branch_evaluations": branch_evaluations,
            "recovered_col_mapping": rec_col_to_slice,
            "recovered_sub_key": recovered_key_str,
            "recovered_full_plaintext": "".join(recovered_full_pt),
        }
