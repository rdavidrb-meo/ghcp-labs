# Lab 02 — Testing with Copilot

**Duration:** ~1 hour  
**SDLC Phase:** Test  
**Autonomy Level:** 🟢 Human directs, Copilot generates  
**Prerequisites:** Lab 01 completed, Python 3.10+, VS Code with GitHub Copilot

---

## What You'll Practice

| Part | Skill | Time | Copilot Feature |
|------|-------|------|-----------------|
| **1** | Mocking HTTP & DB | 10 min | Chat `/tests` + inline |
| **2** | Fixtures & Parametrize | 15 min | Chat + inline suggestions |
| **3** | Async with `AsyncMock` | 15 min | Chat with explicit prompt |
| **4** | Coverage gap fill | 10 min | Agent Mode (VS Code) + CLI `task` agent |
| **5** | CI gate + Agentic Workflows | 10 min | GitHub Actions + `gh aw` |
| **6** | GitHub Copilot CLI for testing | 10 min | `gh copilot explain` / `suggest` / `task` |

---

## Setup

```bash
cd lab02
pip install -r requirements.txt
```

Verify everything is working:

```bash
pytest tests/ -v
```

(All tests should be collected but show as `passed` — they're stubs with `pass`.)

---

## Part 1 — Mocking HTTP & DB (10 min)

**File:** `tests/test_process_order.py`

Open `order_processor.py` and look at `process_order()`. It has **5 code paths**:

| # | Condition | Expected `status` |
|---|-----------|-------------------|
| 1 | Invalid order (no items) | `"invalid"` |
| 2 | DB save fails | `"error"` |
| 3 | Payment succeeds | `"ok"` |
| 4 | Payment HTTP error (402) | `"payment_failed"` |
| 5 | Payment timeout | `"payment_timeout"` |

### Your task

Fill in the 5 test methods in `tests/test_process_order.py` to cover all paths.

**Key techniques:**
- `unittest.mock.patch` to mock `requests.post` for the payment API
- In-memory SQLite (`:memory:`) for the DB — `save_order` accepts a `conn` parameter
- Create the `orders` table in your test setup

**Try with Copilot:** Open the test file and use **Copilot Chat** → ask it to help implement each test.

<details>
<summary>💡 Hints (click to expand)</summary>

- Patch at the import location: `@patch("order_processor.requests.post")` not `@patch("requests.post")`
- For `raise_for_status` on 402: `mock_resp.raise_for_status.side_effect = requests.HTTPError("402")`
- For timeout: `mock_post.side_effect = requests.Timeout()`

</details>

### Verify

```bash
pytest tests/test_process_order.py -v
```

---

## Part 2 — Fixtures & Parametrize (15 min)

**Files:** `tests/test_validation.py` + `tests/conftest.py`

`validate_order()` has **8+ conditions**. Writing 8 separate test functions is tedious — use `@pytest.mark.parametrize` instead.

### Your tasks

1. **Fixture factory:** Move the `make_order` fixture into `conftest.py` so it's shared across all test files. The fixture should return a *function* (factory pattern), not an object.

2. **Parametrized tests:** In `test_validation.py`, use `@pytest.mark.parametrize` to test all these cases in ONE test function:

   | `order_kwargs` | Expected error substring |
   |---|---|
   | `order_id=""` | `"order_id is required"` |
   | `order_id="   "` | `"order_id is required"` |
   | `customer_email="no-at"` | `"customer_email is invalid"` |
   | `customer_email=""` | `"customer_email is invalid"` |
   | `items=[]` | `"at least one item"` |
   | `discount_pct=-5` | `"between 0 and 100"` |
   | `discount_pct=101` | `"between 0 and 100"` |

3. **Boundary tests:** Verify that `discount_pct=0` and `discount_pct=100` are VALID (no errors).

4. **Item-level validation:** Test `quantity <= 0` and `unit_price < 0`.

<details>
<summary>💡 Hints (click to expand)</summary>

- Fixture factory: the fixture returns a function, not an object
- For boundary tests (discount=0, discount=100): these should return empty error list
- Use `pytest.mark.parametrize("order_kwargs,expected_errors", [...])`

</details>

### Verify

```bash
pytest tests/test_validation.py -v
```

---

## Part 3 — Async with AsyncMock (15 min)

**File:** `tests/test_notify.py`

`notify_customer()` is fully async with `aiohttp`. This forces you to use `AsyncMock` and `pytest-asyncio`.

### Your tasks

1. **Successful notification:** Mock the session, set `status = 200`, assert `True`
2. **Non-200 response:** Set `status = 500`, assert `False`
3. **Network error:** Set `side_effect = aiohttp.ClientError()`, assert `False`

<details>
<summary>💡 Hints (click to expand)</summary>

- `AsyncMock` is in `unittest.mock` from Python 3.8+
- Mock the context manager: `mock_session.post.return_value.__aenter__.return_value.status = 200`
- Use `assert_awaited_once_with()` not `assert_called_once_with()` for async

</details>

### Verify

```bash
pytest tests/test_notify.py -v
```

---

## Part 4 — Coverage Gap Fill with Agent Mode (10 min)

Now let's see how much coverage you have:

```bash
pytest tests/ --cov=order_processor --cov-report=term-missing -v
```

### Your tasks

1. **Read the report** — which lines/functions are still uncovered?
2. **Use Copilot Agent Mode** (VS Code) — open Agent Mode and prompt:
   > "Run pytest with coverage, identify uncovered lines in order_processor.py, and write tests to cover them."
3. **Or use the CLI task agent:**
   ```bash
   gh copilot task "Run pytest --cov on this project, find uncovered lines, and add tests"
   ```
4. Re-run coverage and aim for **80%+**

<details>
<summary>💡 Hints (click to expand)</summary>

- If Agent Mode stops early, re-prompt: "Continue — run pytest again and fix remaining failures"
- Likely uncovered: `load_order()`, `charge_customer()` standalone, `Order.subtotal`/`total` properties, `get_db_connection()`

</details>

---

## Part 5 — CI Coverage Gate + Agentic Workflows (10 min)

### 5a: Coverage gate in CI

If your repo has a `.github/workflows/tests.yml`, look for the `--cov-fail-under=80` flag — this makes the CI job **fail** if coverage drops below 80%. (If you don't have one yet, just test the flag locally.)

```bash
# Test it locally:
pytest tests/ --cov=order_processor --cov-report=term-missing --cov-fail-under=80 -v
```

If it fails, go back and add more tests until you pass the gate.

### 5b: Agentic Workflows (bonus)

If your repo has a `.github/workflows/improve-tests.md`, this is a GitHub Agentic Workflow definition that automatically finds and fills coverage gaps. (This file is not included in the lab — you can create one as an exercise.)

To try it locally (requires `gh` CLI):

```bash
gh extension install github/gh-aw
gh aw compile .github/workflows/improve-tests.md
gh aw run improve-tests
```

<details>
<summary>💡 Hints (click to expand)</summary>

- `--cov-fail-under=80` exits with code 2 if coverage is below threshold
- The Agentic Workflow needs `gh extension install github/gh-aw` to compile and run locally

</details>

---

## Part 6 — GitHub Copilot CLI for Testing (10 min)

So far you've used Copilot inside VS Code. Now let's use it **from the terminal** with the GitHub CLI.

### Setup

```bash
# Install the Copilot CLI extension (requires gh CLI)
gh extension install github/gh-copilot

# Verify
gh copilot --help
```

### 6a: Explain — understand unfamiliar test patterns (2 min)

Use `gh copilot explain` to understand code without leaving the terminal:

```bash
gh copilot explain "What does @patch('order_processor.requests.post') do and why not @patch('requests.post')?"
```

Try another:

```bash
gh copilot explain "What does mock_session.post.return_value.__aenter__.return_value.status = 200 mean in Python?"
```

**When to use:** Onboarding to a new codebase, understanding unfamiliar patterns, quick reference.

### 6b: Suggest — get the right command (3 min)

You know *what* you want but not the exact command:

```bash
# How do I run only tests that failed last time?
gh copilot suggest "run only previously failed pytest tests"

# How do I see coverage for just one function?
gh copilot suggest "run pytest coverage for only the validate_order function in order_processor.py"

# How do I create a PR from the terminal?
gh copilot suggest "create a draft pull request titled 'Add unit tests' from current branch"
```

Copilot will ask you to pick the command type (shell, git, or gh) then generate the exact command. You can run it directly.

### 6c: Task — autonomous test generation (5 min)

`gh copilot task` is the CLI equivalent of Agent Mode. Give it a goal and it works autonomously:

**Step 1:** Check your current coverage gaps:

```bash
pytest tests/ --cov=order_processor --cov-report=term-missing -v
```

**Step 2:** Ask Copilot to fill them:

```bash
gh copilot task "Look at lab02/order_processor.py. The functions load_order() and charge_customer() need direct unit tests. Write them in lab02/tests/test_cli_generated.py using in-memory SQLite for DB and unittest.mock.patch for HTTP calls."
```

**Step 3:** Verify the generated tests pass:

```bash
pytest tests/ --cov=order_processor --cov-report=term-missing -v
```

**Step 4:** If coverage is still below target, iterate:

```bash
gh copilot task "Coverage is still below 80%. Check the remaining uncovered lines and add tests."
```

<details>
<summary>💡 Hints (click to expand)</summary>

- `explain` is best for understanding patterns — give it a specific code snippet or concept
- `suggest` asks you to pick shell/git/gh command type — pick "shell" for pytest commands
- `task` works best with specific, well-scoped instructions — include file paths and function names
- If `task` output isn't right, refine your prompt with more context

</details>

---

## Final Check

Run the full suite with coverage:

```bash
pytest tests/ --cov=order_processor --cov-report=term-missing -v
```

---

## Lab Complete! Here's What You Practiced:

- ✅ Mocking HTTP clients and DB layers with `unittest.mock.patch`
- ✅ Fixture factories with `conftest.py` for clean, reusable test data
- ✅ `pytest.mark.parametrize` for data-driven edge case coverage
- ✅ Async testing with `AsyncMock` and `pytest-asyncio`
- ✅ Copilot Agent Mode (VS Code) and CLI `task` agent to identify and fill coverage gaps autonomously
- ✅ CI coverage gate with `--cov-fail-under` to make quality a hard requirement
- ✅ GitHub Agentic Workflows for continuous, automated test improvement
- ✅ GitHub Copilot CLI (`explain`, `suggest`, `task`) for terminal-first testing workflows

---

## Solutions

Solutions for each part are in the `solutions/` folder:
- `solutions/test_process_order_solution.py` — Part 1
- `solutions/conftest_solution.py` — Part 2 (shared fixtures)
- `solutions/test_validation_solution.py` — Part 2
- `solutions/test_notify_solution.py` — Part 3

---

## Trainer Notes

- The starter code is intentionally injectable — all external deps (DB, HTTP, async session) accept optional parameters so they're easy to mock without monkeypatching globals
- `process_order()` has 5 distinct code paths — ideal for Part 1
- `validate_order()` has 8+ conditions — ideal for parametrize in Part 2
- `notify_customer()` is fully async with aiohttp — forces use of AsyncMock in Part 3
- `.github/workflows/improve-tests.md` is referenced as a GitHub Agentic Workflow definition — participants can create one as a bonus exercise
- `datetime.datetime.now()` in `Order.__post_init__` is an intentional testability trap — ask participants how they'd mock it (answer: inject `created_at` explicitly in tests, or monkeypatch `datetime.datetime`)
