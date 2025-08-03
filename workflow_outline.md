# AI-Native Development Workflow with Cursor  
*(workflow_outline.md)*

**Loom video walkthrough – insert link here →** `https://loom.com/share/your-video-id`

---

## 1 · Why Cursor + Modern Prompt Engineering?

Cursor (an AI-powered code editor based on VS Code with built-in AI features for coding assistance) delivers context-aware code completion, one-click “smart rewrite,” whole-project semantic search, and tight Git integration.  
By layering proven prompting patterns—**zero/few-shot, system / context / role cues, Chain-of-Thought (CoT), Self-Consistency, ReAct, Step-Back, and Automatic Prompt Engineering (APE)**—we shorten feedback loops, curb hallucinations, and make large-scale modernizations (e.g., *monolith → modules*) deterministic and auditable.

---

## 2 · End-to-End Workflow (10 Steps)

| # | Cursor Action  (🖥️) | Prompt-Engineering Booster  💡 |
|---|---------------------|------------------------------|
| **0** | *Bootstrap*: open repo, `git checkout -b refactor-monolith`, enable code-index, add **Rules** (“hash passwords, no globals”). | Add a **system prompt** describing target architecture so every AI edit stays aligned. |
| **1** | *Baseline analysis*: Chat → “Summarize major components & code smells.” | Zero-shot, **temperature 0.2** for factual scans. |
| **2** | *Extract auth*: highlight functions → Inline Edit (`⌘/Ctrl K`) → create `auth.py`. | **Few-shot**: show one extraction example, then ask AI to repeat pattern. |
| **3** | *Add SQLite*: Chat → “Create `database.py` with CRUD + SHA-256 password hashing.” | **Contextual prompt** – inject path to `auth.py` so types match. |
| **4** | *Build Flask API*: Chat → “You are a senior Python API engineer—generate JSON routes /register /login /get_user.” | **Role prompting** ensures style & PEP 8. |
| **5** | *Global sweep*: Agent (`⌃/Ctrl I`) → “Replace all `users` dict references with DB calls.” | **Step-Back**: first ask AI for a migration plan, then feed that plan back for execution. |
| **6** | *Debug tests*: paste failing stack trace → “Let’s think step by step—why does test X fail?” | **Chain-of-Thought** for transparent reasoning. |
| **7** | *Stabilize logic*: run same CoT prompt 5 ×, majority-vote result. | **Self-Consistency** improves reliability. |
| **8** | *External look-ups*: terminal + ReAct loop: *reason → `curl` → observe → reason*. | **ReAct** couples reasoning with live tool output. |
| **9** | *Commit & doc*: AI commit-msg; Chat → “Draft README architecture section.” | Log every key prompt in `ai_interactions.log` per APE best practice. |

---

## 3 · Prompt Crafting Cheat-Sheet

* **Hierarchy:** **System → Context → Role** clarifies intent.  
* **Sampling defaults:** `temperature 0.2` / `top-p 0.95` for analysis; bump temperature for creative docs.  
* **Zero-shot first, escalate to few-shot** if structure drifts.  
* **APE loop:** “Generate 5 alternative prompts that achieve X; rank by clarity.”  
* **Document everything**—versioned prompt table ensures reproducibility.

---

## 4 · Where Prompt Techniques Accelerate Modernization

| Pain-Point | Technique(s) | Pay-off |
|------------|--------------|---------|
| Safely split monolith | Few-shot + Step-Back | Repeatable extraction pattern, lower risk |
| Secure data layer | System prompt with security rule | Consistent hashing, no plaintext |
| Ambiguous legacy logic | CoT + Self-Consistency | Transparent reasoning, stable outcomes |
| Unknown external APIs | ReAct | Automates research & integration |

---

## 5 · Efficiency · Accuracy · Iteration

Cursor automates boilerplate while structured prompting minimizes hallucinations and enforces style.  
Small, AI-assisted iterations—each validated by tests—yield a modular, well-documented codebase in **hours instead of days**, with every architectural change traceable via logged prompts and Git commits.

---

### References

1. Cursor Documentation – <https://cursor.sh/docs>  
2. Google Cloud. **Prompt Engineering v4** (PDF, Sept 2024)  
3. DataCamp Blog: *“Getting Started with Cursor”*, 12 Jan 2025  

---
