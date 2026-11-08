"""Draws the report figures from results.json (run benchmark.py first). Holds no data of its own."""
import json
import os

import matplotlib.pyplot as plt
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(SCRIPT_DIR, 'results.json'), encoding='utf-8') as handle:
    results = json.load(handle)

# Set professional academic styling
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 9
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['axes.labelsize'] = 9
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['figure.autolayout'] = True

# -------------------------------------------------------------
# FIGURE 1: Frequency & Index of Coincidence (IoC) Analysis
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 3.0), dpi=300)

freq = results['frequency']
ranks = np.arange(1, 27)
ax1.plot(ranks, freq['english_ranked_freq'], color='#1A365D', marker='o', markersize=3, linewidth=1.5, label='Expected English')
ax1.plot(ranks, freq['ciphers']['Shift']['ranked_freq'], color='#E67E22', linestyle='--', marker='^', markersize=3, linewidth=1.2, label='Shift ciphertext')
ax1.plot(ranks, freq['ciphers']['Custom']['ranked_freq'], color='#27AE60', marker='s', markersize=3, linewidth=1.5, label='Custom ciphertext')
ax1.axhline(100 / 26, color='#7F8C8D', linestyle=':', label='Uniform (3.85%)')
ax1.set_title('Letter Frequency, Most to Least Common', fontweight='bold', pad=8)
ax1.set_xlabel('Frequency rank')
ax1.set_ylabel('Frequency (%)')
ax1.set_ylim(0, 15)
ax1.grid(axis='y', linestyle='--', alpha=0.4)
ax1.legend(loc='upper right', framealpha=0.9, fontsize=7.5)

# Subplot 2: IoC Comparison
names = ['Plaintext', 'Shift', 'Hill only', 'Vigenere only', 'Custom']
labels = ['Plaintext', 'Shift', 'Hill\nonly', 'Vigenere\nonly', 'Custom\n(Vig + Hill)']
ioc_values = [freq['ciphers'][name]['ioc'] for name in names]
colors = ['#2C3E50', '#E67E22', '#8E44AD', '#2980B9', '#27AE60']

bars = ax2.bar(labels, ioc_values, color=colors, width=0.55, edgecolor='#333333', linewidth=0.6)
ax2.axhline(1 / 26, color='#7F8C8D', linestyle=':', label='Uniform random (0.0385)')

for bar in bars:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.0015, f'{yval:.4f}', ha='center', va='bottom', fontsize=7.5, fontweight='bold')

ax2.set_title('Measured Index of Coincidence', fontweight='bold', pad=8)
ax2.set_ylabel('IoC')
ax2.set_ylim(0, 0.085)
ax2.grid(axis='y', linestyle='--', alpha=0.4)
ax2.legend(loc='upper right', framealpha=0.9, fontsize=7)

plt.savefig(os.path.join(SCRIPT_DIR, 'frequency_ioc_analysis.png'), bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# FIGURE 2: Performance Benchmark & Attack Recovery Scaling
# -------------------------------------------------------------
fig, (ax3, ax4) = plt.subplots(1, 2, figsize=(7.0, 3.0), dpi=300)

rows = results['ciphers']
sizes = [row['length'] for row in rows]
ax3.plot(sizes, [row['custom_enc_ms'] for row in rows], marker='s', linewidth=1.8, color='#1A365D', label='Custom encrypt')
ax3.plot(sizes, [row['custom_dec_ms'] for row in rows], marker='D', markersize=3.5, linewidth=1.0, linestyle='--', color='#27AE60', label='Custom decrypt')
ax3.plot(sizes, [row['shift_enc_ms'] for row in rows], marker='o', linewidth=1.8, color='#E67E22', label='Shift encrypt')
ax3.set_title('Cipher Time vs Message Length', fontweight='bold', pad=8)
ax3.set_xlabel('Message size (letters)')
ax3.set_ylabel('Time (ms)')
ax3.grid(True, linestyle='--', alpha=0.4)
ax3.legend(loc='upper left', framealpha=0.9, fontsize=8)

# Subplot 4: attack success against amount of known plaintext
known_rows = results['attack']['by_known']
positions = np.arange(len(known_rows))
ax4.bar(positions, [row['success_rate'] for row in known_rows], color='#34495E', width=0.55, edgecolor='#1A252F', linewidth=0.6)
for position, row in zip(positions, known_rows):
    ax4.text(position, row['success_rate'] + 2, f"{row['success_rate']:.0f}%", ha='center', va='bottom', fontsize=7.5, fontweight='bold')
ax4.set_xticks(positions)
ax4.set_xticklabels([row['known_chars'] for row in known_rows])
ax4.set_title('Attack Success vs Known Plaintext', fontweight='bold', pad=8)
ax4.set_xlabel('Known letters (key length 10-20, unknown)')
ax4.set_ylabel('Exact recovery (%)')
ax4.set_ylim(0, 115)
ax4.grid(axis='y', linestyle='--', alpha=0.4)

plt.savefig(os.path.join(SCRIPT_DIR, 'benchmark_comparison.png'), bbox_inches='tight')
plt.close()

print("Plots successfully generated: frequency_ioc_analysis.png, benchmark_comparison.png")
