"""
Local web server for the React UI: a thin JSON layer over custom_cipher.py and attack.py.
All cryptography stays in those files; the browser only displays what they return.

Run with: python server.py   (build the UI first, see README)
"""

import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from attack import ENGLISH_FREQ, FrequencyAnalyzer, KnownPlaintextAttacker
from custom_cipher import CustomHybridCipher, add_padding, clean_text

HERE = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(HERE, "ui", "dist")
RESULTS_PATH = os.path.join(HERE, "results.json")
PORT = 8000
MAX_BODY_BYTES = 1_000_000


def text_field(data: dict, name: str) -> str:
    value = data.get(name)
    if not isinstance(value, str):
        raise ValueError(f"'{name}' must be text.")
    return value


def build_cipher(data: dict) -> CustomHybridCipher:
    return CustomHybridCipher(text_field(data, "vigenere_key"), text_field(data, "hill_key"))


def as_matrix(values) -> list:
    return [list(values[:2]), list(values[2:])]


def encrypt(data: dict) -> dict:
    cipher = build_cipher(data)
    plaintext = clean_text(text_field(data, "plaintext"))
    if not plaintext:
        raise ValueError("Enter a message with at least one letter A-Z.")

    padded = add_padding(plaintext)
    ciphertext = cipher.encrypt(plaintext)
    return {
        "plaintext": plaintext,
        "padded": padded,
        "after_vigenere": "".join(chr(n + 65) for n in cipher._vigenere_encrypt(padded)),
        "ciphertext": ciphertext,
        "decrypted": cipher.decrypt(ciphertext),
        "vigenere_key": cipher.vigenere_key,
        "hill_matrix": as_matrix(cipher.hill_mat),
        "hill_inverse": as_matrix(cipher.hill_inv),
        "stats": FrequencyAnalyzer.analyze(plaintext, ciphertext),
        "frequencies": {
            "plaintext": FrequencyAnalyzer.calculate_frequencies(plaintext),
            "ciphertext": FrequencyAnalyzer.calculate_frequencies(ciphertext),
            "english": ENGLISH_FREQ,
        },
    }


def decrypt(data: dict) -> dict:
    ciphertext = clean_text(text_field(data, "ciphertext"))
    if not ciphertext:
        raise ValueError("Enter a ciphertext to decrypt.")
    return {"plaintext": build_cipher(data).decrypt(ciphertext)}


def attack(data: dict) -> dict:
    ciphertext = clean_text(text_field(data, "ciphertext"))
    known = clean_text(text_field(data, "known_plaintext"))
    if not ciphertext or len(ciphertext) % 2:
        raise ValueError("The ciphertext must have an even number of letters.")
    if not known:
        raise ValueError("Enter the plaintext the attacker already knows.")
    if len(known) > len(ciphertext):
        raise ValueError("Known plaintext cannot be longer than the ciphertext.")

    result = KnownPlaintextAttacker.attack(ciphertext, known)
    result["known_letters"] = len(known)
    return result


ROUTES = {"/api/encrypt": encrypt, "/api/decrypt": decrypt, "/api/attack": attack}


class Handler(SimpleHTTPRequestHandler):
    # Windows can map .js to text/plain in the registry, which browsers refuse for modules
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".js": "text/javascript", ".css": "text/css"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def send_json(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/api/results":
            return super().do_GET()
        with open(RESULTS_PATH, "rb") as handle:
            self.send_json(200, handle.read())

    def do_POST(self):
        route = ROUTES.get(self.path)
        if route is None:
            return self.send_json(404, b'{"error": "Unknown endpoint."}')
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length > MAX_BODY_BYTES:
                raise ValueError("Input is too long (limit is 1 MB).")
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object.")
            payload = route(data)
        except ValueError as error:
            return self.send_json(400, json.dumps({"error": str(error)}).encode())
        self.send_json(200, json.dumps(payload).encode())


if __name__ == "__main__":
    if not os.path.isdir(UI_DIR):
        print("UI not built yet. Run: cd ui && npm install && npm run build")
    # Local only: this is a course demo, so it is not exposed to the network
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Open http://127.0.0.1:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
