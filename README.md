# Network and Information Security (CT-486)
## Complex Computing Problem [CLO3]
### Design and Break a Custom Cipher Based on Classical Techniques

---

## 📌 Deliverables Overview
This repository contains the complete implementation and report for the CT-486 Complex Computing Problem:
1. **Custom Hybrid Cipher:** Combines Polyalphabetic Substitution (Vigenère) and Polygraphic Block Matrix (Hill Cipher) with key lengths $\ge 10$ characters.
2. **Attack Simulation:** Known-Plaintext Attack (KPA) solver and Frequency Analysis.
3. **Efficiency Benchmarking:** Time complexity analysis and empirical comparison against the classical Shift cipher.

---

## 📂 Project Structure

```
NIS_CCP/
│
├── custom_cipher.py    # Custom Hybrid Cipher (Vigenere + Hill) & Shift Cipher
├── attack.py           # Frequency analysis & Known-Plaintext Attack (KPA) solver
├── benchmark.py        # Latency & throughput benchmarking suite
├── test_suite.py       # Automated unit tests
├── live_test.py        # Live custom encryption and attack demonstration
├── main.py             # Interactive CLI & automated demo (python main.py --demo)
└── REPORT.md           # Required Security and Efficiency Report
```

---

## 🚀 Execution Commands

* **Run Automated Demonstration (Walkthrough & Benchmarks):**
  ```bash
  python main.py --demo
  ```
* **Run Custom Live Attack Test:**
  ```bash
  python live_test.py
  ```
* **Run Unit Tests:**
  ```bash
  python test_suite.py
  ```
* **Run Performance Benchmarks:**
  ```bash
  python benchmark.py
  ```
