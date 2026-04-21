# Lab 07 — Security in the SDLC

**Duration:** ~1 hour  
**SDLC Phase:** Security Gate  
**Autonomy Level:** 🔴 Agent scans, enforces, gates  
**Prerequisites:** Lab 06 completed, Python 3.10+, VS Code with GitHub Copilot, [HVE Core](https://marketplace.visualstudio.com/items?itemName=ise-hve-essentials.hve-core) extension (optional)

---

## What You'll Practice

| Part | Skill | Time | Copilot Feature |
|------|-------|------|-----------------|
| **1** | Find security vulnerabilities | 15 min | Chat security review |
| **2** | Fix OWASP Top 10 issues | 20 min | Chat + inline + Agent Mode |
| **3** | Write security-focused tests | 10 min | Chat `/tests` with security prompt |
| **4** | Automate with CodeQL & HVE OWASP skill | 10 min | GitHub Actions + HVE Core |
| **5** | Secure-by-default patterns | 5 min | Chat best practices |

---

## Setup

```bash
cd lab07
pip install pytest bcrypt
```

---

## The Scenario

You've inherited `auth_service.py` — a user authentication and file upload service. It has **8 security vulnerabilities** spanning the OWASP Top 10. Your job: find them all, fix them, and write tests to prevent regressions.

---

## ⚠️ Important

This code is **intentionally vulnerable** for educational purposes. Never deploy code like this. The vulnerabilities are clearly marked with comments in the solutions.

---

## Part 1 — Find Security Vulnerabilities (15 min)

### Your tasks

1. **Full security audit:** Select the entire file → Chat → prompt:
   ```
   Perform a security audit of this code. List every vulnerability you find,
   categorized by OWASP Top 10 category. For each, explain the risk and
   how an attacker could exploit it.
   ```

2. **Targeted review:** Ask about specific areas:
   ```
   Is the login function vulnerable to SQL injection? Show me an attack payload.
   ```
   ```
   Is the password storage secure? What should be used instead?
   ```
   ```
   Are there any path traversal vulnerabilities in the file operations?
   ```

3. **Check your list:** You should find at least these 8:

   | # | Vulnerability | OWASP Category |
   |---|--------------|----------------|
   | 1 | SQL injection in `login()` and `search_users()` | A03: Injection |
   | 2 | MD5 password hashing with no salt | A02: Cryptographic Failures |
   | 3 | Path traversal in `upload_file()` and `read_file()` | A01: Broken Access Control |
   | 4 | Command injection in `get_file_info()` and `compress_file()` | A03: Injection |
   | 5 | Hardcoded secrets (API keys, passwords) | A02: Cryptographic Failures |
   | 6 | Insecure deserialization with `pickle` | A08: Software & Data Integrity Failures |
   | 7 | Missing access control in `get_user_profile()` and `delete_user()` | A01: Broken Access Control |
   | 8 | Information exposure in `handle_error()` | A05: Security Misconfiguration |

---

## Part 2 — Fix the Vulnerabilities (20 min)

### Your tasks

Fix each vulnerability. Use Copilot Chat for guidance:

**Fix 1 — SQL Injection:**
```
Fix the SQL injection in login() and search_users() using parameterized queries.
```

**Fix 2 — Password Hashing:**
```
Replace MD5 with bcrypt for password hashing. Add salt automatically.
```

**Fix 3 — Path Traversal:**
```
Sanitize filenames to prevent path traversal. Use pathlib to resolve
and validate the path stays within UPLOAD_DIR.
```

**Fix 4 — Command Injection:**
```
Replace shell=True subprocess calls with safe alternatives.
Use shlex or pass arguments as a list.
```

**Fix 5 — Hardcoded Secrets:**
```
Move all secrets to environment variables. Add a .env.example file.
```

**Fix 6 — Insecure Deserialization:**
```
Replace pickle with json for session serialization.
```

**Fix 7 — Access Control:**
```
Add authorization checks: users can only view their own profile
unless they have the 'admin' role. Only admins can delete users.
```

**Fix 8 — Information Exposure:**
```
Fix handle_error to log the full details server-side but return
only a generic error message to the client.
```

<details>
<summary>💡 Hints</summary>

- For bcrypt: `bcrypt.hashpw(password.encode(), bcrypt.gensalt())`
- For path traversal: `resolved = Path(UPLOAD_DIR).resolve() / Path(filename).name`
- For command injection: `subprocess.run(["file", filepath], capture_output=True)`
- For secrets: `os.getenv("API_KEY")` with a fallback that raises if not set

</details>

---

## Part 3 — Security-Focused Tests (10 min)

### Your tasks

Write tests that specifically verify the vulnerabilities are fixed:

1. **SQL injection test:** Pass `' OR '1'='1` as username — should NOT return a user
2. **Password test:** Verify passwords are hashed with bcrypt, not MD5
3. **Path traversal test:** Pass `../../etc/passwd` as filename — should be rejected
4. **Command injection test:** Pass `; rm -rf /` as filename — should be safe
5. **Access control test:** Non-admin user should NOT be able to delete other users

Use Agent Mode:
```
Write security regression tests for auth_service.py. Each test should verify
that a specific vulnerability is fixed. Include SQL injection, path traversal,
command injection, and access control tests.
```

---

## Part 4 — Automated Security Scanning (10 min)

### 4a: CodeQL workflow

Create `.github/workflows/codeql.yml`:

Ask Chat:
```
Create a GitHub Actions workflow that runs CodeQL analysis on every PR.
Target Python. Include the default security and quality query suites.
```

### 4b: HVE Core OWASP skill (if installed)

If you have HVE Core installed, try the OWASP CI/CD skill:

1. Open Chat → select the OWASP-related agent or prompt
2. Ask it to review `auth_service.py`
3. Compare its findings with what you found manually

---

## Part 5 — Secure-by-Default Patterns (5 min)

### Your task

Ask Copilot Chat:
```
Based on the vulnerabilities we found and fixed, generate a
security checklist for Python web applications that I can add
to our copilot-instructions.md file. This should help Copilot
generate secure code by default.
```

Add the output to `.github/copilot-instructions.md` so future code generation follows secure patterns.

---

## Solutions

- `solutions/auth_service_fixed.py` — fixed version with all 8 vulnerabilities resolved
- `solutions/test_security.py` — 24 security regression tests (run with `pytest solutions/ -v`)

---

## Lab Complete!

- ✅ Identified 8 OWASP Top 10 vulnerabilities using Copilot security review
- ✅ Fixed SQL injection, weak crypto, path traversal, command injection, and more
- ✅ Wrote security regression tests to prevent re-introduction
- ✅ Set up automated CodeQL scanning in CI
- ✅ Created secure-by-default coding instructions for Copilot
