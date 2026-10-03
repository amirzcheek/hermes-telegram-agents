#!/usr/bin/env python3
"""Install the four agents into existing Hermes profiles.

For each agent (coordinator, researcher, coder, studybuddy) this script:
  1. renders SOUL.md and the skills with the bot usernames from team.json;
  2. deep-merges agents/<name>/config.yaml into the profile's config.yaml;
  3. checks (read-only) that the profile's .env has the keys the agent needs.

It never writes tokens or keys. Existing files are backed up as *.bak.

Usage:
    python scripts/install.py                # uses ~/.hermes
    python scripts/install.py --hermes-home /path/to/.hermes
    python scripts/install.py --dry-run
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ["coordinator", "researcher", "coder", "studybuddy"]
OWN_TOPIC = {"coordinator": None, "researcher": "RESEARCH", "coder": "CODE", "studybuddy": "STUDY"}
REQUIRED_ENV = [
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_ALLOWED_USERS",
    "TELEGRAM_GROUP_ALLOWED_CHATS",
    "TELEGRAM_ALLOW_BOTS",
]


def render(text, names):
    for key, value in names.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def deep_merge(base, overlay):
    """Overlay wins. Dicts merge recursively, everything else is replaced."""
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def backup(path):
    if path.exists():
        shutil.copy2(path, path.with_name(path.name + ".bak"))


def env_keys(env_path):
    keys = set()
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                name, value = line.split("=", 1)
                if value.strip():
                    keys.add(name.strip())
    return keys


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--hermes-home", default=str(Path.home() / ".hermes"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    home = Path(args.hermes_home).expanduser()
    team = json.loads((ROOT / "team.json").read_text(encoding="utf-8"))
    names = {k: v.lstrip("@") for k, v in team.items() if k.endswith("_BOT")}
    # Optional forum topics: every agent ignores the topics that belong to
    # another specialist. TEAM (and anything not listed) stays open to all.
    topics = {k: v for k, v in (team.get("TOPICS") or {}).items()
              if not k.startswith("_") and v is not None}
    if len(names) != len(AGENTS) or len(set(names.values())) != len(AGENTS):
        sys.exit(f"team.json must contain {len(AGENTS)} different bot usernames.")

    try:
        import yaml
    except ImportError:
        yaml = None
        print("! PyYAML not found: SOUL.md and skills will be installed, but merge the\n"
              "  config overlays by hand (or `pip install pyyaml` and rerun).\n")

    workspace = Path.home() / "hermes-agents-workspace" / "coder"
    problems = []

    for agent in AGENTS:
        src = ROOT / "agents" / agent
        dst = home / "profiles" / agent
        print(f"== {agent} -> {dst}")
        if not dst.is_dir():
            problems.append(f"{agent}: profile missing. Run: hermes profile create {agent} --clone")
            print("   profile not found, skipped")
            continue

        # 1. SOUL.md
        soul = render((src / "SOUL.md").read_text(encoding="utf-8"), names)
        if "{{" in soul:
            sys.exit(f"Unrendered placeholder left in {agent}/SOUL.md")
        if not args.dry_run:
            backup(dst / "SOUL.md")
            (dst / "SOUL.md").write_text(soul, encoding="utf-8")
        print("   SOUL.md installed")

        # 2. skills
        for skill_file in (src / "skills").glob("*/SKILL.md") if (src / "skills").is_dir() else []:
            target = dst / "skills" / skill_file.parent.name / "SKILL.md"
            if not args.dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(render(skill_file.read_text(encoding="utf-8"), names), encoding="utf-8")
            print(f"   skill installed: {skill_file.parent.name}")

        # 3. config overlay
        if yaml is not None:
            overlay = yaml.safe_load((src / "config.yaml").read_text(encoding="utf-8")) or {}
            ignored = [tid for name, tid in topics.items()
                       if name != "TEAM" and name != OWN_TOPIC[agent]]
            if ignored:
                overlay.setdefault("telegram", {})["ignored_threads"] = ignored
                print(f"   ignores topics: {ignored}")
            if agent == "studybuddy" and "STUDY" in topics:
                # topics share one session by default; keep one per student
                overlay["thread_sessions_per_user"] = True
            if agent == "coder":
                overlay["terminal"]["cwd"] = str(workspace)
                if not args.dry_run:
                    workspace.mkdir(parents=True, exist_ok=True)
            cfg_path = dst / "config.yaml"
            current = {}
            if cfg_path.exists():
                current = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            merged = deep_merge(current, overlay)
            if not args.dry_run:
                backup(cfg_path)
                cfg_path.write_text(
                    yaml.safe_dump(merged, sort_keys=False, allow_unicode=True), encoding="utf-8"
                )
            print("   config.yaml merged (previous version saved as config.yaml.bak)")

        # 4. secrets check (presence only, values are never printed)
        missing = [k for k in REQUIRED_ENV if k not in env_keys(dst / ".env")]
        if missing:
            problems.append(f"{agent}: add to {dst / '.env'}: {', '.join(missing)}")

    print()
    if problems:
        print("Still to do:")
        for p in problems:
            print("  - " + p)
    else:
        print("All profiles are configured.")
    print("\nNext: restart the gateway (hermes gateway restart, or stop and run `hermes gateway`)\n"
          "and check that `hermes gateway status` lists all four profiles.")


if __name__ == "__main__":
    main()
