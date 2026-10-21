"""Regression: attack paths in the example models (spec/vectors/), checked by hand
against each file's gates and `precedes` edges.

The vectors list both alternatives of an OR step in one authored AttackPath; the
engine returns one path per alternative, so those threats have two paths here.
"""

from pathlib import Path

import pytest

from engine.load.vector import load_vector
from engine.paths import enumerate_paths

VECTORS = Path(__file__).resolve().parents[2] / "spec" / "vectors"
EXAMPLE_MODELS = sorted(p for p in VECTORS.glob("*.yaml") if ".linkml." not in p.name)

# file -> threat -> expected paths (step ids without the "attack-step:" prefix)
EXPECTED = {
    "mvp-01-software-doc-service": {
        "xxe-file-read": [
            [
                "upload-crafted-doc",
                "parser-resolves-entity",
                "coerce-file-uri",
                "read-internal-file",
            ],
        ],
        "imds-pivot": [
            ["point-entity-at-metadata", "fetch-instance-credentials"],
            ["dns-rebind-to-metadata", "fetch-instance-credentials"],
        ],
    },
    "mvp-02-automotive-ecu": {
        "remote-diag-injection": [
            ["reach-modem-over-cellular", "bypass-diag-auth", "inject-can-frame"],
        ],
        "infotainment-pivot": [
            ["compromise-companion-app", "gain-infotainment-foothold", "pivot-to-can"],
            ["malicious-ota", "gain-infotainment-foothold", "pivot-to-can"],
        ],
    },
    "mvp-03-hierarchical-system": {
        "gateway-default-creds": [
            ["reach-gateway-service", "use-default-creds", "actuate-via-can"],
        ],
        "cloud-jwt-bypass": [
            ["forge-jwt-none-alg", "call-fleet-api"],
            ["forge-jwt-weak-key", "call-fleet-api"],
        ],
        # authored with only call-fleet-api and chain-to-in-vehicle; the shared
        # JWT steps that call-fleet-api needs come from the whole graph
        "cross-subsystem-chain": [
            ["forge-jwt-none-alg", "call-fleet-api", "chain-to-in-vehicle"],
            ["forge-jwt-weak-key", "call-fleet-api", "chain-to-in-vehicle"],
        ],
    },
    "mvp-18-shared-vuln-vex-override": {
        "weak-rng-key-recovery": [
            ["observe-rng-outputs", "capture-tls-handshake", "derive-session-key"],
        ],
        "side-channel-seed-leak": [
            ["power-side-channel", "recover-seed"],
            ["emi-side-channel", "recover-seed"],
        ],
    },
    "tv-hardware-brake-ecu": {
        # connect-debug-probe feeds both branches of the AND; it appears once
        "fw-tamper": [
            [
                "gain-physical-access",
                "connect-debug-probe",
                "bypass-readout-protection",
                "inject-voltage-glitch",
                "extract-and-modify-firmware",
                "reflash-unit",
            ],
        ],
    },
    "tv-software-auth-service": {
        "rce-via-deser": [
            [
                "enumerate-refresh-endpoint",
                "craft-serialized-payload",
                "deliver-via-refresh",
                "trigger-gadget-chain",
            ],
        ],
        "supply-chain-rce": [
            [
                "compromise-maintainer-account",
                "publish-malicious-release",
                "downstream-pulls-update",
            ],
            ["typosquat-dependency", "publish-malicious-release", "downstream-pulls-update"],
        ],
    },
}


def short(step_id):
    return step_id.removeprefix("attack-step:")


def test_every_example_model_has_expectations():
    assert {p.stem for p in EXAMPLE_MODELS} == set(EXPECTED)


@pytest.mark.parametrize("stem", sorted(EXPECTED))
def test_paths_match_expected(stem):
    graph = load_vector(VECTORS / f"{stem}.yaml")
    assert {t.removeprefix("threat-instance:") for t in graph.threats()} == set(EXPECTED[stem])
    for threat, expected in EXPECTED[stem].items():
        got = [
            [short(s) for s in p.steps] for p in enumerate_paths(graph, f"threat-instance:{threat}")
        ]
        assert got == expected, threat


@pytest.mark.parametrize("path", EXAMPLE_MODELS, ids=lambda p: p.stem)
def test_every_computed_path_respects_gates_and_order(path):
    graph = load_vector(path)
    for threat in graph.threats():
        for computed in enumerate_paths(graph, threat):
            position = {s: i for i, s in enumerate(computed.steps)}
            for sid in computed.steps:
                preds = graph.predecessors(sid)
                inside = [p for p in preds if p in position]
                gate = graph.steps[sid].gate
                if gate == "or_gate" and len(preds) > 1:
                    assert inside, (threat, sid)  # at least one alternative
                else:
                    assert inside == preds, (threat, sid)
                assert all(position[p] < position[sid] for p in inside), (threat, sid)
