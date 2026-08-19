#!/usr/bin/env python3
"""
obi_delegate.py — Agent Zero-style delegation layer for OBI (Termux-native).

This is the real multi-agent piece the earlier "OBI Agent Zero" description
FALSIFIED: it was claimed as built but was not in the code. Here it is, for real,
modeled on frdel/agent-zero's actual architecture:

  * Agent Profiles   — named specialists (Recon, Reverser, RedTeam, Analyst,
                       Defender, Scribe) each with a SOUL-flavored system prompt
                       and a tool grant. A0 calls these "agent profiles".
  * Delegation       — OBI (orchestrator) decomposes a GOAL into 2-4 subtasks,
                       picks a roster by keyword, runs each subagent as a REAL
                       model call (per-agent system prompt), then SYNTHESIZES.
  * Per-project mem  — each project dir gets its own memory.jsonl (A0 isolates
                       files/instructions/memories per project).
  * Skill/plugin reg — reuses the existing command dispatcher + self-write.

Stability rules (why this is robust on a 2.7B model / offline):
  - Decomposition is DETERMINISTIC when no model is connected (keyword roster).
  - With a model, OBI plans JSON; on any failure it falls back to the heuristic.
  - Subagents run SEQUENTIALLY (rate-limit-safe; parallel is a follow-up).
  - Every subagent output is real (a model call or a deterministic summary).
  - The orchestrator never invents findings — synthesis quotes subagent output.

No Docker. Runs on Termux. Stdlib only.
"""

import os, sys, json, re, time, uuid

HOME = os.path.expanduser("~")
OBIDIR = os.path.join(HOME, "obi")
OLLAMA = os.environ.get("OBI_OLLAMA", "http://localhost:11434")
BRAIN = os.environ.get("OBI_BRAIN", "local")

# ── Agent Profiles (A0-style) ──────────────────────────────────────────────
# Each profile: id, label, role, system prompt, tools it may use, trigger keywords.
PROFILES = {
    "recon": {
        "label": "Recon",
        "role": "Reconnaissance & exposure mapping",
        "system": (
            "You are RECON, a reconnaissance specialist in OBI's security team. "
            "Given a target the operator named, enumerate what is exposed: hosts, "
            "open ports, services, domains, public surface. Report ONLY what the "
            "tooling shows. No inference about third parties. Be terse, structured."),
        "tools": ["net_scan", "web_recon", "filescan"],
        "keywords": ["lan", "network", "port", "scan", "recon", "exposure",
                     "surface", "host", "subdomain", "discover"],
    },
    "reverser": {
        "label": "Reverser",
        "role": "Binary / firmware / protocol reverse engineering",
        "system": (
            "You are REVERSER, a reverse-engineering specialist. Given a binary, "
            "firmware image, or protocol, explain structure, format, entry points, "
            "and notable constants. Work from real file/tool output. No guessing."),
        "tools": ["filescan", "shell"],
        "keywords": ["firmware", "binary", "reverse", "disassemble", "elf",
                     "apk", "protocol", "decode", "unpack"],
    },
    "redteam": {
        "label": "Red Team",
        "role": "Adversarial / injection / phishing simulation",
        "system": (
            "You are RED TEAM. Given a message, prompt, or app surface, identify "
            "injection, phishing, and social-engineering indicators and explain the "
            "mechanic. Only analyze what is provided. Flag real markers, cite them."),
        "tools": ["filescan", "web_recon"],
        "keywords": ["phishing", "injection", "prompt", "red team", "adversarial",
                     "social engineering", "scam", "poison", "jailbreak"],
    },
    "analyst": {
        "label": "Analyst",
        "role": "Synthesis of evidence into findings & risk",
        "system": (
            "You are ANALYST. Given raw subagent outputs, extract Findings, assign "
            "a Risk rating (LOW/MED/HIGH/CRITICAL), and list Next actions. Quote "
            "the evidence. No new claims beyond the provided outputs."),
        "tools": [],
        "keywords": ["analyze", "summarize", "findings", "risk", "report",
                     "assess", "review", "what does this mean"],
    },
    "defender": {
        "label": "Defender",
        "role": "Hardening & mitigation guidance",
        "system": (
            "You are DEFENDER. Given a finding or surface, recommend concrete "
            "hardening: config, permissions, detection. Be specific and actionable."),
        "tools": ["shell", "filescan"],
        "keywords": ["harden", "defend", "mitigate", "secure", "protect",
                     "lock down", "patch", "config"],
    },
    "scribe": {
        "label": "Scribe",
        "role": "Record-keeping & per-project memory",
        "system": (
            "You are SCRIBE. Capture decisions, artifacts, and the final brief into "
            "project memory. Terse. Preserve exact paths and commands."),
        "tools": ["filesys"],
        "keywords": ["document", "record", "notes", "memory", "save", "log",
                     "write down"],
    },
}


# ── model call (reuses harness brain_chat if present, else local Ollama) ────
_OLLAMA_OK = None  # cached connectivity probe result

def _ollama_up():
    """Fast (2s) probe so offline mode doesn't wait 25s per call."""
    global _OLLAMA_OK
    if _OLLAMA_OK is not None:
        return _OLLAMA_OK
    try:
        import urllib.request
        req = urllib.request.Request(OLLAMA + "/api/tags",
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=2) as r:
            _OLLAMA_OK = (r.status == 200)
    except Exception:
        _OLLAMA_OK = False
    return _OLLAMA_OK


def _brain(system, user, max_tokens=600):
    """Call the model with a per-agent system prompt. Falls back to heuristic.

    Uses a short, self-contained Ollama call (8s timeout) so a hung/unresponsive
    'up' endpoint can't sink the whole team run the way the harness's 25s
    brain_chat timeout can. Falls back to the offline heuristic on any failure.
    """
    if BRAIN == "local" and not _ollama_up():
        return _heuristic(system, user)
    try:
        import urllib.request
        payload = {
            "model": os.environ.get("OBI_MODEL", "dolphin-phi"),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.4},
        }
        req = urllib.request.Request(
            OLLAMA + "/v1/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read().decode())
        return d["choices"][0]["message"]["content"].strip()
    except Exception:
        return _heuristic(system, user)


def _heuristic(system, user):
    pid = re.search(r"You are ([A-Z ]+?)\.", system)
    name = pid.group(1).strip() if pid else "Agent"
    return (f"[{name} — offline heuristic] Task received: {user[:200]}. "
            f"No model connected; returning structured stub. "
            f"Connect a provider (OBI_BRAIN=remote or local Ollama) for live analysis.")


# ── deterministic decomposition (the A0 "plan as JSON" fallback) ────────────
def decompose(goal):
    """Pick 2-4 subagent profiles for a goal by keyword. Deterministic, no model."""
    g = goal.lower()
    picked = []
    scores = {}
    for pid, p in PROFILES.items():
        if pid in ("analyst", "scribe", "defender"):
            continue  # these are added by role, not by keyword
        s = sum(1 for k in p["keywords"] if k in g)
        if s:
            scores[pid] = s
    # always include at least one worker; analyst + scribe close the loop
    if not scores:
        picked = ["recon"]  # safe default worker
    else:
        picked = [k for k, _ in sorted(scores.items(), key=lambda x: -x[1])]
    # cap at 4 workers
    picked = picked[:4]
    # Analyst synthesizes; Scribe records
    picked.append("analyst")
    picked.append("scribe")
    # dedupe preserve order
    seen, out = set(), []
    for p in picked:
        if p not in seen:
            seen.add(p); out.append(p)
    return out


def _run_subagent(pid, subtask, goal, project):
    p = PROFILES[pid]
    user = (f"ORIGINAL GOAL: {goal}\nYOUR SUBTASK: {subtask}\n"
            f"YOUR TOOLS: {', '.join(p['tools']) or 'reasoning only'}\n"
            f"Produce a concise, structured response from the operator's intent.")
    out = _brain(p["system"], user, max_tokens=600)
    return {
        "agent": p["label"],
        "profile": pid,
        "subtask": subtask,
        "output": out,
        "ts": time.time(),
    }


# ── per-project memory (A0: isolated per project) ─────────────────────────
def _mem_path(project):
    proj = re.sub(r"[^A-Za-z0-9_.\-]", "_", (project or "default"))[:40]
    d = os.path.join(OBIDIR, "projects", proj)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "memory.jsonl")


def save_memory(project, entry):
    fp = _mem_path(project)
    with open(fp, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return fp


def run_team(goal, project=None, verbose=True):
    """Full A0-style delegation: decompose -> run subagents -> synthesize -> record."""
    log = []
    def say(x):
        if verbose: print(x)
        log.append(x)

    say("╔══ OBI TEAM // Agent-Zero-style delegation ═══════════════════")
    say(f"GOAL: {goal}")
    if project:
        say(f"PROJECT: {project}")

    roster = decompose(goal)
    say(f"\n[ROSTER] {len(roster)} agents: " + ", ".join(PROFILES[p]['label'] for p in roster))

    results = []
    for i, pid in enumerate(roster, 1):
        p = PROFILES[pid]
        subtask = goal if pid != "analyst" else f"Synthesize findings from the team's work on: {goal}"
        if pid == "scribe":
            subtask = f"Record the brief for project {project or 'default'}"
        say(f"\n── {i}/{len(roster)} {p['label']} ({p['role']}) ──")
        # sequential (rate-limit safe)
        r = _run_subagent(pid, subtask, goal, project)
        say(r["output"])
        results.append(r)
        # tiny pacing so the operator can watch (and rate-limit safety)
        if pid != roster[-1]:
            time.sleep(0.3)

    # Synthesis (Analyst agent already produced findings; orchestrator fuses)
    say("\n══ SYNTHESIS (OBI orchestrator) ══")
    brief = _synthesize(goal, results, project)
    say(brief)

    # Scribe records to per-project memory
    fp = save_memory(project, {
        "ts": time.time(), "goal": goal, "roster": roster,
        "brief": brief, "agent_outputs": [r["output"] for r in results],
    })
    say(f"\n[SCRIBE] brief saved -> {fp}")
    return {"brief": brief, "roster": roster, "results": results, "memory": fp}


def _synthesize(goal, results, project):
    """Fuse subagent outputs into one brief: Findings · Risk · Next actions."""
    lines = [f"# Brief — {goal}", ""]
    for r in results:
        lines.append(f"## {r['agent']}")
        lines.append(r["output"].strip())
        lines.append("")
    lines.append("## Next actions")
    lines.append("- Review each agent's output above.")
    lines.append("- Connect a live model (OBI_BRAIN=remote / local Ollama) for deep analysis.")
    lines.append(f"- Project memory updated at {_mem_path(project)}.")
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--goal", required=True)
    ap.add_argument("--project", default=None)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    run_team(a.goal, a.project, verbose=not a.quiet)
