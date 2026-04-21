# Lab 05 — Code Review & Refactoring

**Duration:** ~1 hour  
**SDLC Phase:** Review  
**Autonomy Level:** 🟠 Human asks, Agent researches & plans  
**Prerequisites:** Lab 04 completed, Python 3.10+, VS Code with GitHub Copilot, [HVE Core](https://marketplace.visualstudio.com/items?itemName=ise-hve-essentials.hve-core) extension

---

## Learning Objective

Use Copilot and HVE Core agents as a **code reviewer** — one that researches context, identifies smells, suggests refactorings, and plans migrations. This is the bridge from "Copilot as tool" to "Agent as team member."

---

## What You'll Practice

| Part | Skill | Time | Copilot Feature |
|------|-------|------|-----------------|
| **1** | Copilot as code reviewer | 10 min | Chat code review prompts |
| **2** | Agent-assisted smell detection | 10 min | HVE `task-researcher` agent |
| **3** | Extract patterns & refactor | 15 min | Chat + inline + RPI workflow |
| **4** | Plan & execute a migration | 15 min | HVE `rpi-agent` (Research → Plan → Implement) |
| **5** | Agent-assisted PR review | 10 min | Chat + agents for review |

---

## Setup

```bash
cd lab05
pip install -r requirements.txt
```

---

## The Scenario

You have two codebases:
- **`task_api.py`** — a Flask REST API with repeated patterns, no validation, raw SQL everywhere
- **`ecommerce.py`** — a well-structured e-commerce backend to use as a "target quality" reference

Your job: use Copilot and agents to review, refactor, and migrate `task_api.py` to production quality.

---

## Part 1 — Copilot as Code Reviewer (10 min)

### Your tasks

1. **Full review:** Select the entire `task_api.py` → Chat → prompt:
   ```
   Act as a senior code reviewer. Review this code for:
   - Code smells and anti-patterns
   - Security concerns
   - Performance issues
   - Maintainability problems
   Rate each issue as Critical/High/Medium/Low.
   ```

2. **Compare with a reference:** Open `ecommerce.py` side-by-side. Ask Chat:
   ```
   Compare the code quality of task_api.py with ecommerce.py.
   What patterns from ecommerce.py should be applied to task_api.py?
   ```

3. **Targeted review:** Ask about specific concerns:
   ```
   Is the database connection handling in task_api.py safe?
   What happens if an exception occurs between connect and close?
   ```

### Takeaway
Copilot can act as a reviewer, but it needs **specific review criteria**. Vague "review this" gets vague feedback. Structured prompts get structured reviews.

---

## Part 2 — Agent-Assisted Smell Detection (10 min)

### Your tasks

1. **Use `task-researcher`:** In Chat, select the `task-researcher` agent → prompt:
   ```
   Research task_api.py thoroughly. Categorize all issues you find into:
   1. DRY violations (repeated code)
   2. Security vulnerabilities
   3. Missing abstractions
   4. Error handling gaps
   5. Testing difficulty (code that's hard to test and why)
   ```

2. **Use `@workspace` for cross-file context:**
   ```
   @workspace What conventions does ecommerce.py follow that task_api.py violates?
   List specific examples.
   ```

### Takeaway
Agents **research first, then answer**. This is more thorough than a single Chat prompt because the agent reads the full files before forming an opinion.

---

## Part 3 — Extract Patterns & Refactor (15 min)

### Your tasks

Apply the review findings one by one:

1. **DB connection context manager:** Ask Chat:
   ```
   Extract the repeated sqlite3.connect/close pattern into a context manager.
   Show me the helper, then show how each route changes.
   ```

2. **Row mapping helper:** Ask Chat:
   ```
   Extract the repeated row-to-dict mapping into a reusable function
   that uses cursor.description for column names.
   ```

3. **Use the RPI workflow** (HVE Core): Select `rpi-agent` → prompt:
   ```
   Add Pydantic validation models for task creation and update.
   Validation rules: title required (1-200 chars), status must be
   pending/in_progress/completed, priority 0-5.
   ```
   Watch the three phases: Research → Plan → Implement.

4. **Apply changes:** Accept the agent's output and verify:
   ```bash
   python -c "from task_api import app; print('imports ok')"
   ```

<details>
<summary>💡 Hints</summary>

- A context manager with `yield` works great for DB connections
- Use `cursor.description` to get column names dynamically
- For Pydantic: `pip install pydantic` first

</details>

---

## Part 4 — Plan & Execute a Migration (15 min)

The big task: migrate from Flask to FastAPI using the RPI workflow.

### Your tasks

1. **Use `rpi-agent`** → prompt:
   ```
   Migrate task_api.py from Flask to FastAPI.
   
   Requirements:
   - Keep the same routes and behavior
   - Use the Pydantic models from Part 3 for request/response
   - Use Depends() for DB connection injection
   - Add async support
   - Create the result as task_api_fastapi.py
   
   Research the existing code first, create a detailed plan, then implement.
   ```

2. **Review the plan** before the agent implements. Does it cover:
   - Route conversion (`@app.route` → `@app.get`, `@app.post`, etc.)?
   - `request.get_json()` → Pydantic model parameter?
   - `Depends()` for DB injection?
   - Response models?

3. **Install and verify:**
   ```bash
   pip install fastapi uvicorn
   python -c "from task_api_fastapi import app; print('migration ok')"
   ```

---

## Part 5 — Agent-Assisted PR Review (10 min)

Simulate a PR review workflow.

### Your tasks

1. **Generate a diff summary:** Ask Chat:
   ```
   Compare task_api.py (original) with the refactored version.
   Generate a review summary as if this were a PR, including:
   - What changed and why
   - Potential risks
   - Suggested follow-up items
   ```

2. **Create a review prompt file:** Create `.github/copilot/prompts/pr-review.prompt.md`:
   ```markdown
   ---
   description: Review code changes as a senior developer
   ---
   Review the selected code changes as a senior developer would in a PR.
   
   Structure your review as:
   ## Summary
   ## What's Good
   ## Concerns
   ## Suggestions
   ## Testing Recommendations
   ```

3. **Use it:** Select the new FastAPI file and use your review prompt.

---

## Lab Complete!

- ✅ Used Copilot as a structured code reviewer with specific criteria
- ✅ Used HVE `task-researcher` for thorough, research-first analysis
- ✅ Extracted repeated patterns into reusable helpers
- ✅ Used the RPI workflow (Research → Plan → Implement) for a full migration
- ✅ Simulated agent-assisted PR review with custom prompts

### What's Next

In **Lab 06**, the agent takes over. You'll switch to **Agent Mode** where Copilot autonomously reads, edits, runs, and iterates — you just approve.

## Part 3 — Add Data Validation with Pydantic (15 min)

### Your tasks

1. Ask Chat: *"Add Pydantic models for task creation and update requests with proper validation"*
2. Add validation rules:
   - `title`: required, 1-200 characters
   - `status`: must be one of `pending`, `in_progress`, `completed`
   - `priority`: integer 0-5
3. Apply the models to the POST and PUT routes

```bash
pip install pydantic
```

<details>
<summary>💡 Hints</summary>

- Use `pydantic.BaseModel` with `Field()` for constraints
- For status, use `Literal["pending", "in_progress", "completed"]`
- Flask + Pydantic: validate in the route with `TaskCreate(**data)`

</details>

---

## Part 4 — Migrate Flask → FastAPI (15 min)

Now for the big one: use **Agent Mode** to migrate the entire API from Flask to FastAPI.

### Your tasks

1. Open Agent Mode in VS Code
2. Prompt: *"Migrate task_api.py from Flask to FastAPI. Keep the same routes and behavior. Use Pydantic models for request/response. Add proper async support and dependency injection for the DB connection."*
3. Agent Mode should:
   - Create a new `task_api_fastapi.py` (or modify in place)
   - Convert `@app.route` to `@app.get`, `@app.post`, etc.
   - Use `Depends()` for DB connection injection
   - Add Pydantic response models
4. Install FastAPI: `pip install fastapi uvicorn`

<details>
<summary>💡 Hints</summary>

- FastAPI uses `@app.get("/tasks")` instead of `@app.route("/tasks", methods=["GET"])`
- `request.get_json()` becomes a Pydantic model parameter
- `Depends()` is the FastAPI pattern for dependency injection (replaces the connection helper)

</details>

---

## Part 5 — Verify with Tests (5 min)

### Your tasks

1. Ask Chat: *"Write pytest tests for the FastAPI task API using TestClient"*
2. Run: `pytest tests/ -v`
3. Ensure all CRUD operations still work

---

## Solutions

- `solutions/task_api_refactored.py` — Parts 1-3 (refactored Flask)
- `solutions/task_api_fastapi.py` — Part 4 (migrated to FastAPI)

---

## Lab Complete!

- ✅ Identified code smells with Copilot Chat review
- ✅ Extracted repeated patterns into reusable helpers
- ✅ Added Pydantic validation models
- ✅ Migrated Flask → FastAPI using Agent Mode
- ✅ Verified migration with tests
