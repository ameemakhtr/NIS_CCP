# Network and Information Security (CT-486)
## Complex Computing Problem [CLO3]
### Design and Break a Custom Cipher Based on Classical Techniques

---

## 📌 Deliverables Overview
This repository contains the complete implementation and formal report for the CT-486 Complex Computing Problem:
1. **Custom Hybrid Cipher:** Combines Polyalphabetic Substitution (Vigenère) and Polygraphic Block Matrix (Hill Cipher) with key lengths $\ge 10$ characters.
2. **Attack Simulation:** Known-Plaintext Attack (KPA) solver and Frequency Analysis.
3. **Efficiency Benchmarking:** Time complexity analysis and empirical comparison against the classical Shift cipher.
4. **Formal Academic Report:** Publication-grade PDF report adhering strictly to assignment specifications.

---

## 📂 Project Structure

```
NIS_CCP/
│
├── custom_cipher.py                    # Custom Hybrid Cipher (Vigenere + Hill) & Shift Cipher
├── attack.py                           # Frequency analysis & Known-Plaintext Attack (KPA) solver
├── benchmark.py                        # Latency & throughput empirical benchmarking suite
├── test_suite.py                       # Automated unit tests (6/6 passing)
├── main.py                             # Interactive CLI & automated demo (python main.py --demo)
├── build_report_pdf.py                 # Standalone academic PDF report generation script
├── Complex_Computing_Problem_Report.pdf# Formal Academic PDF Report (6 pages, publication layout)
└── REPORT.md                           # Comprehensive Markdown technical report
```

---

## 🚀 Execution Commands

* **Run Automated Demonstration (Walkthrough & Benchmarks):**
  ```bash
  python main.py --demo
  ```
* **Run Unit Tests:**
  ```bash
  python test_suite.py
  ```
* **Run Performance Benchmarks:**
  ```bash
  python benchmark.py
  ```
* **Recompile Academic PDF Report:**
  ```bash
  python build_report_pdf.py
  ```
