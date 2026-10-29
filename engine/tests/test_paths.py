"""Small AND/OR graphs with known answers (#63 test plan)."""

import pytest

from engine.graph import AttackGraph, GraphError
from engine.paths import enumerate_paths


def graph(*steps, paths=()):
    """steps: (id, gate, precedes) tuples; gate None for no gate."""
    return AttackGraph.from_dict(
        {
            "attack_steps": [
                {"id": sid, "gate": gate, "precedes": list(precedes)}
                for sid, gate, precedes in steps
            ],
            "attack_paths": list(paths),
        }
    )


def found(g, goal, **kw):
    return [p.steps for p in enumerate_paths(g, goal, **kw)]


def test_single_step():
    g = graph(("a", None, []))
    assert found(g, "a") == [("a",)]


def test_sequence():
    g = graph(("a", None, ["b"]), ("b", None, ["c"]), ("c", None, []))
    assert found(g, "c") == [("a", "b", "c")]


def test_pure_or_gives_one_path_per_alternative():
    g = graph(("a", None, ["goal"]), ("b", None, ["goal"]), ("goal", "or_gate", []))
    assert found(g, "goal") == [("a", "goal"), ("b", "goal")]


def test_pure_and_needs_every_predecessor():
    g = graph(("a", None, ["goal"]), ("b", None, ["goal"]), ("goal", "and_gate", []))
    assert found(g, "goal") == [("a", "b", "goal")]


def test_mixed_and_of_ors_multiplies_out():
    # goal = AND(x, y); x = OR(a, b); y = OR(c, d)  ->  2 x 2 = 4 paths
    g = graph(
        ("a", None, ["x"]),
        ("b", None, ["x"]),
        ("c", None, ["y"]),
        ("d", None, ["y"]),
        ("x", "or_gate", ["goal"]),
        ("y", "or_gate", ["goal"]),
        ("goal", "and_gate", []),
    )
    assert found(g, "goal") == [
        ("a", "c", "x", "y", "goal"),
        ("a", "d", "x", "y", "goal"),
        ("b", "c", "x", "y", "goal"),
        ("b", "d", "x", "y", "goal"),
    ]


def test_mixed_or_of_and():
    # goal = OR(x, c); x = AND(a, b)
    g = graph(
        ("a", None, ["x"]),
        ("b", None, ["x"]),
        ("x", "and_gate", ["goal"]),
        ("c", None, ["goal"]),
        ("goal", "or_gate", []),
    )
    assert found(g, "goal") == [("a", "b", "x", "goal"), ("c", "goal")]


def test_shared_step_counts_once():
    # s precedes both branches of an AND: it appears once, not twice
    g = graph(
        ("s", None, ["x", "y"]),
        ("x", None, ["goal"]),
        ("y", None, ["goal"]),
        ("goal", "and_gate", []),
    )
    assert found(g, "goal") == [("s", "x", "y", "goal")]


def test_superset_paths_are_dropped():
    # goal = OR(a, m) with a -> m: the alternatives are {a, goal} and {a, m, goal};
    # the second only adds a detour, so it is dropped
    g = graph(("a", None, ["m", "goal"]), ("m", None, ["goal"]), ("goal", "or_gate", []))
    assert found(g, "goal") == [("a", "goal")]


def test_order_follows_precedes_not_declaration():
    g = graph(("c", None, []), ("b", None, ["c"]), ("a", None, ["b"]))
    assert found(g, "c") == [("a", "b", "c")]


def test_ties_break_by_declaration_order():
    g = graph(("b", None, ["goal"]), ("a", None, ["goal"]), ("goal", "and_gate", []))
    assert found(g, "goal") == [("b", "a", "goal")]


def test_threat_goal_uses_authored_paths_final_steps():
    g = graph(
        ("a", None, ["goal"]),
        ("b", None, ["goal"]),
        ("goal", "or_gate", []),
        paths=[{"id": "p1", "steps": ["a", "b", "goal"], "realizes_threat": "t1"}],
    )
    result = enumerate_paths(g, "t1")
    assert [p.steps for p in result] == [("a", "goal"), ("b", "goal")]
    assert {p.goal_step for p in result} == {"goal"}
    assert {p.authored_path for p in result} == {"p1"}
    assert result[0].to_dict() == {
        "steps": ["a", "goal"],
        "goal_step": "goal",
        "authored_path": "p1",
        "review": {"reviewed": False, "assertion_status": None, "review_status": None},
    }


def test_threat_goal_searches_the_whole_graph():
    # the authored path lists only x and goal, but x needs a first
    g = graph(
        ("a", None, ["x"]),
        ("x", None, ["goal"]),
        ("goal", None, []),
        paths=[{"id": "p1", "steps": ["x", "goal"], "realizes_threat": "t1"}],
    )
    assert found(g, "t1") == [("a", "x", "goal")]


def test_step_goal_has_no_authored_path():
    g = graph(("a", None, []))
    assert enumerate_paths(g, "a")[0].to_dict() == {
        "steps": ["a"],
        "goal_step": "a",
        "review": {"reviewed": False, "assertion_status": None, "review_status": None},
    }


def test_unknown_goal_is_rejected():
    with pytest.raises(GraphError, match="unknown goal"):
        enumerate_paths(graph(("a", None, [])), "nope")


def test_cycle_is_rejected():
    g = graph(("a", None, ["b"]), ("b", None, ["a"]))
    with pytest.raises(GraphError, match="cycle in precedes"):
        enumerate_paths(g, "a")


def test_join_without_gate_is_rejected():
    g = graph(("a", None, ["goal"]), ("b", None, ["goal"]), ("goal", None, []))
    with pytest.raises(GraphError, match="2 predecessors but no gate"):
        enumerate_paths(g, "goal")


def test_path_limit_is_enforced():
    # AND of three 2-way ORs = 8 paths
    steps = []
    for i in range(3):
        steps += [(f"l{i}a", None, [f"o{i}"]), (f"l{i}b", None, [f"o{i}"])]
        steps.append((f"o{i}", "or_gate", ["goal"]))
    steps.append(("goal", "and_gate", []))
    g = graph(*steps)
    assert len(found(g, "goal")) == 8
    with pytest.raises(GraphError, match="more than 4 attack paths"):
        enumerate_paths(g, "goal", limit=4)


# --- fixes from review on #132 ------------------------------------------------


def test_and_limit_counts_real_paths_not_raw_combinations():
    # a 2-way OR feeding a 10-way AND has 2 real paths (the raw product is 2**10)
    steps = [("a", None, ["s"]), ("b", None, ["s"]), ("s", "or_gate", [f"x{i}" for i in range(10)])]
    steps += [(f"x{i}", None, ["g"]) for i in range(10)] + [("g", "and_gate", [])]
    assert len(found(graph(*steps), "g", limit=10)) == 2


def test_authored_path_that_skips_a_step_has_one_final_step():
    g = graph(
        ("a", None, ["b"]),
        ("b", None, ["c"]),
        ("c", None, []),
        paths=[{"id": "p", "steps": ["a", "c"], "realizes_threat": "t"}],
    )
    assert found(g, "t") == [("a", "b", "c")]


def test_authored_path_forming_a_cycle_is_rejected():
    g = graph(
        ("a", None, ["b"]),
        ("b", None, ["a"]),
        paths=[{"id": "p", "steps": ["a", "b"], "realizes_threat": "t"}],
    )
    with pytest.raises(GraphError, match="p: no final step"):
        enumerate_paths(g, "t")


def test_each_result_is_credited_to_its_own_authored_path():
    g = graph(
        ("a", None, ["x"]),
        ("b", None, ["x"]),
        ("x", "or_gate", []),
        paths=[
            {"id": "p1", "steps": ["a", "x"], "realizes_threat": "t"},
            {"id": "p2", "steps": ["b", "x"], "realizes_threat": "t"},
        ],
    )
    assert [(p.steps, p.authored_path) for p in enumerate_paths(g, "t")] == [
        (("a", "x"), "p1"),
        (("b", "x"), "p2"),
    ]


def test_limit_caps_the_total_across_goal_steps():
    # two authored paths whose final steps have 4 paths each: 8 in total
    steps, paths = [], []
    for k in range(2):
        steps += [(f"a{k}{i}", None, [f"A{k}"]) for i in range(2)]
        steps += [(f"b{k}{i}", None, [f"B{k}"]) for i in range(2)]
        steps += [(f"A{k}", "or_gate", [f"X{k}"]), (f"B{k}", "or_gate", [f"X{k}"])]
        steps += [(f"X{k}", "and_gate", [])]
        paths.append({"id": f"p{k}", "steps": [f"X{k}"], "realizes_threat": "t"})
    g = graph(*steps, paths=paths)
    assert len(found(g, "t")) == 8
    with pytest.raises(GraphError, match="t: more than 6 attack paths"):
        enumerate_paths(g, "t", limit=6)


def test_cycle_message_follows_the_edges():
    g = graph(("a", None, ["b"]), ("b", None, ["c"]), ("c", None, ["a"]))
    with pytest.raises(GraphError, match="cycle in precedes: a -> b -> c -> a"):
        enumerate_paths(g, "a")


def test_very_deep_chain_is_an_error_not_a_crash():
    steps = [(f"s{i}", None, [f"s{i + 1}"]) for i in range(5000)] + [("s5000", None, [])]
    with pytest.raises(GraphError, match="too deep"):
        enumerate_paths(graph(*steps), "s5000")
