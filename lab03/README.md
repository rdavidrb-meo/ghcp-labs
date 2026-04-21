# Lab 03 — Debugging & Troubleshooting

**Duration:** ~1 hour  
**SDLC Phase:** Debug  
**Autonomy Level:** 🟡 Human points, Copilot fixes  
**Prerequisites:** Lab 02 completed, Python 3.10+, VS Code with GitHub Copilot

---

## What You'll Practice

| Part | Skill | Time | Copilot Feature |
|------|-------|------|-----------------|
| **1** | Find bugs with Copilot | 15 min | Chat `/fix` + inline |
| **2** | Explain unfamiliar code | 10 min | Chat `/explain` |
| **3** | Generate docstrings & docs | 15 min | Chat `/doc` + inline |
| **4** | Troubleshoot failing tests | 10 min | Chat + error context |
| **5** | Generate a README from code | 10 min | Chat with explicit prompt |

---

## Setup

```bash
cd lab03
pip install pytest
```

---

## The Scenario

You've inherited `inventory.py` — an inventory management system written by a colleague who left the company. It has **7 known bugs** and **no documentation**.

Your job: fix the bugs, add documentation, and write tests.

---

## Part 1 — Find and Fix Bugs (15 min)

**File:** `inventory.py`

There are **7 bugs** hidden in the code. Use Copilot to find them.

### Your tasks

1. **Select the `Inventory` class** → open Copilot Chat → type `/fix`
2. Review each suggestion. Copilot should catch most of the bugs.
3. For the ones it misses, try asking:
   - *"Is the restock method correct? It seems like stock is being replaced, not added."*
   - *"What's wrong with the get_low_stock filter?"*
   - *"Is the percentage calculation in bulk_update_prices correct?"*

### Bug checklist

Once you've found them, check them off:

- [ ] `restock()` — stock is replaced instead of added (`=` should be `+=`)
- [ ] `sell()` — total uses integer division (`// 1` should be removed or use `round()`)
- [ ] `get_low_stock()` — comparison is backwards (`>` should be `<`)
- [ ] `get_total_value()` — adds only price, not price × stock
- [ ] `bulk_update_prices()` — divides by 10 instead of 100
- [ ] `export_report()` — value is price + stock instead of price × stock
- [ ] `get_transactions()` — compares string timestamp to datetime object

<details>
<summary>💡 Hints</summary>

- Try: select a method → Chat → "Is there a bug in this method?"
- Try: select the whole class → Chat → `/fix` → review all suggestions
- For `get_transactions`: the fix is to compare `t["timestamp"] > since.isoformat()`

</details>

### Verify

After fixing all bugs, create `test_inventory.py` and write at least one test per fix to prove the bug is gone.

---

## Part 2 — Explain Unfamiliar Code (10 min)

Pretend you've never seen this codebase before.

### Your tasks

1. Select `export_report()` → Chat → `/explain`
2. Select `get_transactions()` → Chat → *"Explain the filtering logic and what types the parameters expect"*
3. Select `_record_transaction()` → Chat → *"Why is this prefixed with underscore?"*
4. Ask: *"What design pattern does the Inventory class follow?"*

### Takeaway

`/explain` is your first tool when onboarding to unfamiliar code. It's faster than reading docs (especially when there are none).

---

## Part 3 — Generate Documentation (15 min)

The code has minimal docstrings. Let's fix that.

### Your tasks

1. **Docstrings:** Select each method → Chat → `/doc`. Copilot generates Google/NumPy-style docstrings with parameters, return types, and examples.

2. **Type hints:** Ask Chat: *"Add type hints to all methods in the Inventory class"*

3. **Inline comments:** For complex logic (like `get_transactions` filtering), ask: *"Add inline comments explaining each step"*

4. **Module docstring:** At the top of the file, ask Chat: *"Generate a module-level docstring for inventory.py explaining what this module does"*

<details>
<summary>💡 Hints</summary>

- `/doc` generates docstrings for the selected code
- For type hints, Copilot uses the existing code to infer types
- Ask for specific docstring formats: "Use Google-style docstrings"

</details>

---

## Part 4 — Troubleshoot Failing Tests (10 min)

**File:** `tests/test_inventory_starter.py`

The starter test file has tests that **fail due to the original bugs**. Your job: use the failing test output + Copilot to understand and fix each failure.

### Your tasks

1. Run the tests:
   ```bash
   pytest tests/test_inventory_starter.py -v
   ```
2. For each failure, **copy the error traceback** → paste into Chat → ask *"Why is this test failing and how do I fix it?"*
3. Copilot will explain the root cause (the bug) and suggest the fix

### Takeaway

Copilot excels at interpreting tracebacks. Instead of reading stack traces manually, paste them into Chat.

---

## Part 5 — Generate a README from Code (10 min)

### Your tasks

1. Select the entire `inventory.py` file → Chat → *"Generate a README.md for this module including: overview, installation, usage examples, and API reference"*
2. Review the output — Copilot will produce a full README with code examples
3. Ask: *"Add a section about known limitations and a changelog template"*

<details>
<summary>💡 Hints</summary>

- Be specific about what sections you want in the README
- Ask for "usage examples with expected output" to get runnable code blocks

</details>

---

## Solutions

- `solutions/inventory_fixed.py` — All 7 bugs fixed with documentation

> **Note:** `solutions/test_inventory_solution.py` is not yet provided.

---

## Lab Complete!

- ✅ Found and fixed bugs using Copilot Chat `/fix`
- ✅ Used `/explain` to understand unfamiliar code
- ✅ Generated docstrings and documentation with `/doc`
- ✅ Troubleshot failing tests by pasting tracebacks into Chat
- ✅ Generated a full README from source code
