# Issues found in `energy_system.py`

Tool results: **Before** Pylint 6.14/10, Flake8 12 issues, Bandit 1 Medium. **After** Pylint 10.00/10, Flake8 0, Bandit 0.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| `eval()` on user input (B307 / W0123) | Security (Medium) | 63 | `eval(input)` lets a user run arbitrary Python (e.g. `__import__('os').system(...)`). | Replaced with `safe_eval()`, which parses with `ast` and allows only numbers and `+ - * /`. Anything else raises `ValueError`. |
| Mutable default argument (W0102) | Bug | 12 | `history=[]` is created once and shared across calls, so unrelated callers pollute each other's history. The "3 readings stored" output only looked right by accident. | Default is now `None`, a new list is created per call, and `main()` passes its own `history`. |
| Bare `except:` (W0702 / E722) | Bug | 44 | Hides every error (even KeyboardInterrupt) and silently wipes `meters`. | Catch only `OSError` and `json.JSONDecodeError`. |
| File handles not closed (R1732, W1514) | Resource / Bug | 42, 48 | `open()` without `with` leaks the handle on error; no encoding given. | `with open(..., encoding="utf-8")`, and `json.load` / `json.dump`. |
| Negative reading accepted (logic bug, not flagged by any tool) | Logic | 55, 12 | `M-03` with -50 units produced a bill of **-192.50**. | `record_reading` raises `ValueError` for negative units. `main()` catches it and reports it. |
| Unknown meter crashes billing | Bug | 18 | `meters[meter_id]` raises `KeyError`. | `compute_bill` raises a clear `ValueError`. `main()` handles it. |
| `global` statements (W0603) | Design | 27, 40 | Rebinding module globals makes state hard to reason about. | Tier rates are kept in a `rates` list and `meters` is mutated in place (`clear`/`update`), so no `global` is needed. |
| Duplicated tier math / long line (E501) | Style | 19-24 | Three branches repeat the same arithmetic, and one line is 88 characters. | Computed tier units with `min` / `max`, with named constants for the limits. |
| `elif` after `return` (R1705) | Style | 19 | Unnecessary `elif`. | Removed along with the branching above. |
| Missing docstrings (C0114, C0116) | Style | 1, 12, 17, 26, 32, 39, 47, 52 | No module or function documentation. | Added docstrings. |
| `%` string formatting (C0209) | Style | 59, 60, 66 | Old-style formatting. | f-strings. |
| Unused import `sys` (W0611 / F401) | Style | 2 | Dead import. | Removed. |
| Missing blank lines (E302, E305) | Style (Flake8) | 12, 17, 26, 32, 39, 47, 52, 68 | PEP 8 needs 2 blank lines around top-level definitions. | Reformatted. |
| `main()` runs on import | Design | 68 | Importing the module runs the program. | Added `if __name__ == "__main__":`. |

## Observation (not changed)
`main()` never loads `meters.json` at startup, so each run overwrites the previous file. I kept this to preserve the original behaviour.
