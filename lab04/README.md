# Lab 04 — Context Engineering

**Duration:** ~1 hour  
**SDLC Phase:** Cross-cutting (Standards & Conventions)  
**Autonomy Level:** 🟡 Human configures, Copilot follows rules  
**Prerequisites:** Lab 03 completed, Python 3.10+, VS Code with GitHub Copilot

---

## What You'll Practice

| Part | Skill | Time | Copilot Feature |
|------|-------|------|-----------------|
| **1** | Custom instructions | 15 min | `.github/copilot-instructions.md` |
| **2** | See instructions in action | 10 min | Chat + inline with instructions active |
| **3** | Prompt files for reusable tasks | 15 min | `.github/copilot/prompts/` |
| **4** | Indexed repos for context | 10 min | VS Code workspace indexing |
| **5** | HVE Core instructions | 10 min | HVE Core extension |

---

## Setup

```bash
cd lab04
pip install pytest
```

---

## The Scenario

You have `data_pipeline.py` — a data processing pipeline. The project has a `.github/copilot-instructions.md` file that defines coding conventions. Your job: see how custom instructions change Copilot's behavior, then extend them.

---

## Part 1 — Custom Instructions (15 min)

### What are custom instructions?

`.github/copilot-instructions.md` is a file that Copilot reads automatically. Whatever conventions you write there, Copilot follows when generating code for this repo.

### Your tasks

1. **Read the instructions:** Open `.github/copilot-instructions.md` — it defines Python style, testing, error handling, and naming conventions.

2. **Test without instructions:** Temporarily rename the file (e.g., add `.bak`). Then ask Chat: *"Write a function to merge two data pipeline outputs into one"*. Note the style Copilot uses.

3. **Test with instructions:** Rename it back. Ask the same question. Compare:
   - Does it use `pathlib.Path`?
   - Does it have Google-style docstrings?
   - Does it use type hints?
   - Does it follow the naming conventions?

4. **Add a new convention:** Add a rule to the instructions file:
   ```markdown
   ## Logging
   - Use `structlog` instead of `logging` for structured log output
   - Always include `event`, `level`, and context fields
   ```
   Then ask Chat to add logging to `DataPipeline.run()`. Does it use `structlog`?

<details>
<summary>💡 Hints</summary>

- Instructions are picked up automatically — no restart needed
- Be specific in your conventions — vague rules get vague results
- Test each convention by asking Copilot to generate code that would exercise it

</details>

---

## Part 2 — Instructions in Action (10 min)

### Your tasks

Now write code with instructions active and see the difference:

1. **Ask Chat:** *"Write tests for the DataPipeline class"*
   - Check: Does it use `pytest` with fixtures (not `unittest`)?
   - Check: Does it use `tmp_path` for file system tests?
   - Check: Does it use factory fixtures?

2. **Ask Chat:** *"Add error handling to _read_csv for malformed files"*
   - Check: Does it use custom exception classes?
   - Check: Does it log before raising?

3. **Inline completion:** Start typing a new method in `DataPipeline`:
   ```python
   def _read_parquet(self, filepath: Path) -> list[dict[str, Any]]:
   ```
   - Check: Does the inline suggestion follow the same patterns as the existing code?

---

## Part 3 — Prompt Files (15 min)

Prompt files are reusable templates stored in `.github/copilot/prompts/`.

### Your tasks

1. **Create a test-generation prompt:** Create `.github/copilot/prompts/generate-tests.prompt.md`:
   ```markdown
   ---
   description: Generate pytest tests following project conventions
   ---
   Generate comprehensive pytest tests for the selected code.

   Requirements:
   - Use factory fixtures (fixture returns a function)
   - Use `tmp_path` for any file system operations
   - Use `pytest.mark.parametrize` for edge cases
   - Include happy path, error cases, and boundary tests
   - Follow Google-style docstrings for test descriptions
   ```

2. **Use the prompt:** Select `validate_batch()` → open Chat → type `/` and select your custom prompt. Compare the output with a regular `/tests` request.

3. **Create a review prompt:** Create `.github/copilot/prompts/code-review.prompt.md`:
   ```markdown
   ---
   description: Review code against project conventions
   ---
   Review the selected code against our project conventions in .github/copilot-instructions.md.

   For each violation, provide:
   1. The specific convention being violated
   2. The line(s) of code
   3. The suggested fix
   ```

4. **Test it:** Select `DataPipeline._transform()` and use your review prompt.

<details>
<summary>💡 Hints</summary>

- Prompt files must end in `.prompt.md`
- They appear in Chat when you type `/`
- The `---` frontmatter block is required with at least a `description`

</details>

---

## Part 4 — Indexed Repos for Context (10 min)

When Copilot indexes your repository, it understands the full codebase — not just the open file.

### Your tasks

1. **Test cross-file awareness:** Without opening `data_pipeline.py`, ask Chat:
   *"What does the DataPipeline class do and what config options does it accept?"*
   - If indexing is active, Copilot answers from the codebase
   - If not, it won't know about your code

2. **Test convention awareness:** Ask Chat:
   *"What are the testing conventions for this project?"*
   - It should reference the `copilot-instructions.md` file

3. **Use `@workspace`:** In Chat, type:
   ```
   @workspace How is error handling done in this project?
   ```
   Copilot searches across all files and summarizes the patterns.

---

## Part 5 — HVE Core Instructions (10 min)

**Prerequisite:** Install [HVE Core](https://marketplace.visualstudio.com/items?itemName=ise-hve-essentials.hve-core) from the VS Code Marketplace.

### Your tasks

1. **Explore HVE instructions:** HVE Core adds 102 auto-applied instructions. Open Copilot Chat and ask:
   *"What coding conventions should I follow for Python in this project?"*
   Notice how HVE instructions supplement your custom ones.

2. **Compare outputs:** Ask Chat to generate the same function twice:
   - Once with HVE Core disabled (disable the extension temporarily)
   - Once with HVE Core enabled
   Compare the quality, structure, and conventions followed.

3. **Explore HVE prompts:** Type `/` in Chat and browse the HVE prompts. Try the RPI (Research → Plan → Implement) workflow:
   *"Use the RPI workflow to add CSV export support to DataPipeline"*

<details>
<summary>💡 Hints</summary>

- HVE instructions and your custom instructions work together — they don't conflict
- HVE prompts appear alongside your custom prompts when you type `/`
- The RPI workflow is three steps: Research the codebase → Plan the changes → Implement

</details>

---

## Lab Complete!

- ✅ Created and tested custom instructions in `.github/copilot-instructions.md`
- ✅ Saw how instructions change Copilot's code generation style
- ✅ Built reusable prompt files for testing and code review
- ✅ Used `@workspace` and indexed repos for cross-file awareness
- ✅ Explored HVE Core instructions and the RPI workflow
