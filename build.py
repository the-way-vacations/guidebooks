#!/usr/bin/env python3
"""Build per-channel guest guides from one source.

src/<name>.html may contain channel blocks:
    <!-- @only direct --> ... <!-- @end -->
    <!-- @only airbnb --> ... <!-- @end -->
Untagged content goes to every channel.

Outputs to _site/:
    <name>.html          direct channel (Vrbo + direct site), same URL as before
    <name>-airbnb.html   airbnb channel
Every other top-level file (index.html, heaven-on-surf.html, ...) is copied as is.

The airbnb output is checked against policy/airbnb-banned.txt; any hit fails the build.
Usage: python build.py
"""
import re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC, OUT = ROOT / "src", ROOT / "_site"
CHANNELS = {"direct": "{name}.html", "airbnb": "{name}-airbnb.html"}
BLOCK = re.compile(r"<!-- @only (\w+) -->(.*?)<!-- @end -->", re.S)
COPY_SKIP = {"build.py", "README.md", "AGENTS.md", "_site", "src", "policy", ".git", ".github"}


def render(text, channel):
    def sub(m):
        if m.group(1) not in CHANNELS:
            sys.exit(f"unknown channel '{m.group(1)}'")
        return m.group(2) if m.group(1) == channel else ""
    out = BLOCK.sub(sub, text)
    if "@only" in out or "@end" in out:
        sys.exit("unbalanced @only/@end marker")
    return out


def banned_patterns(channel):
    f = ROOT / "policy" / f"{channel}-banned.txt"
    if not f.exists():
        return []
    lines = [l.strip() for l in f.read_text(encoding="utf-8").splitlines()]
    return [l for l in lines if l and not l.startswith("#")]


def lint(path, channel):
    text = path.read_text(encoding="utf-8")
    visible = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    errors = []
    for pat in banned_patterns(channel):
        for m in re.finditer(pat, visible, re.I):
            line = visible.count("\n", 0, m.start()) + 1
            errors.append(f"{path.name}:{line}: '{m.group(0)}' matches banned pattern /{pat}/")
    return errors


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for f in ROOT.iterdir():
        if f.name in COPY_SKIP or f.name.startswith("."):
            continue
        if f.is_file():
            shutil.copy2(f, OUT / f.name)
    (OUT / ".nojekyll").touch()

    errors = []
    for src in sorted(SRC.glob("*.html")):
        text = src.read_text(encoding="utf-8")
        for channel, pattern in CHANNELS.items():
            dest = OUT / pattern.format(name=src.stem)
            dest.write_text(render(text, channel), encoding="utf-8")
            errors += lint(dest, channel)
            print(f"built {dest.relative_to(ROOT)}")
    if errors:
        print("\nPOLICY CHECK FAILED:\n" + "\n".join(errors))
        sys.exit(1)
    print("policy check passed")


if __name__ == "__main__":
    main()
