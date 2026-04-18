# App test lab — SaaS *compare* prototype

Modular preview that performs **live Leboncoin searches**, scores each ad against the average price of the result set (`hot %`), and produces a **JSON + HTML** report.

## Layout

```
tests/apptest/
  _common.py                    # shared lib (DTOs, filters, stats, HTML, orchestrator)
  _template.html                # HTML shell + CSS (filled by ``render_html``)
  run_mx5_compare.py            # Mazda MX-5 184 ch · 2020+ · ≤ 50 000 km · Pack Sport
  run_z900_compare.py           # Kawasaki Z900 A2 · ≤ 7 000 € · ≤ 17 500 km · 20 km SLV
  test_apptest_compare.py       # pytest unit tests (pure, no HTTP)
  output/                       # JSON + HTML (ignored except ``.gitkeep``)
```

`_common.py` is the only place that touches the LBC SDK — the runners are thin and only declare a `CompareSpec` + an ordered tuple of `FilterStage` predicates.

## Run a comparison (live HTTP, optional `LBC_API_PROXY_URL`)

```bash
python3 tests/apptest/run_mx5_compare.py
python3 tests/apptest/run_z900_compare.py
```

Outputs are written to `tests/apptest/output/<basename>.{html,json}`.

## Unit tests

Fast, no network — covered by the default `pytest` run:

```bash
pytest tests/apptest/test_apptest_compare.py -v
```

## Filtering pipeline

Each runner declares a tuple of `FilterStage` (name, predicate, optional fallback note). The first stage that produces ≥ 1 ad wins; subsequent stages are tried only if the previous ones found nothing. The stage that matched is logged in the report (JSON `filtering.matched_stage`, HTML banner).

Example for **Z900**:

| Stage | Predicate | Note when used |
|---|---|---|
| `z900_in_title` | `Z900` in title | (clean, no warning) |
| `z900_anywhere` | `Z900` in title or body, but not on a known other-bike title | shown as a yellow warning |
| `raw_finder_results` | accept anything | strong warning: no real Z900 in this zone today |

## Adding a new comparator

1. Create `run_<topic>_compare.py`.
2. Build a `cm.CompareSpec(...)` and a tuple of `cm.FilterStage(...)`.
3. Call `cm.run_compare(spec, stages)` from `main()`.
4. Add unit tests in `test_apptest_compare.py` for the new predicates.
