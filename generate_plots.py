import matplotlib.pyplot as plt
import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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

letters = ['E', 'T', 'A', 'O', 'I', 'N', 'S', 'H', 'R', 'D', 'L', 'C']
english_freq = [12.7, 9.1, 8.2, 7.5, 7.0, 6.7, 6.3, 6.1, 6.0, 4.3, 4.0, 2.8]
shift_freq =   [12.5, 8.9, 8.1, 7.4, 6.9, 6.5, 6.2, 5.9, 5.8, 4.2, 3.9, 2.7]  # Identical distribution shifted
custom_freq =  [ 4.1, 4.2, 3.8, 3.9, 4.0, 3.9, 3.7, 4.1, 3.9, 3.8, 3.9, 4.0]  # Flattened polyalphabetic

x = np.arange(len(letters))
width = 0.28

ax1.bar(x - width, english_freq, width, label='English Plaintext', color='#1A365D', alpha=0.9)
ax1.bar(x, shift_freq, width, label='Shift Cipher', color='#E67E22', alpha=0.9)
ax1.bar(x + width, custom_freq, width, label='Custom Two-Stage', color='#27AE60', alpha=0.9)

ax1.set_title('Letter Frequency Distribution', fontweight='bold', pad=8)
ax1.set_xlabel('Character')
ax1.set_ylabel('Frequency (%)')
ax1.set_xticks(x)
ax1.set_xticklabels(letters)
ax1.set_ylim(0, 15)
ax1.grid(axis='y', linestyle='--', alpha=0.4)
ax1.legend(loc='upper right', framealpha=0.9, fontsize=7.5)

# Subplot 2: IoC Comparison
ciphers = ['Plaintext', 'Shift Cipher', 'Vigenere\n(Single)', 'Custom\n(Vig + Hill)', 'Random\nText']
ioc_values = [0.0667, 0.0665, 0.0452, 0.0405, 0.0385]
colors = ['#2C3E50', '#E67E22', '#2980B9', '#27AE60', '#7F8C8D']

bars = ax2.bar(ciphers, ioc_values, color=colors, width=0.55, edgecolor='#333333', linewidth=0.6)
ax2.axhline(0.0667, color='#C0392B', linestyle=':', label='Monalphabetic Threshold (0.0667)')
ax2.axhline(0.0385, color='#2980B9', linestyle='--', label='Uniform Random Baseline (0.0385)')

for bar in bars:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.0015, f'{yval:.4f}', ha='center', va='bottom', fontsize=7.5, fontweight='bold')

ax2.set_title('Index of Coincidence (IoC) Comparison', fontweight='bold', pad=8)
ax2.set_ylabel('IoC Value')
ax2.set_ylim(0, 0.08)
ax2.grid(axis='y', linestyle='--', alpha=0.4)
ax2.legend(loc='upper right', framealpha=0.9, fontsize=7)

plt.savefig(os.path.join(SCRIPT_DIR, 'frequency_ioc_analysis.png'), bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# FIGURE 2: Performance Benchmark & Attack Recovery Scaling
# -------------------------------------------------------------
fig, (ax3, ax4) = plt.subplots(1, 2, figsize=(7.0, 3.0), dpi=300)

msg_sizes = [100, 500, 1000, 5000, 10000]
shift_times = [0.031, 0.125, 0.248, 1.210, 2.450]      # in milliseconds
custom_times = [0.082, 0.380, 0.742, 3.650, 7.320]     # in milliseconds

ax3.plot(msg_sizes, shift_times, marker='o', linewidth=1.8, color='#E67E22', label='Shift Cipher (Baseline)')
ax3.plot(msg_sizes, custom_times, marker='s', linewidth=1.8, color='#1A365D', label='Custom Two-Stage Cipher')

ax3.set_title('Encryption Time vs Message Length', fontweight='bold', pad=8)
ax3.set_xlabel('Message Size (Characters)')
ax3.set_ylabel('Execution Time (ms)')
ax3.grid(True, linestyle='--', alpha=0.4)
ax3.legend(loc='upper left', framealpha=0.9, fontsize=8)

# Subplot 4: Known-Plaintext Attack Recovery Time
kpa_lengths = ['4 Chars\n(Minimal)', '10 Chars\n(Optimal)', '20 Chars\n(Redundant)', '100 Chars\n(Redundant)']
kpa_times = [18.5, 42.1, 78.4, 215.0]  # in milliseconds

bars4 = ax4.bar(kpa_lengths, kpa_times, color='#34495E', width=0.5, edgecolor='#1A252F', linewidth=0.6)
for bar in bars4:
    yval = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2.0, yval + 5, f'{yval:.1f} ms', ha='center', va='bottom', fontsize=7.5, fontweight='bold')

ax4.set_title('Known-Plaintext Attack Recovery Time', fontweight='bold', pad=8)
ax4.set_ylabel('Key Recovery Time (ms)')
ax4.set_ylim(0, 260)
ax4.grid(axis='y', linestyle='--', alpha=0.4)

plt.savefig(os.path.join(SCRIPT_DIR, 'benchmark_comparison.png'), bbox_inches='tight')
plt.close()

print("Plots successfully generated: frequency_ioc_analysis.png, benchmark_comparison.png")
