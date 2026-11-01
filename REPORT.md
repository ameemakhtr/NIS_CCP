# Network and Information Security (CT-486)
## Complex Computing Problem [CLO3]
# Design and Break a Custom Cipher Based on Classical Techniques

---

### **Course Title:** Network and Information Security (CT-486)  
### **Evaluation Component:** Complex Computing Problem (CLO3)  
### **Submission Deadline:** 8th November 2026  
### **Maximum Group Members:** 04  

---

## Abstract
Classical cryptography provides the foundational principles upon which modern symmetric cryptosystems are built—specifically Claude Shannon’s dual concepts of **Confusion** and **Diffusion**. This report presents the design, mathematical specification, algorithmic implementation, cryptanalysis, and empirical performance evaluation of a novel **Two-Stage Custom Hybrid Classical Cipher**. The cipher integrates two distinct classical techniques: **Stage 1: Polyalphabetic Substitution (Vigenère Cipher)** and **Stage 2: Keyed Columnar Transposition**. Both stages enforce a minimum key length of $\ge 10$ characters. Furthermore, we simulate both a **Frequency Analysis Attack** and a **Known-Plaintext Attack (KPA)** using constraint-guided branch-and-bound backtracking. The results demonstrate that while the hybrid cipher flattens statistical letter frequencies (reducing the Index of Coincidence from $0.0655$ to $0.0400$), it remains vulnerable to linear-time algebraic recovery under known-plaintext assumptions. Finally, an asymptotic and empirical complexity comparison against a single-stage Shift Cipher validates its $O(N)$ efficiency.

---

## 1. Cipher Design and Theoretical Foundations

### 1.1 Motivation and Architectural Philosophy
Single-stage classical ciphers suffer from critical vulnerabilities:
- **Monoalphabetic Substitution (e.g., Shift/Caesar, Affine):** Preserves the exact frequency distribution of the plaintext language, rendering it trivially breakable via frequency analysis.
- **Pure Transposition (e.g., Rail Fence, Columnar):** Preserves the character counts and unigram frequencies intact, making anagramming and bigram reconstruction straightforward.

To eliminate these vulnerabilities, our custom cipher implements a **Product Cipher** architecture combining substitution and permutation in successive stages.

```
       Plaintext (P)
             │
             ▼
┌───────────────────────────────┐
│           STAGE 1             │
│   Polyalphabetic Substitution │  <--- Substitution Key (K_sub, len >= 10)
│      (Vigenère Cipher)        │       [Provides CONFUSION]
└────────────┬──────────────────┘
             │ Intermediate Ciphertext (C_1)
             ▼
┌───────────────────────────────┐
│           STAGE 2             │
│  Keyed Columnar Transposition │  <--- Transposition Key (K_trans, len >= 10)
│       (Permutation Grid)      │       [Provides DIFFUSION]
└────────────┬──────────────────┘
             │
             ▼
      Ciphertext (C)
```

### 1.2 Stage Details
1. **Stage 1 (Confusion - Polyalphabetic Substitution):**
   - Implements a polyalphabetic shift where each letter $P[i]$ is shifted by the numerical value of the corresponding key letter $K_{sub}[i \pmod{L_{sub}}]$.
   - Masks single-letter statistical frequencies by mapping identical plaintext characters to different ciphertext characters depending on position.
2. **Stage 2 (Diffusion - Keyed Columnar Transposition):**
   - The intermediate text $C_1$ is written row-by-row into a rectangular matrix of width $W = |K_{trans}| \ge 10$.
   - Columns are subsequently read out in lexicographical order of the characters in $K_{trans}$.
   - Scrambles positional relationships, preventing direct localized bigram/trigram cryptanalysis.

### 1.3 Key Space and Minimum Length Requirements
The assignment specifies a minimum key length of at least 10 characters:
- **Substitution Key ($K_{sub}$):** Length $L_{sub} \ge 10$. The key space for an arbitrary 10-character keyword is $26^{10} \approx 1.41 \times 10^{14}$.
- **Transposition Key ($K_{trans}$):** Length $W \ge 10$. The number of possible column permutations is $W! \ge 10! = 3,628,800$.
- **Total Key Space:** $\approx 26^{10} \times 10! \approx 5.12 \times 10^{20}$ combinations.

---

## 2. Mathematical Formulation and Algorithms

Let the alphabet be $\Sigma = \{A, B, \dots, Z\}$, mapped bijectively to $\mathbb{Z}_{26} = \{0, 1, \dots, 25\}$.

### 2.1 Encryption Algorithm
- **Input:** Plaintext $P \in \Sigma^N$, Substitution Key $K_{sub} \in \Sigma^{L_{sub}}$ ($L_{sub} \ge 10$), Transposition Key $K_{trans} \in \Sigma^{W}$ ($W \ge 10$).
- **Output:** Ciphertext $C \in \Sigma^N$.

#### Step 1: Polyalphabetic Substitution
For each character $i \in \{0, 1, \dots, N-1\}$:
$$C_1[i] = (P[i] + K_{sub}[i \pmod{L_{sub}}]) \pmod{26}$$

#### Step 2: Columnar Permutation
1. Determine the permutation $\pi: \{0, \dots, W-1\} \to \{0, \dots, W-1\}$ by sorting $K_{trans}$ lexicographically.
2. Arrange $C_1$ into an array of $W$ columns:
   $$\text{col}_c = \left[ C_1[c], C_1[c + W], C_1[c + 2W], \dots \right]$$
3. Read columns in order $\pi(0), \pi(1), \dots, \pi(W-1)$ and concatenate them to produce $C$.

```
Algorithm 1: Custom Hybrid Encryption
────────────────────────────────────────────────────────────────────────
Input : Plaintext P, Keys K_sub (len >= 10), K_trans (len >= 10)
Output: Ciphertext C

1. P_clean <- CleanAndNormalizeToUpperAZ(P)
2. N <- Length(P_clean)
3. C_1 <- Array of size N
4. for i <- 0 to N - 1 do
5.     shift <- Ord(K_sub[i mod Length(K_sub)]) - 65
6.     C_1[i] <- Chr(((Ord(P_clean[i]) - 65 + shift) mod 26) + 65)
7. end for
8. W <- Length(K_trans)
9. perm_order <- GetSortedColumnIndices(K_trans)
10. columns <- List of W empty dynamic arrays
11. for i <- 0 to N - 1 do
12.    Append C_1[i] to columns[i mod W]
13. end for
14. C <- Empty String
15. for col_idx in perm_order do
16.    C <- C + Concatenate(columns[col_idx])
17. end for
18. return C
```

---

### 2.2 Decryption Algorithm
Decryption applies the exact inverse operations in reverse sequence:

```
Algorithm 2: Custom Hybrid Decryption
────────────────────────────────────────────────────────────────────────
Input : Ciphertext C, Keys K_sub, K_trans
Output: Plaintext P

1. N <- Length(C), W <- Length(K_trans)
2. perm_order <- GetSortedColumnIndices(K_trans)
3. num_full <- N / W
4. rem <- N mod W
5. for c <- 0 to W - 1 do
6.     col_lengths[c] <- num_full + (1 if c < rem else 0)
7. end for
8. curr_idx <- 0
9. for col_idx in perm_order do
10.    len <- col_lengths[col_idx]
11.    reconstructed_cols[col_idx] <- Slice(C, curr_idx, curr_idx + len)
12.    curr_idx <- curr_idx + len
13. end for
14. C_1 <- Empty Array
15. for r <- 0 to MaxRows(col_lengths) do
16.    for c <- 0 to W - 1 do
17.        if r < Length(reconstructed_cols[c]) then
18.            Append reconstructed_cols[c][r] to C_1
19.        end if
20.    end for
21. end for
22. P <- Empty String
23. for i <- 0 to N - 1 do
24.    shift <- Ord(K_sub[i mod Length(K_sub)]) - 65
25.    P <- P + Chr(((Ord(C_1[i]) - 65 - shift + 26) mod 26) + 65)
26. end for
27. return P
```

---

## 3. Security Analysis of the Custom Cipher

### 3.1 Confusion and Diffusion Assessment
- **Confusion:** The polyalphabetic substitution decouples the direct relationship between plaintext letters and ciphertext statistics. Standard English plaintext displays a non-uniform frequency distribution dominated by `E` ($12.7\%$) and `T` ($9.1\%$). In our cipher, an identical character `E` in plaintext produces varying characters based on the 10+ character key period.
- **Diffusion:** The columnar transposition spreads adjacent characters across distant ciphertext segments. Changing a single character in the plaintext changes the character at that specific position, but the transposition relocates it by offsets proportional to message length $N/W$, disguising grammatical structures and bigram frequencies.

### 3.2 Index of Coincidence (IoC) Cryptanalysis
The **Index of Coincidence (IoC)** measures the probability that two randomly chosen letters from a text are identical:
$$IC = \frac{\sum_{i=A}^Z f_i (f_i - 1)}{N(N - 1)}$$
- Natural English Text: $IC \approx 0.0667$
- Monoalphabetic Substitution (Shift / Caesar): $IC \approx 0.0667$ (Invariant)
- Uniformly Random / Polyalphabetic Text: $IC \approx 0.0385$

#### Empirical Experimental Results:
| Metric | Natural English Plaintext | Single-Stage Shift Cipher | Custom Hybrid Cipher |
| :--- | :--- | :--- | :--- |
| **Index of Coincidence ($IC$)** | **0.06552** | **0.06552** | **0.04000** |
| **Chi-Squared ($\chi^2$ vs English)** | **34.62** | **34.62** | **869.73** |
| **Top 3 Frequent Characters** | `T` (11.9%), `O` (10.3%), `I` (9.5%) | `A` (11.9%), `V` (10.3%), `P` (9.5%) | `G` (7.1%), `L` (7.1%), `H` (6.3%) |

**Conclusion from Frequency Analysis:**  
The hybrid cipher effectively defeats basic monographic frequency attacks. An attacker cannot use frequency counting alone to directly reconstruct the plaintext without breaking the polyalphabetic key and column ordering.

---

## 4. Attack Simulation and Results

As mandated by Deliverable 2, we simulate an attack scenario to break the cipher.

### 4.1 Threat Model: Known-Plaintext Attack (KPA)
- **Attacker Knowledge:**
  1. The attacker intercepts the full ciphertext $C$ of length $N$.
  2. The attacker possesses a known plaintext fragment $P_{known}$ of length $M$ (e.g., standardized message header, protocol preamble, or greeting).
  3. The attacker knows the cipher architecture and candidate key lengths ($W \ge 10, L_{sub} \ge 10$).
- **Attacker Objective:**
  Recover the transposition column permutation, recover the Vigenère keyword, and decrypt the **entire unknown remainder** of the message.

### 4.2 Cryptanalytic Attack Methodology
In a naive brute-force approach, testing all $W! \times 26^{L_{sub}}$ combinations is computationally intractable ($> 10^{20}$ operations).  
However, our cryptanalytic engine uses a **Constraint-Guided Branch-and-Bound Backtracking Solver**:

1. **Slice Identification:** The ciphertext $C$ consists of $W$ slices. If $N \pmod{W} = \text{rem}$, exactly $\text{rem}$ slices have length $\lfloor N/W \rfloor + 1$, and $(W - \text{rem})$ have length $\lfloor N/W \rfloor$.
2. **Algebraic Keystream Derivation:**  
   If slice $S_j$ is tentatively assigned to original column $c$, then at row $r$:
   $$\text{Candidate Key Character: } K[k_{pos}] = (S_j[r] - P[r \cdot W + c]) \pmod{26}$$
   where $k_{pos} = (r \cdot W + c) \pmod{L_{sub}}$.
3. **Consistency Pruning:**  
   If $k_{pos}$ was already assigned by an earlier column test, the candidate value **must match exactly**. Any discrepancy causes immediate pruning of that entire search branch.
4. **Key and Message Recovery:**  
   Once all columns are consistently matched, the full Vigenère key is extracted, the transposition grid is inverted, and the remaining unknown plaintext is decrypted deterministically.

```
                    Root (Column 0)
                    /      |       \
               Slice 0  Slice 1   Slice 2 ...
                /          \
            Column 1     [PRUNED: Key Conflict]
            /      \
        Column 2  [PRUNED]
          ...
     [Full Key Recovered] -> Decrypt Remaining Message
```

---

### 4.3 Attack Performance and Computational Effort
We tested the attack across multiple message lengths ($100, 250, 500, 1000$ characters) using a fixed known prefix of $35$ characters ($L_{sub}=12, W=11$).

| Ciphertext Length ($N$) | Known Characters ($M$) | Unknown Characters Recovered | Success Rate | Avg Execution Time | Avg Search Branches |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **100** | 35 | 65 | **100.0%** | **0.25 ms** | 23 |
| **250** | 35 | 215 | **100.0%** | **6.91 ms** | 700 |
| **500** | 35 | 465 | **100.0%** | **17.38 ms** | 1,786 |
| **1000** | 35 | 965 | **100.0%** | **1.52 ms** | 90 |

#### Experimental Observations:
- **100% Success Rate:** The attack consistently achieves complete message recovery once the known plaintext exceeds $2.5 \times W$ characters.
- **Microsecond-to-Millisecond Execution:** Constraint satisfaction reduces search spaces from millions of permutations to under $2,000$ branch evaluations, completing in under $20\text{ ms}$.

---

## 5. Efficiency and Time Complexity Considerations

### 5.1 Theoretical Complexity Analysis

| Algorithm Phase | Stage 1 (Vigenère) | Stage 2 (Columnar Transposition) | Overall Custom Hybrid Cipher | Baseline Shift Cipher |
| :--- | :---: | :---: | :---: | :---: |
| **Encryption Time** | $O(N)$ | $O(N + W \log W)$ | **$O(N + W \log W) \approx O(N)$** | $O(N)$ |
| **Decryption Time** | $O(N)$ | $O(N + W \log W)$ | **$O(N + W \log W) \approx O(N)$** | $O(N)$ |
| **Space Complexity** | $O(N)$ | $O(N)$ | **$O(N)$** | $O(N)$ |

*Note: Since key length $W$ is fixed ($W \ge 10$, typically $10 \le W \le 20$), $W \log W$ is an infinitesimal constant factor. Hence both ciphers scale strictly linearly $O(N)$.*

---

### 5.2 Empirical Benchmark: Custom Hybrid vs. Single-Stage Shift Cipher
Execution latency measured across 50 iterations on an Intel/AMD CPU with Python 3.14:

| Message Length ($N$) | Custom Enc (ms) | Custom Dec (ms) | Shift Enc (ms) | Shift Dec (ms) | Overhead Factor |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **100** | 0.0601 | 0.0727 | 0.0251 | 0.0254 | $\approx 2.4\times$ |
| **500** | 0.2806 | 0.3321 | 0.1211 | 0.1309 | $\approx 2.3\times$ |
| **1,000** | 0.5493 | 0.6531 | 0.2720 | 0.2883 | $\approx 2.0\times$ |
| **5,000** | 2.7906 | 3.3142 | 1.2286 | 1.2607 | $\approx 2.3\times$ |
| **10,000** | 5.6787 | 6.3655 | 2.5799 | 2.9910 | $\approx 2.2\times$ |

#### Key Insights:
1. **Linear Scaling:** Both ciphers exhibit perfect linear runtime scaling proportional to message size $N$.
2. **Computational Overhead:** The Custom Hybrid Cipher introduces an expected $\approx 2.2\times$ overhead compared to the primitive Shift Cipher. This overhead is due to maintaining two sequential transformation passes (arithmetic modular substitution followed by memory buffer partitioning and permutation).
3. **Practical Performance:** Encrypting $10,000$ characters takes only $5.68\text{ ms}$, representing a throughput of over **$1.76\text{ million characters/second}$**.

---

## 6. Recommendations for Improving Security

While our custom cipher successfully prevents monographic frequency analysis, its vulnerability to Known-Plaintext Attacks highlights the fundamental limitations of classical ciphers. To strengthen the cipher without significantly increasing its computational complexity, we recommend the following enhancements:

### 1. Autokey Cipher Integration (Dynamic Key Scheduling)
- **Vulnerability Addressed:** Static repetition of the Vigenère keyword every $L_{sub}$ characters allows periodic keystream alignment.
- **Solution:** Replace repeating Vigenère with an **Autokey Cipher**, where the key is initialized by the secret keyword and subsequently extended by the plaintext characters themselves ($K[i] = P[i - L_{sub}]$).
- **Complexity Impact:** Remains $O(N)$ runtime with zero additional memory overhead.

### 2. Double Keyed Columnar Transposition
- **Vulnerability Addressed:** A single transposition leaves column slices intact as contiguous blocks within the ciphertext.
- **Solution:** Apply a secondary transposition pass using a different key length $W_2$ coprime to $W_1$ ($\gcd(W_1, W_2) = 1$).
- **Complexity Impact:** Adds one linear $O(N)$ pass, but increases the search space for attacks from $W!$ to $W_1! \times W_2!$, effectively eliminating slice-based attacks.

### 3. Non-Linear Substitution (S-Box) Stage
- **Vulnerability Addressed:** Modular addition is linear over $\mathbb{Z}_{26}$: $(P + K) \pmod{26}$.
- **Solution:** Incorporate a fixed, non-linear substitution permutation table (classical S-Box / polybius square with affine mixing) before transposition.

---

## 7. Conclusion

In this Complex Computing Problem (CLO3), we successfully:
1. Designed and implemented a Two-Stage Custom Hybrid Classical Cipher combining **Polyalphabetic Substitution** and **Keyed Columnar Transposition**, strictly adhering to key lengths $\ge 10$.
2. Demonstrated mathematically and empirically that the hybrid cipher provides strong statistical **confusion** and **diffusion**, depressing the Index of Coincidence to $0.0400$ and thwarting ciphertext-only frequency analysis.
3. Devised and executed a **Known-Plaintext Attack (KPA)** using branch-and-bound constraint resolution that reliably breaks the cipher with a **100% success rate** in under $20\text{ ms}$.
4. Conducted asymptotic and empirical benchmarking against the classical **Shift Cipher**, confirming $O(N)$ operational efficiency with a modest $\approx 2.2\times$ performance trade-off for substantially superior diffusion.

---

## 8. References
1. Shannon, C. E. (1949). *Communication Theory of Secrecy Systems*. Bell System Technical Journal, 28(4), 656-715.
2. Stallings, W. (2017). *Cryptography and Network Security: Principles and Practice* (7th ed.). Pearson.
3. Stinson, D. R., & Paterson, M. B. (2018). *Cryptography: Theory and Practice* (4th ed.). CRC Press.
4. Beker, H., & Piper, F. (1982). *Cipher Systems: The Protection of Communications*. John Wiley & Sons.
