"""
Phase E1b Verification Unit Tests.
Verifies:
1. Potency Gate logic under synthetic cases (a, b, c, d).
2. Matrix cell recomputation equality against per-seed lists.
3. Soft containment State Factor (SF) calculation and clipping to [0, 1].
"""

import json
from pathlib import Path
import numpy as np
import pytest

from src.experiments.aggregate_results import (
    evaluate_potency_gate,
    extract_client_outcomes,
)
from src.trust.state_machine import ClientStateMachine


def test_potency_gate_synthetic_cases():
    """
    Unit test potency gate under synthetic paired deltas:
      Sign convention:
        - ASR delta = attacked - clean. Harm achieved if CI lower bound > 0.
        - RECON-F1 drop = clean - attacked. Harm achieved if CI lower bound > 0.
    """
    # (a) ASR up and F1 down -> PASS
    asr_up = [0.15, 0.16, 0.14, 0.15, 0.17, 0.15, 0.16, 0.14]
    f1_down = [0.20, 0.22, 0.21, 0.19, 0.20, 0.23, 0.21, 0.20]  # drop is positive
    asr_ok, f1_ok, gate, _, _ = evaluate_potency_gate(
        paired_asr_deltas=asr_up, paired_recon_drops=f1_down, is_targeted=True
    )
    assert asr_ok is True, "ASR should pass when all deltas are strongly positive"
    assert f1_ok is True, "F1 drop should pass when all drops are strongly positive"
    assert gate == "**PASS**", "Gate must PASS when both criteria are met"

    # (b) F1 down but ASR flat or down -> FAIL
    asr_flat_down = [0.0, -0.01, 0.01, -0.02, 0.0, -0.01, 0.0, -0.02]
    asr_ok, f1_ok, gate, _, _ = evaluate_potency_gate(
        paired_asr_deltas=asr_flat_down, paired_recon_drops=f1_down, is_targeted=True
    )
    assert asr_ok is False, "ASR should fail when CI lower bound <= 0"
    assert f1_ok is True
    assert gate == "**FAIL**", "Gate must FAIL when ASR does not increase"

    # (c) ASR up but F1 flat -> FAIL
    f1_flat = [0.0, 0.01, -0.01, 0.0, 0.01, -0.01, 0.0, 0.0]
    asr_ok, f1_ok, gate, _, _ = evaluate_potency_gate(
        paired_asr_deltas=asr_up, paired_recon_drops=f1_flat, is_targeted=True
    )
    assert asr_ok is True
    assert f1_ok is False, "F1 drop should fail when drop is flat / straddles zero"
    assert gate == "**FAIL**", "Gate must FAIL when RECON-F1 drop is not achieved"

    # (d) Either CI straddling zero -> FAIL
    asr_straddle = [-0.10, -0.05, 0.05, 0.15, 0.10, -0.02, 0.08, 0.02]
    asr_ok, f1_ok, gate, (m, l, h), _ = evaluate_potency_gate(
        paired_asr_deltas=asr_straddle, paired_recon_drops=f1_down, is_targeted=True
    )
    assert l < 0 < h, "Synthetic CI must straddle zero"
    assert asr_ok is False, "ASR straddling zero must fail"
    assert gate == "**FAIL**"

    # Also verify when RECON drop straddles zero
    f1_straddle = [-0.08, -0.04, 0.06, 0.12, 0.05, -0.01, 0.07, 0.02]
    asr_ok, f1_ok, gate, _, (fm, fl, fh) = evaluate_potency_gate(
        paired_asr_deltas=asr_up, paired_recon_drops=f1_straddle, is_targeted=True
    )
    assert fl < 0 < fh, "Synthetic F1 drop CI must straddle zero"
    assert f1_ok is False, "F1 drop straddling zero must fail"
    assert gate == "**FAIL**"


def test_matrix_recompute_equality():
    """
    Asserts that every matrix outcome cell exactly equals the arithmetic mean
    of the per-seed rows recomputed strictly from the four client lists:
      - honest_prob_clients
      - honest_quar_clients
      - attackers_prob_clients
      - attackers_quar_clients
    """
    jsonl_path = Path("results/runs/phase_e1_smoke/runs.jsonl")
    assert jsonl_path.exists(), "phase_e1_smoke runs.jsonl must exist"

    records = []
    with open(jsonl_path) as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    processed = []
    for r in records:
        rec = dict(r)
        outcomes = extract_client_outcomes(rec, num_total_clients=10)
        rec.update(outcomes)
        processed.append(rec)

    # Group by method and scenario
    methods = sorted(list(set(r["method"] for r in processed)))

    for m in methods:
        m_clean = [r for r in processed if r["method"] == m and r["scenario"] == "clean"]
        m_atk = [r for r in processed if r["method"] == m and r["scenario"] == "attacked"]

        if m_clean:
            # Recompute from per-seed rows
            per_seed_cont_fpr = [
                (len(r["honest_prob_clients"]) + len(r["honest_quar_clients"])) / (10 - len(r.get("attacker_ids", [])))
                for r in m_clean
            ]
            per_seed_quar_fpr = [
                len(r["honest_quar_clients"]) / (10 - len(r.get("attacker_ids", [])))
                for r in m_clean
            ]

            matrix_cont_fpr = np.mean([r["containment_fpr"] for r in m_clean])
            matrix_quar_fpr = np.mean([r["quarantine_fpr"] for r in m_clean])

            np.testing.assert_allclose(matrix_cont_fpr, np.mean(per_seed_cont_fpr), rtol=1e-6)
            np.testing.assert_allclose(matrix_quar_fpr, np.mean(per_seed_quar_fpr), rtol=1e-6)

        if m_atk:
            per_seed_atk_q = [
                len(r["attackers_quar_clients"]) / len(r["attacker_ids"])
                for r in m_atk
            ]
            per_seed_atk_p = [
                len(r["attackers_prob_clients"]) / len(r["attacker_ids"])
                for r in m_atk
            ]
            valid_per_seed_prec = [
                len(r["attackers_quar_clients"]) / (len(r["honest_quar_clients"]) + len(r["attackers_quar_clients"]))
                for r in m_atk
                if (len(r["honest_quar_clients"]) + len(r["attackers_quar_clients"])) > 0
            ]
            tot_atks_quar = sum(len(r["attackers_quar_clients"]) for r in m_atk)
            tot_all_quar = sum(len(r["honest_quar_clients"]) + len(r["attackers_quar_clients"]) for r in m_atk)
            pooled_prec = (tot_atks_quar / tot_all_quar) if tot_all_quar > 0 else None

            matrix_atk_q = np.mean([r["attacker_det_quar"] for r in m_atk])
            matrix_atk_p = np.mean([r["attacker_det_prob"] for r in m_atk])
            matrix_valid_precs = [r["quar_precision"] for r in m_atk if r["quar_precision"] is not None]

            np.testing.assert_allclose(matrix_atk_q, np.mean(per_seed_atk_q), rtol=1e-6)
            np.testing.assert_allclose(matrix_atk_p, np.mean(per_seed_atk_p), rtol=1e-6)

            if valid_per_seed_prec:
                np.testing.assert_allclose(np.mean(matrix_valid_precs), np.mean(valid_per_seed_prec), rtol=1e-6)
            else:
                assert len(matrix_valid_precs) == 0


def test_soft_containment_sf_clipping():
    """
    Verifies that State Factor (SF) for D4 soft containment:
    1. Returns expected theoretical values for E in {0, 0.2, 0.4, 0.55, 0.7, 0.9}.
    2. Is strictly clipped to [0.0, 1.0].
    """
    cfg = {
        "trust": {
            "state_machine": {
                "probation_threshold": 0.40,
                "quarantine_threshold": 0.70,
                "soft_containment": True,
            }
        }
    }
    sm = ClientStateMachine(config=cfg, soft_containment=True)

    test_points = {
        0.0: 1.0,
        0.2: 1.0,
        0.4: 1.0,
        0.55: 0.5,
        0.7: 0.0,
        0.9: 0.0,
    }

    for E, expected_sf in test_points.items():
        sf = sm.get_state_factor(client_id=0, evidence_score=E)
        assert abs(sf - expected_sf) < 1e-4, f"E={E} expected SF={expected_sf}, got {sf}"
        assert 0.0 <= sf <= 1.0, f"SF must be clipped to [0, 1], got {sf}"

    # Extreme edge cases
    assert sm.get_state_factor(0, -0.5) == 1.0
    assert sm.get_state_factor(0, 1.5) == 0.0

    # Verify what unclipped formula would have yielded at E=0.9
    unclipped_formula_at_09 = (0.70 - 0.90) / (0.70 - 0.40)
    assert abs(unclipped_formula_at_09 - (-0.6666666666666666)) < 1e-4
