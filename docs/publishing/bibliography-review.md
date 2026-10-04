# Bibliography render — adversarial review (first pass)

Status: notes for the WAVE 1 render (#91, content from #86). Not a `DEC-*`.
The generator in `render_bibliography.py` is written to these notes. Do not
treat the first HTML as the finished bibliography; re-run as records arrive
and as review changes tags.

## What would make categorization fail

1. **Reading `summary.md` front matter `type`.** Every summary is
   `type: summary` (`library-summary/v1`). The document type lives on
   `record.yaml` (`rfc`, `draft`, `spec`, `paper`, `dataset`, `repo`, `web`,
   …). A view keyed off the summary puts the whole library in one bucket.

2. **Using the directory, or a body-name tag, as the topic.** Records are
   stored by issuing body. That is not the subject. Tags mix three
   vocabularies (subject, body, role in `library/schema/tags.yaml`) plus free
   words and standing words (`standard`, `draft`). `ietf` on two RFCs is not a
   shared topic. `standard` on ISO/SAE 21434 and FIPS 140-3 is not a shared
   subject. `normative` is why we kept a record, not what it is about.

3. **Treating an empty applicability cell as `none`, or scraping the Why.**
   Summaries use two dialects: an Axis/Rating/Why table, and a prose line
   (`Ratings — security: core · …`) under "Applicability to tmodel". Many
   other files are still the template, with a blank table. A regex will
   mis-read both, and a blank cell is "not assessed", not a judgement.
   Ratings in the HTML come only from `record.yaml` `applicability`.

4. **Publishing the template as if it were a review.** Unfilled `summary.md`
   files still contain the instructions ("_Two to five sentences…"). Rendering
   that text makes a queued record look summarized.

5. **Inventing edges.** A shared tag is co-membership, not a citation.
   `bears_on` means both records name that id, not that they agree. `cites`
   and `relations` are different claims (schema: fact vs curatorial
   judgement) and must not be poured into one crosswalk. A tag that only
   co-occurs because both records were labeled `graph` or `compliance` is a
   weak bucket. Synonyms (`graph` / `knowledge-graph`) must not be merged
   until a reviewed alias table exists. A manifest topic that is not already
   `record.topic` or one of the record's tags would be a shadow taxonomy.

6. **One bibliographic layout for every type.** A dataset is a living
   catalog, not a paper with forgotten authors. An Internet-Draft is not an
   RFC. A repository is not a ratified specification. A web page has a
   retrieval date, not an edition. Empty Author/Published rows hide that.

## How types are displayed

Identity, applicability, tags, and links always come from `record.yaml`.
`summary.md` is prose underneath, labeled as such. Each type adds a heading
and only the fields that type actually has:

| Type | Page shows | Page refuses to pretend |
|---|---|---|
| `rfc` | RFC number, DOI, authors, date, maturity, recorded `supersedes` | That maturity was guessed |
| `draft` | Draft name, datatracker URL, a "not a standard" callout | That a draft is an RFC |
| `spec` | Publisher, version, identifier keys, page count if recorded | A blank author line |
| `paper` | Authors and date; identifiers the record actually has | A venue the record does not name |
| `dataset` | Catalog URL and retrieved date; "one record for the catalog" | An edition date |
| `repo` | Repository URL as the primary link; implementation survey count | That the repo is a normative text |
| `web` | URL and retrieved date; the page can change | That retrieval is publication |

`relations` and `cites` render on the record page only when the YAML has
them. A target in this subset is a link. Any other id is text. Gaps with a
title/locator stay gaps. Nothing is added.

## Views

**v1 (this render)**

- Index — the manifest subset, status visible, not a ranking
- By topic/tag — one primary topic per record, plus other subject/free tags
- By document type
- By issuing body — separate from topic, on purpose
- Crosswalk — shared subject/free tags, and shared `bears_on`, only when at
  least two published records carry them
- One HTML page per record

Body tags, role tags, and standing/maturity words are shown on the record and
kept out of the topic view and the tag crosswalk. A tag whose records do not
share one primary topic is marked **broad**.

**Later, not this pass**

- Maturity view, status-workflow view, applicability-axis matrix
- Synonym folding, only from a reviewed alias list
- Citation chasing from `cites` gaps (#86 expansion)
- A relations graph — that is WAVE 2 / KG (#84), not this page
- Search, PDF, the rest of the library (129 `record.yaml` files today; this
  manifest is a subset)

## Re-run

`python3 docs/publishing/render_bibliography.py` from the repo root.
Output under `docs/bibliography/` is generated. Do not hand-edit it.
`docs/.nojekyll` stays; pages have no scripts and no trackers.
