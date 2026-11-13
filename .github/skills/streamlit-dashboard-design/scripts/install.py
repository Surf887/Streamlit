"""Copy the design system into a Streamlit project. Never overwrites existing files,
unless --update is given, which refreshes the ui_kit/*.py files only (use it after the
skill itself has been updated; it replaces any local edits to ui_kit).

Usage (from the project root):
    python .github/skills/streamlit-dashboard-design/scripts/install.py [target_dir] [--update]

Creates in the target (default: current directory):
    .streamlit/config.toml     theme + bundled font declaration
    static/InterVariable.woff2 the font (plus its licence)
    ui_kit/                    components, chart recipes, tokens
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
PLAN = [
    ("streamlit/config.toml", ".streamlit/config.toml"),
    ("static/InterVariable.woff2", "static/InterVariable.woff2"),
    ("static/Inter-LICENSE.txt", "static/Inter-LICENSE.txt"),
    ("ui_kit/__init__.py", "ui_kit/__init__.py"),
    ("ui_kit/theme.py", "ui_kit/theme.py"),
    ("ui_kit/components.py", "ui_kit/components.py"),
    ("ui_kit/charts.py", "ui_kit/charts.py"),
]


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--update"]
    update = "--update" in sys.argv[1:]
    target = Path(args[0] if args else ".").resolve()
    skipped = []
    for src, dst in PLAN:
        out = target / dst
        if out.exists() and update and dst.startswith("ui_kit/"):
            shutil.copyfile(ASSETS / src, out)
            print(f"  updated: {dst}")
            continue
        if out.exists():
            skipped.append(dst)
            print(f"  exists, left untouched: {dst}")
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ASSETS / src, out)
        print(f"  created: {dst}")
    if ".streamlit/config.toml" in skipped:
        print("\nNOTE: .streamlit/config.toml already exists. Merge the [server], [client], "
              "[[theme.fontFaces]] and [theme*] sections from\n  "
              f"{ASSETS / 'streamlit/config.toml'}\ninto it by hand.")
    try:
        import streamlit
        v = tuple(int(p) for p in streamlit.__version__.split(".")[:2])
        print(f"\nStreamlit {streamlit.__version__} found.")
        if v < (1, 46):
            print("WARNING: the design system needs Streamlit 1.46 or newer "
                  "(tested on 1.67). Upgrade: pip install -U streamlit")
    except ImportError:
        print("\nStreamlit is not installed: pip install streamlit plotly pandas")
    try:
        import plotly  # noqa: F401
    except ImportError:
        print("Plotly is not installed: pip install plotly")
    print("\nDone. Reference app: "
          f"{ASSETS / 'example'}  (copy app.py, sample_data.py and views/ to try it)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
