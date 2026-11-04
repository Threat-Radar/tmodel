#!/usr/bin/env python3
"""Tests for convert.py and check.py (#169). Run: python3 research/0017-requirements-extraction/test_convert.py"""
import pathlib
import sys
import tempfile
import unittest

import yaml

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check  # noqa: E402
import convert  # noqa: E402

FREE = {
    "record": {"id": "demo-free", "body": "regulator", "publisher": "A Government Agency",
               "content": {"sha256": "aa" * 32}},
    "requirements": [
        {"id": "demo-free#1", "designator": "1", "normativity": "requirement", "nature": "process",
         "actor": "Organization (implied)", "locator": "§1", "short_title": "Train staff",
         "text": "The organization shall train\n  its staff."},
        {"id": "demo-free#2", "designator": "2", "normativity": "recommendation",
         "nature": "deliverable", "locator": "§2, Provision 2", "text": "Keep a log: of everything."},
        {"id": "demo-free#3", "designator": "3", "normativity": "permission", "nature": "product",
         "locator": "§3", "condition": "if a model is retrained", "text": "The system may retrain."},
        {"id": "demo-free#4", "designator": "4", "normativity": "principle", "locator": "§4",
         "text": "Be secure."},
        {"id": "demo-free#5", "designator": "5", "normativity": "requirement", "status": "withdrawn",
         "locator": "§5", "text": "Gone."},
    ],
}
LICENSED = {
    "record": {"id": "iso-demo", "body": "iso", "publisher": "ISO/IEC", "content": {"sha256": "bb" * 32}},
    "requirements": [
        {"id": "iso-demo#RQ-01", "designator": "RQ-01", "normativity": "requirement",
         "nature": "deliverable-producing", "locator": "§5.1", "short_title": "Copied title words",
         "text": "LICENSED WORDING that must never be copied."},
    ],
}


def make(tmp, spec, body):
    d = pathlib.Path(tmp) / "records" / body / spec["record"]["id"]
    (d / "distilled").mkdir(parents=True)
    (d / "record.yaml").write_text(yaml.safe_dump(spec["record"]))
    (d / "distilled" / "requirements.yaml").write_text(yaml.safe_dump(
        {"schema": "library-requirements/v2", "record": spec["record"]["id"],
         "requirements": spec["requirements"]}))
    return d


class Convert(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.free = make(self.tmp.name, FREE, "regulator")
        self.lic = make(self.tmp.name, LICENSED, "iso")

    def tearDown(self):
        self.tmp.cleanup()

    def run_convert(self, d, **kw):
        out, n, m, skipped = convert.convert(d, "@someone", date="2026-11-03", **kw)
        return out, yaml.safe_load(out), n, m, skipped

    def test_free_source(self):
        out, doc, n, m, skipped = self.run_convert(self.free)
        reqs = {r["source_ref"]: r for r in doc["requirements"]}
        self.assertEqual((n, m), (5, 3))
        self.assertEqual(dict(skipped)["4"].split(";")[0], "normativity principle has no tmodel equivalent")
        self.assertEqual(dict(skipped)["5"], "status withdrawn in the library record")
        r1 = reqs["library:demo-free#1"]
        self.assertEqual(r1["id"], "requirement:demo-free-1")
        self.assertEqual(r1["name"], "1 — Train staff")
        self.assertEqual(r1["text"], "The organization shall train its staff.")
        self.assertEqual(r1["text_origin"], "verbatim")
        self.assertEqual(r1["normativity"], "mandatory")
        self.assertEqual(r1["requirement_kind"], "organizational")
        self.assertEqual(r1["source_locator"], "1 (§1)")
        r2 = reqs["library:demo-free#2"]
        self.assertEqual((r2["normativity"], r2["requirement_kind"]), ("recommended", "documentation"))
        self.assertEqual(r2["source_locator"], "§2, Provision 2")
        r3 = reqs["library:demo-free#3"]
        self.assertEqual((r3["normativity"], r3["requirement_kind"]), ("optional", "technical"))
        self.assertIn("consider conditional", out)
        self.assertEqual(doc["assertions"], [])
        self.assertEqual(doc["parties"][0]["id"], "party:someone")
        self.assertIn("Coverage: 5 in the source, 3 converted, 2 skipped.", out)

    def test_licensed_source_copies_no_wording(self):
        out, doc, *_ = self.run_convert(self.lic)
        r = doc["requirements"][0]
        self.assertEqual((r["text"], r["text_origin"]), ("", "paraphrase"))
        self.assertEqual(r["name"], "RQ-01")
        self.assertEqual(r["requirement_kind"], "process")
        self.assertNotIn("LICENSED WORDING", out)
        self.assertNotIn("Copied title", out)

    def test_options(self):
        _, doc, _, m, skipped = self.run_convert(self.free, only=["1", "2"], skips={"2": "no product link"},
                                                 extra_normativity={"principle": "informative"})
        self.assertEqual(m, 1)
        self.assertEqual(dict(skipped)["2"], "no product link")
        _, doc, _, m, _ = self.run_convert(self.free, extra_normativity={"principle": "informative"},
                                           empty_text=True)
        self.assertEqual(m, 4)
        self.assertTrue(all(r["text"] == "" and r["text_origin"] == "paraphrase" for r in doc["requirements"]))

    def test_id_collision_fails(self):
        spec = {"record": FREE["record"], "requirements": [
            dict(FREE["requirements"][0], designator="1.1"),
            dict(FREE["requirements"][0], id="demo-free#1-1", designator="1-1")]}
        d = make(self.tmp.name + "/c", spec, "regulator")
        with self.assertRaises(SystemExit):
            convert.convert(d, "someone")

    def test_output_passes_check(self):
        for d, name in ((self.free, "demo-free"), (self.lic, "iso-demo")):
            out, *_ = self.run_convert(d)
            p = pathlib.Path(self.tmp.name) / f"{name}.yaml"
            p.write_text(out)
            n, errs, _, _ = check.check(p)
            self.assertEqual(errs, [], name)


GOOD = """
requirements:
  - id: requirement:demo-free-1
    text: "Train staff."
    text_origin: paraphrase
    requirement_kind: process
    normativity: mandatory
    source_ref: "library:demo-free#1"
    source_locator: "1 (§1)"
  - id: requirement:demo-free-2
    text: "Keep a log."
    text_origin: paraphrase
    requirement_kind: documentation
    normativity: recommended
    source_ref: "library:demo-free#2"
    source_locator: "2 (§2)"
parties:
  - {id: party:someone, name: "@someone", party_kind: person}
assertions:
  - id: assertion:a
    subject: requirement:demo-free-2
    predicate: derived_from
    object: requirement:demo-free-1
    confidence: medium
    assertion_status: accepted
    description: "Proposed by an agent, 2026-11-03. Basis: §2; it builds on §1."
reviews:
  - {id: review:a, reviews: assertion:a, reviewer: party:someone, review_status: accepted, justification: "Checked."}
"""


class Check(unittest.TestCase):
    def errors(self, text, name="demo-free"):
        with tempfile.TemporaryDirectory() as t:
            p = pathlib.Path(t) / f"{name}.yaml"
            p.write_text(text)
            return check.check(p)[1]

    def test_good(self):
        self.assertEqual(self.errors(GOOD), [])

    def test_each_rule_fails(self):
        cases = {
            "no source_locator": GOOD.replace('    source_locator: "1 (§1)"\n', ""),
            "id does not start": GOOD.replace("requirement:demo-free-1\n", "requirement:other-1\n", 1),
            "is not library:demo-free": GOOD.replace("library:demo-free#1", "library:other#1"),
            "filled; propose it": GOOD.replace("    normativity: mandatory\n",
                                               "    normativity: mandatory\n    addresses: [weakness:x]\n"),
            "accepted without": GOOD.replace("review_status: accepted", "review_status: rejected"),
            "should be accepted": GOOD.replace("assertion_status: accepted", "assertion_status: proposed"),
            "not proposed or accepted": GOOD.replace("assertion_status: accepted", "assertion_status: rejected"),
            "no 'Basis:'": GOOD.replace("Basis:", "Because"),
            "out of scope here": GOOD.replace("predicate: derived_from", "predicate: maps_to"),
            "must point at a requirement": GOOD.replace("object: requirement:demo-free-1",
                                                        "object: requirement:other-1"),
            "is not a person": GOOD.replace("party_kind: person", "party_kind: organization"),
            "no justification": GOOD.replace('justification: "Checked."', 'justification: ""'),
        }
        for want, text in cases.items():
            errs = self.errors(text)
            self.assertTrue(any(want in e for e in errs), f"{want!r} not in {errs}")

    def test_licensed_verbatim_fails(self):
        text = GOOD.replace("demo-free", "iso-demo").replace("text_origin: paraphrase",
                                                             "text_origin: verbatim", 1)
        self.assertTrue(any("licensed source" in e for e in self.errors(text, "iso-demo")))

    def test_mitigation_stated_as_fails(self):
        text = GOOD + "mitigations:\n  - {id: mitigation:m, stated_as: [requirement:demo-free-1]}\n"
        self.assertTrue(any("stated_as is filled" in e for e in self.errors(text)))


if __name__ == "__main__":
    unittest.main(verbosity=1)
