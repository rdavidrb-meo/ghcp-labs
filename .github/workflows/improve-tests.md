---
name: improve-tests
description: >
  Automatically identify and fill coverage gaps in the lab1 test suite.
  Runs pytest --cov, finds uncovered lines, and writes new tests.

on:
  slash_command: improve-tests

---

steps:
  - name: Run coverage analysis
    run: |
      cd lab1
      pip install -r requirements.txt
      pytest tests/ --cov=order_processor --cov-report=json --cov-report=term-missing -v

  - name: Identify uncovered lines
    prompt: |
      Read the coverage JSON report. List all lines in order_processor.py
      that are NOT covered. For each uncovered line, determine what test
      case would exercise it.

  - name: Write missing tests
    prompt: |
      For each uncovered code path you identified, write a pytest test
      that covers it. Follow the existing test patterns:
      - Use unittest.mock.patch for external calls
      - Use in-memory SQLite for DB tests
      - Use AsyncMock for async functions
      - Use the make_order factory pattern from conftest.py
      Add the tests to the appropriate test file.

  - name: Verify coverage improved
    run: |
      cd lab1
      pytest tests/ --cov=order_processor --cov-fail-under=90 -v
