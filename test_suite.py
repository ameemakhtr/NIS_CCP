"""
Comprehensive Test Suite for Vigenere + Hill Hybrid Classical Cipher
Course: Network and Information Security (CT-486) - Dr. Shariq Mahmood Khan
Complex Computing Problem [CLO3]
"""

import unittest
from custom_cipher import CustomHybridCipher, ShiftCipher, clean_text
from attack import FrequencyAnalyzer, KnownPlaintextAttacker


class TestCustomCipher(unittest.TestCase):

    def setUp(self):
        self.vigenere_key = "CONFIDENTIALKEY"   # len 15 >= 10
        self.hill_key = "HILLCIPHERKEY"         # len 13 >= 10
        self.cipher = CustomHybridCipher(self.vigenere_key, self.hill_key)
        self.shift_cipher = ShiftCipher(shift=7)

    def test_key_length_validation(self):
        """Verify enforcement of key length >= 10 characters."""
        with self.assertRaises(ValueError):
            CustomHybridCipher("SHORT", "HILLCIPHERKEY")

        with self.assertRaises(ValueError):
            CustomHybridCipher("CONFIDENTIALKEY", "TINY")

        # Valid keys should not raise
        c = CustomHybridCipher("LONGKEYTEST1", "LONGKEYTEST2")
        self.assertIsNotNone(c)

    def test_clean_text(self):
        """Verify proper normalization to uppercase A-Z."""
        raw = "Hello, World! 123... How are you?"
        cleaned = clean_text(raw)
        self.assertEqual(cleaned, "HELLOWORLDHOWAREYOU")

    def test_roundtrip_various_lengths(self):
        """Test encryption and decryption round-trip across varying message sizes."""
        test_messages = [
            "SECRETDATA",                           # even length
            "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG",  # standard pangram (odd length -> padded)
            "A" * 150,                              # repetitive sequence
            "NETWORKSECURITYANDINFORMATIONASSURANCE" * 10  # long message (380 chars)
        ]

        for msg in test_messages:
            cleaned = clean_text(msg)
            expected = cleaned if len(cleaned) % 2 == 0 else cleaned + 'X'
            ciphertext = self.cipher.encrypt(msg)
            decrypted = self.cipher.decrypt(ciphertext)
            self.assertEqual(decrypted, expected, f"Failed round-trip for message: {msg[:20]}...")

    def test_shift_cipher_roundtrip(self):
        """Verify single-stage shift cipher baseline."""
        msg = "CLASSICALCIPHERTESTING"
        c = self.shift_cipher.encrypt(msg)
        p = self.shift_cipher.decrypt(c)
        self.assertEqual(p, msg)

    def test_frequency_analyzer(self):
        """Test frequency analysis and IoC calculations."""
        english_sample = (
            "THECONCEPTBEHINDTHISCLASSICALCIPHERCOMBINESSUBSTITUTIONANDTRANSPOSITION"
            "TOPROVIDEBOTHCONFUSIONANDDIFFUSIONINCOMPUTINGANDCOMMUNICATIONNETWORKS"
        )
        ciphertext = self.cipher.encrypt(english_sample)

        metrics = FrequencyAnalyzer.analyze(english_sample, ciphertext)
        self.assertGreater(metrics["plaintext_ioc"], metrics["ciphertext_ioc"])
        self.assertAlmostEqual(metrics["ciphertext_ioc"], 0.0385, delta=0.015)

    def test_known_plaintext_attack_full_recovery(self):
        """Verify known-plaintext attack recovers full message from partial knowledge."""
        secret_message = (
            "TOPSECRETOPERATIONCOMMENCINGATMIDNIGHTTOSECUREPRIMARY"
            "COMMUNICATIONRELAYSTATIONSTHROUGHOUTTHEENTIRENATIONALGRID"
        )
        ciphertext = self.cipher.encrypt(secret_message)
        known_prefix = secret_message[:36]  # 36 chars known (covers 2+ periods)

        attack_result = KnownPlaintextAttacker.attack(
            ciphertext=ciphertext,
            known_prefix=known_prefix,
            vigenere_key_len=len(self.vigenere_key)
        )

        self.assertTrue(attack_result["success"])
        self.assertEqual(attack_result["recovered_vigenere_key"], self.vigenere_key)
        expected_full = secret_message if len(secret_message) % 2 == 0 else secret_message + 'X'
        self.assertEqual(attack_result["recovered_full_plaintext"], expected_full)


if __name__ == "__main__":
    unittest.main()
