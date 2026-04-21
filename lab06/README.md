# Lab 06 — Agent Mode

**Duration:** ~1 hour  
**SDLC Phase:** Code + Test + Debug (Autonomous)  
**Autonomy Level:** 🔴 Human approves, Agent implements  
**Prerequisites:** Lab 05 completed, Python 3.10+, VS Code with GitHub Copilot (Agent Mode enabled)

---

## What You'll Practice

| Part | Skill | Time | Copilot Feature |
|------|-------|------|-----------------|
| **1** | Single-file feature with Agent Mode | 10 min | Agent Mode |
| **2** | Multi-file autonomous changes | 15 min | Agent Mode |
| **3** | Test generation + iteration | 15 min | Agent Mode (run & fix loop) |
| **4** | Bug hunting across modules | 10 min | Agent Mode + terminal |
| **5** | Full feature: plan → implement → test | 10 min | Agent Mode end-to-end |

---

## Setup

```bash
cd lab06
pip install pytest
```

---

## The Scenario

You have `expense_tracker.py` — a CLI expense tracker with multiple classes: `ExpenseStore` (persistence), `ReportGenerator` (reports), and `BudgetTracker` (budget alerts). You'll use **Agent Mode** to autonomously add features, fix bugs, and write tests.

---

## What is Agent Mode?

Agent Mode is Copilot working **autonomously**. Instead of answering one question, it:
1. **Reads** your codebase
2. **Plans** what to do
3. **Edits** files
4. **Runs** commands (tests, linters)
5. **Iterates** if something fails

You give it a goal. It figures out the steps.

To activate: In VS Code Copilot Chat, switch from "Chat" to "Agent" mode (dropdown at the top).

---

## Part 1 — Single-File Feature (10 min)

### Your task

Switch to Agent Mode and prompt:

```
Add a "recurring expenses" feature to expense_tracker.py.

A RecurringExpense should have:
- All Expense fields
- frequency (daily, weekly, monthly, yearly)
- start_date and optional end_date
- is_active flag

Add a method to ExpenseStore that generates pending expenses
from all active recurring expenses for a given month.
```

### What to observe

- Does Agent Mode read `expense_tracker.py` first?
- Does it follow the existing patterns (dataclasses, Enum, etc.)?
- Does it add the new class in the right place?
- Does it handle edge cases (end_date in the past, etc.)?

### Verify

Review the changes. Ask Agent Mode: *"Now write tests for the recurring expenses feature."*

---

## Part 2 — Multi-File Autonomous Changes (15 min)

### Your task

Prompt Agent Mode:

```
Refactor expense_tracker.py into separate modules:
- models.py — all dataclasses and enums (Expense, Budget, Category, etc.)
- store.py — ExpenseStore class
- reports.py — ReportGenerator class  
- budget.py — BudgetTracker class

Update all imports. Make sure everything still works together.
Create an __init__.py that re-exports the main classes.
```

### What to observe

- Does Agent Mode create all 5 files?
- Does it update imports correctly across files?
- Does it create a proper `__init__.py`?
- Does it run tests to verify nothing broke?

If it stops early, prompt: *"Continue — verify the refactoring by running pytest."*

---

## Part 3 — Test Generation + Iteration (15 min)

### Your task

Prompt Agent Mode:

```
Write comprehensive pytest tests for the expense tracker.
Cover all classes: ExpenseStore, ReportGenerator, and BudgetTracker.
Use tmp_path for file operations. Use factory fixtures.
Run the tests and fix any failures.
Target 90% coverage.
```

### What to observe

- Does it create test files?
- Does it run pytest and read the output?
- When tests fail, does it fix them automatically?
- Does it check coverage and add more tests if needed?

### Key learning

Agent Mode's **run-fix loop** is its superpower. It writes tests → runs them → reads failures → fixes → runs again. This is the cycle that makes it so productive.

---

## Part 4 — Bug Hunting (10 min)

### Your task

Prompt Agent Mode:

```
Run all tests with coverage. Analyze the coverage report.
For any uncovered lines, determine if they represent:
1. Untested happy paths — write tests
2. Error handling — write tests that trigger the errors
3. Dead code — flag it for removal

Give me a summary of what you found and what you did.
```

### What to observe

- Does it identify truly dead code vs. just untested code?
- Does it write meaningful tests (not just hitting lines for coverage)?
- Does it explain its reasoning?

---

## Part 5 — Full Feature: Plan → Implement → Test (10 min)

### Your task

Give Agent Mode a complex, open-ended prompt:

```
Add a complete "expense analytics" feature to the expense tracker:
1. Trend analysis — compare spending month-over-month
2. Category breakdown — pie chart data (percentages by category)  
3. Anomaly detection — flag expenses that are 2x above the category average
4. Savings projection — based on current spending, project monthly savings

Write the code, write tests, run them, and make sure everything passes.
```

### What to observe

- Does it plan before coding?
- Does it create a well-structured class/module?
- Does it write tests proactively (not just when asked)?
- How does it handle the ambiguity in "anomaly detection" and "savings projection"?

---

## Tips for Effective Agent Mode Prompts

1. **Be specific about the goal** but flexible about implementation
2. **Include acceptance criteria** — "write tests", "target 90% coverage", "run and fix"
3. **Name files and classes** if you have preferences
4. **Say "continue"** if it stops before finishing
5. **Review intermediate output** — you can steer mid-task

---

## Lab Complete!

- ✅ Used Agent Mode for single-file feature development
- ✅ Let Agent Mode autonomously refactor across multiple files
- ✅ Experienced the run-fix loop for test generation
- ✅ Used Agent Mode for intelligent bug hunting and coverage analysis
- ✅ Gave Agent Mode an open-ended feature request and reviewed its plan
