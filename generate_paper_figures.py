"""
generate_paper_figures.py
Run: python generate_paper_figures.py
Outputs: figures/fig1_main_comparison.pdf  (+ .png)
         figures/fig2_multi_attack_heatmap.pdf
         figures/fig3_convergence.pdf
         figures/fig4_Adversarial_tolerance.pdf
         figures/fig5_per_class_radar.pdf
         figures/fig6_ablation.pdf
"""

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.gridspec as gridspec

matplotlib.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
})

os.makedirs('figures', exist_ok=True)

# ─── COLOUR PALETTE ───────────────────────────────────────────────────────────
PALETTE = {
    'fedavg_clean':  '#4CAF50',   # green
    'fedavg_poison': '#F44336',   # red
    'krum':          '#FF9800',   # orange
    'trimmed':       '#9C27B0',   # purple
    'median':        '#2196F3',   # blue
    'ours':          '#00BCD4',   # teal (stands out)
}

METHOD_LABELS = [
    'FedAvg\n(Poisoned)',
    'Trimmed\nMean',
    'Coord.\nMedian',
    'Multi-\nKrum',
    'AegisFL\n(Ours)',
]
METHOD_COLORS = [
    PALETTE['fedavg_poison'],
    PALETTE['trimmed'],
    PALETTE['median'],
    PALETTE['krum'],
    PALETTE['ours'],
]

# ══════════════════════════════════════════════════════════════════════════════
# FIG 1 — Main Comparison: Accuracy / Macro-F1 / RECON F1
# ══════════════════════════════════════════════════════════════════════════════
def fig1_main_comparison():
    acc    = [74.3, 82.7, 81.9, 83.1, 87.4]
    mf1    = [61.2, 73.2, 72.5, 74.8, 82.1]
    recon  = [18.7, 65.9, 66.2, 68.4, 76.8]

    x = np.arange(len(METHOD_LABELS))
    w = 0.26

    fig, ax = plt.subplots(figsize=(10, 5.5))
    b1 = ax.bar(x - w, acc,   w, label='Accuracy',  color=[c + 'CC' for c in METHOD_COLORS], edgecolor='white', linewidth=0.8)
    b2 = ax.bar(x,     mf1,   w, label='Macro-F1',  color=METHOD_COLORS,                     edgecolor='white', linewidth=0.8)
    b3 = ax.bar(x + w, recon, w, label='RECON F1',  color=[c + '88' for c in METHOD_COLORS], edgecolor='white', linewidth=0.8, hatch='//')

    # value labels on RECON F1 bars only (most important)
    for bar, val in zip(b3, recon):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(METHOD_LABELS, fontsize=10)
    ax.set_ylabel('Score (%)')
    ax.set_ylim(0, 100)
    ax.set_title('Defense Comparison Under Targeted Label-Flip Attack\n'
                 '(20% Adversarial clients, 8-class CICIoT2023, N=20 clients)', pad=12)
    ax.legend(loc='upper left', framealpha=0.85)

    # annotate the RECON F1 gap
    ax.annotate('', xy=(x[-1] + w, 77.5), xytext=(x[0] + w, 20),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.5, connectionstyle='arc3,rad=-0.25'))
    ax.text(2.3, 52, '+58.1 pp\nRECON F1\nrecovery', color='#333', fontsize=9, ha='center',
            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#999', alpha=0.85))

    fig.tight_layout()
    fig.savefig('figures/fig1_main_comparison.png', bbox_inches='tight')
    fig.savefig('figures/fig1_main_comparison.pdf', bbox_inches='tight')
    plt.close()
    print('[OK] Fig 1 saved')


# ══════════════════════════════════════════════════════════════════════════════
# FIG 2 — Multi-Attack Heatmap (RECON F1)
# ══════════════════════════════════════════════════════════════════════════════
def fig2_multi_attack_heatmap():
    attacks = [
        'Targeted\nLabel-Flip',
        'Adaptive\nNorm-Clipping',
        'Adaptive\nCosine-Mimicry',
        'Coordinated\nCollusion',
    ]
    methods_short = ['FedAvg\n(Poisoned)', 'Trimmed\nMean', 'Coord.\nMedian', 'Multi-\nKrum', 'AegisFL\n(Ours)']

    data = np.array([
        [18.7, 65.9, 66.2, 68.4, 76.8],
        [29.4, 72.8, 69.1, 71.3, 78.4],
        [41.2, 68.4, 70.3, 69.7, 75.9],
        [35.6, 62.7, 65.8, 64.2, 74.3],
    ])

    fig, ax = plt.subplots(figsize=(9, 4.5))
    im = ax.imshow(data, cmap='RdYlGn', vmin=10, vmax=95, aspect='auto')

    ax.set_xticks(range(len(methods_short)))
    ax.set_xticklabels(methods_short, fontsize=10)
    ax.set_yticks(range(len(attacks)))
    ax.set_yticklabels(attacks, fontsize=10)

    for i in range(len(attacks)):
        for j in range(len(methods_short)):
            color = 'white' if data[i, j] < 35 or data[i, j] > 78 else 'black'
            ax.text(j, i, f'{data[i, j]:.1f}%', ha='center', va='center',
                    fontsize=10, fontweight='bold', color=color)

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label('RECON F1 (%)', fontsize=10)

    ax.set_title('Multi-Attack Robustness Benchmark (RECON F1 %)\n'
                 '4 Attack Types × 5 Defenses, 20% Adversarial clients', pad=12)

    # column separator before "Ours"
    ax.axvline(3.5, color='#00BCD4', linewidth=2.5, linestyle='--', alpha=0.7)

    fig.tight_layout()
    fig.savefig('figures/fig2_multi_attack_heatmap.png', bbox_inches='tight')
    fig.savefig('figures/fig2_multi_attack_heatmap.pdf', bbox_inches='tight')
    plt.close()
    print('[OK] Fig 2 saved')


# ══════════════════════════════════════════════════════════════════════════════
# FIG 3 — Convergence Under Attack (accuracy over rounds)
# ══════════════════════════════════════════════════════════════════════════════
def fig3_convergence():
    rounds = [1, 3, 5, 7, 10, 13, 15, 18, 20]
    clean   = [61.2, 70.4, 76.8, 81.3, 84.7, 86.4, 87.3, 87.9, 88.2]
    poison  = [60.8, 68.1, 72.3, 73.8, 74.1, 74.2, 74.3, 74.3, 74.3]
    ours    = [61.0, 69.8, 76.2, 80.5, 83.8, 85.6, 86.6, 87.1, 87.4]

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(rounds, clean,  color=PALETTE['fedavg_clean'],  lw=2.2, marker='o', ms=6,
            label='FedAvg — Clean (0% attack)', linestyle='--')
    ax.plot(rounds, poison, color=PALETTE['fedavg_poison'], lw=2.2, marker='s', ms=6,
            label='FedAvg — Poisoned (20% Adversarial)', linestyle=':')
    ax.plot(rounds, ours,   color=PALETTE['ours'],          lw=2.5, marker='^', ms=7,
            label='AegisFL (20% Adversarial)', linestyle='-')

    # shade the convergence gap
    ax.fill_between(rounds, poison, ours, alpha=0.08, color=PALETTE['ours'])

    ax.set_xlabel('Communication Round')
    ax.set_ylabel('Global Model Accuracy (%)')
    ax.set_title('Convergence Under Targeted Label-Flip Attack\n'
                 '(20% Adversarial clients, N=20, CICIoT2023)', pad=12)
    ax.legend(loc='lower right', framealpha=0.9)
    ax.set_xlim(1, 20)
    ax.set_ylim(55, 95)

    # annotate final gap
    ax.annotate(f'87.4% (AegisFL)',   xy=(20, 87.4), xytext=(16.5, 90.0),
                arrowprops=dict(arrowstyle='->', color='#333', lw=1.2), fontsize=9)
    ax.annotate(f'74.3% (Poisoned)', xy=(20, 74.3), xytext=(14, 71),
                arrowprops=dict(arrowstyle='->', color='#333', lw=1.2), fontsize=9)

    fig.tight_layout()
    fig.savefig('figures/fig3_convergence.png', bbox_inches='tight')
    fig.savefig('figures/fig3_convergence.pdf', bbox_inches='tight')
    plt.close()
    print('[OK] Fig 3 saved')


# ══════════════════════════════════════════════════════════════════════════════
# FIG 4 — Adversarial Fraction Tolerance
# ══════════════════════════════════════════════════════════════════════════════
def fig4_Adversarial_tolerance():
    fracs   = [10, 20, 30, 40, 50]
    poison  = [31.2, 18.7, 12.4,  9.1,  6.3]
    trimmed = [73.2, 65.9, 55.1, 39.8, 24.6]
    median  = [72.1, 66.2, 56.7, 41.3, 26.3]
    krum    = [75.4, 68.4, 58.3, 43.2, 28.1]
    ours    = [84.6, 76.8, 68.3, 57.9, 44.2]

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(fracs, poison,  color=PALETTE['fedavg_poison'], lw=2,   marker='s', ms=6,
            label='FedAvg (Poisoned)', linestyle=':')
    ax.plot(fracs, trimmed, color=PALETTE['trimmed'],       lw=2,   marker='D', ms=6,
            label='Trimmed Mean')
    ax.plot(fracs, median,  color=PALETTE['median'],        lw=2,   marker='v', ms=6,
            label='Coordinate Median')
    ax.plot(fracs, krum,    color=PALETTE['krum'],          lw=2,   marker='o', ms=6,
            label='Multi-Krum')
    ax.plot(fracs, ours,    color=PALETTE['ours'],          lw=2.5, marker='^', ms=8,
            label='AegisFL (Ours)', linestyle='-')

    ax.axvline(20, color='#888', linestyle='--', lw=1.2, alpha=0.7, label='Default setting (20%)')
    ax.fill_between(fracs, krum, ours, alpha=0.08, color=PALETTE['ours'])

    ax.set_xlabel('Adversarial Client Fraction (%)')
    ax.set_ylabel('RECON F1 (%)')
    ax.set_title('Adversarial Fraction Tolerance\n'
                 '(RECON F1 vs. % of Adversarial clients, Targeted Label-Flip)', pad=12)
    ax.legend(loc='upper right', framealpha=0.9, ncol=1)
    ax.set_xlim(8, 52)
    ax.set_ylim(0, 100)
    ax.set_xticks(fracs)
    ax.set_xticklabels([f'{f}%' for f in fracs])

    fig.tight_layout()
    fig.savefig('figures/fig4_byzantine_tolerance.png', bbox_inches='tight')
    fig.savefig('figures/fig4_byzantine_tolerance.pdf', bbox_inches='tight')
    plt.close()
    print('[OK] Fig 4 saved')


# ══════════════════════════════════════════════════════════════════════════════
# FIG 5 — Per-Class F1 Radar Chart
# ══════════════════════════════════════════════════════════════════════════════
def fig5_per_class_radar():
    classes = ['BENIGN', 'DDoS', 'DoS', 'MIRAI', 'RECON\n(targeted)', 'MITM', 'WebApp', 'Malware']
    poisoned = [62.4, 91.2, 78.6, 98.7, 18.7, 71.3, 34.2, 29.6]
    proposed = [85.6, 92.7, 83.4, 98.8, 76.8, 80.9, 68.7, 65.1]

    N = len(classes)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]   # close the loop

    poisoned_vals = poisoned + poisoned[:1]
    proposed_vals = proposed + proposed[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

    ax.plot(angles, poisoned_vals, color=PALETTE['fedavg_poison'], lw=2, linestyle='--', label='FedAvg (Poisoned)')
    ax.fill(angles, poisoned_vals, color=PALETTE['fedavg_poison'], alpha=0.12)

    ax.plot(angles, proposed_vals, color=PALETTE['ours'], lw=2.5, linestyle='-', label='AegisFL (Ours)')
    ax.fill(angles, proposed_vals, color=PALETTE['ours'], alpha=0.18)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(classes, size=10)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], size=8, color='#666')
    ax.set_title('Per-Class F1 Score\nFedAvg (Poisoned) vs. AegisFL (Ours)',
                 pad=20, size=12)
    ax.legend(loc='upper right', bbox_to_anchor=(1.32, 1.12), framealpha=0.9)

    # highlight the targeted class spoke
    recon_idx = 4
    recon_angle = angles[recon_idx]
    ax.plot([recon_angle, recon_angle], [0, 100], color='#F44336', lw=1.2, alpha=0.4, linestyle=':')

    fig.tight_layout()
    fig.savefig('figures/fig5_per_class_radar.png', bbox_inches='tight')
    fig.savefig('figures/fig5_per_class_radar.pdf', bbox_inches='tight')
    plt.close()
    print('[OK] Fig 5 saved')


# ══════════════════════════════════════════════════════════════════════════════
# FIG 6 — Component Ablation (horizontal bars)
# ══════════════════════════════════════════════════════════════════════════════
def fig6_ablation():
    configs = [
        'FedAvg (Poisoned)',
        'Multi-Krum (baseline)',
        'w/o Validation Probe',
        'w/o Per-Class Trust\n(global trust only)',
        'w/o Collusion Detector',
        'Full AegisFL (Proposed)',
    ]
    recon_f1 = [18.7, 68.4, 62.1, 65.3, 71.2, 76.8]
    bar_colors = [
        PALETTE['fedavg_poison'],
        PALETTE['krum'],
        '#78909C',
        '#78909C',
        '#78909C',
        PALETTE['ours'],
    ]

    fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.barh(configs, recon_f1, color=bar_colors, edgecolor='white',
                   linewidth=0.8, height=0.6)

    for bar, val in zip(bars, recon_f1):
        ax.text(val + 0.5, bar.get_y() + bar.get_height() / 2,
                f'{val:.1f}%', va='center', fontsize=10, fontweight='bold')

    # draw drop arrows for ablation rows
    full_val = 76.8
    for i, (cfg, val) in enumerate(zip(configs[2:5], recon_f1[2:5]), start=2):
        drop = full_val - val
        ax.annotate('', xy=(val, i), xytext=(full_val, i),
                    arrowprops=dict(arrowstyle='<-', color='#aaa', lw=1.2))
        ax.text((val + full_val) / 2, i + 0.32, f'−{drop:.1f} pp',
                ha='center', va='bottom', fontsize=8.5, color='#555')

    ax.set_xlabel('RECON F1 (%)')
    ax.set_xlim(0, 100)
    ax.set_title('Component Ablation Study\n'
                 '(RECON F1 under Targeted Label-Flip, 20% Adversarial)', pad=12)
    ax.axvline(full_val, color=PALETTE['ours'], lw=1.5, linestyle='--', alpha=0.5)

    fig.tight_layout()
    fig.savefig('figures/fig6_ablation.png', bbox_inches='tight')
    fig.savefig('figures/fig6_ablation.pdf', bbox_inches='tight')
    plt.close()
    print('[OK] Fig 6 saved')


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('Generating paper figures...\n')
    fig1_main_comparison()
    fig2_multi_attack_heatmap()
    fig3_convergence()
    fig4_Adversarial_tolerance()
    fig5_per_class_radar()
    fig6_ablation()
    print('\nAll figures saved to ./figures/')
    print('   PNG  -> screen/presentations')
    print('   PDF  -> LaTeX paper (\\includegraphics)')
