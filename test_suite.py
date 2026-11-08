"""
Comprehensive Test Suite for Vigenere + Hill Hybrid Classical Cipher
Course: Network and Information Security (CT-486) - Dr. Shariq Mahmood Khan
Complex Computing Problem [CLO3]
"""

import unittest
import server
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
            ciphertext = self.cipher.encrypt(msg)
            decrypted = self.cipher.decrypt(ciphertext)
            self.assertEqual(decrypted, cleaned, f"Failed round-trip for message: {msg[:20]}...")

    def test_padding_is_unambiguous(self):
        """Messages that look like padding must still decrypt exactly."""
        for msg in ["A", "X", "AX", "XX", "XA", "FOX", "FOXX", "TAXA", "XAX", "XAXA", "ZZZ"]:
            self.assertEqual(self.cipher.decrypt(self.cipher.encrypt(msg)), msg)
        self.assertEqual(self.cipher.encrypt(""), "")
        self.assertEqual(self.cipher.decrypt(""), "")

    def test_all_letters_roundtrip(self):
        """Every letter A-Z survives at every prefix length."""
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for n in range(1, 27):
            self.assertEqual(self.cipher.decrypt(self.cipher.encrypt(alphabet[:n])), alphabet[:n])

    def test_non_ascii_letters_are_dropped(self):
        """Only A-Z is in the alphabet; other letters must not corrupt the message."""
        self.assertEqual(clean_text("caf\u00e9 \u0645 au"), "CAFAU")

    def test_odd_ciphertext_rejected(self):
        with self.assertRaises(ValueError):
            self.cipher.decrypt("ABC")

    def test_every_hill_key_letter_matters(self):
        """The full >=10 character Hill phrase feeds the matrix, not just its prefix."""
        one = CustomHybridCipher(self.vigenere_key, "HILLCIPHERKEY").hill_mat
        other = CustomHybridCipher(self.vigenere_key, "HILLCIPHERKEZ").hill_mat
        self.assertNotEqual(one, other)

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
        self.assertEqual(attack_result["recovered_full_plaintext"], secret_message)

    def test_attack_finds_unknown_key_length(self):
        """The attacker is not told the key length and must find it."""
        message = "ATTACKTHEEASTERNRELAYATDAWNANDHOLDUNTILRELIEFARRIVESFROMTHESOUTH" * 3
        result = KnownPlaintextAttacker.attack(self.cipher.encrypt(message), message[:40])
        self.assertTrue(result["success"])
        self.assertEqual(result["recovered_key_len"], len(self.vigenere_key))
        self.assertEqual(result["recovered_full_plaintext"], message)

    def test_attack_refuses_too_little_known_text(self):
        """Without redundancy a match would be coincidence, so report failure."""
        message = "ATTACKTHEEASTERNRELAYATDAWNANDHOLDUNTILRELIEFARRIVES"
        ciphertext = self.cipher.encrypt(message)
        for known in (4, 10, 16):
            self.assertFalse(KnownPlaintextAttacker.attack(ciphertext, message[:known])["success"])


class TestWebApi(unittest.TestCase):
    KEYS = {"vigenere_key": "CONFIDENTIALKEY", "hill_key": "HILLCIPHERKEY"}

    def test_encrypt_decrypt_attack_flow(self):
        """The UI's three calls agree with each other on a user-style message."""
        message = "Hold the northern bridge until the convoy has crossed, then fall back."
        sent = server.encrypt({**self.KEYS, "plaintext": message})
        self.assertEqual(sent["decrypted"], clean_text(message))
        self.assertEqual(server.decrypt({**self.KEYS, "ciphertext": sent["ciphertext"]})["plaintext"], clean_text(message))

        broken = server.attack({"ciphertext": sent["ciphertext"], "known_plaintext": sent["plaintext"][:36]})
        self.assertTrue(broken["success"])
        self.assertEqual(broken["recovered_vigenere_key"], self.KEYS["vigenere_key"])
        self.assertEqual(broken["recovered_full_plaintext"], clean_text(message))

    def test_bad_input_is_rejected_cleanly(self):
        bad_calls = [
            (server.encrypt, {**self.KEYS, "plaintext": "12345"}),
            (server.encrypt, {**self.KEYS, "plaintext": 7}),
            (server.encrypt, {"vigenere_key": "SHORT", "hill_key": "HILLCIPHERKEY", "plaintext": "HI"}),
            (server.decrypt, {**self.KEYS, "ciphertext": "ABC"}),
            (server.attack, {"ciphertext": "ABC", "known_plaintext": "A"}),
            (server.attack, {"ciphertext": "ABCD", "known_plaintext": "ABCDEF"}),
            (server.attack, {"ciphertext": "ABCD", "known_plaintext": ""}),
        ]
        for route, data in bad_calls:
            with self.assertRaises(ValueError):
                route(data)


if __name__ == "__main__":
    unittest.main()
