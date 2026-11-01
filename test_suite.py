"""
Comprehensive Test Suite for Custom Hybrid Classical Cipher
Course: Network and Information Security (CT-486)
CLO: Complex Computing Problem [CLO3]
"""

import unittest
from custom_cipher import CustomHybridCipher, ShiftCipher, clean_text
from attack import FrequencyAnalyzer, KnownPlaintextAttacker


class TestCustomCipher(unittest.TestCase):

    def setUp(self):
        self.sub_key = "CONFIDENTIAL"   # len 12 >= 10
        self.trans_key = "ALGORITHMIC"   # len 11 >= 10
        self.cipher = CustomHybridCipher(self.sub_key, self.trans_key)
        self.shift_cipher = ShiftCipher(shift=7)

    def test_key_length_validation(self):
        """Verify enforcement of key length >= 10 characters."""
        with self.assertRaises(ValueError):
            CustomHybridCipher("SHORT", "ALGORITHMIC")

        with self.assertRaises(ValueError):
            CustomHybridCipher("CONFIDENTIAL", "TINY")

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
            "SECRET",                               # very short (< key len)
            "CONFIDENTIALDATA",                     # medium
            "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG",  # standard pangram
            "A" * 150,                              # repetitive sequence
            "NETWORKSECURITYANDINFORMATIONASSURANCE" * 10  # long message (380 chars)
        ]

        for msg in test_messages:
            cleaned = clean_text(msg)
            ciphertext = self.cipher.encrypt(msg)
            decrypted = self.cipher.decrypt(ciphertext)
            self.assertEqual(decrypted, cleaned, f"Failed round-trip for message: {msg[:20]}...")

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
        known_prefix = secret_message[:35]  # first 35 chars known

        attack_result = KnownPlaintextAttacker.attack(
            ciphertext=ciphertext,
            known_prefix=known_prefix,
            trans_key_len=len(self.trans_key),
            sub_key_len=len(self.sub_key)
        )

        self.assertTrue(attack_result["success"])
        self.assertEqual(attack_result["recovered_sub_key"], self.sub_key)
        self.assertEqual(attack_result["recovered_full_plaintext"], secret_message)


if __name__ == "__main__":
    unittest.main()
