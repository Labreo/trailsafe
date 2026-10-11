#!/usr/bin/env python3
"""Linter script enforcing strict deslop-copyeditor rules for submission text.
Checks:
1. Banned words: controlled, precise, deliberate, measured, efficient, specific, particular, quietly, hum, fluorescent, ozone, architecture, system, the way, with the, somehow, rhythm, catalogue.
2. Negative pairings: 'Not X. Not Y. Just Z', 'It wasn't X, it was Y'.
3. Staccato prose: Sentences < 3 words, or 2 consecutive sentences < 5 words.
4. Bloat: Sentences >= 30 words.
5. Tentative modifiers: almost, seemed to, looked like, something like, as if to.
"""

import re
import sys
from pathlib import Path

BANNED_WORDS = [
    "controlled", "precise", "deliberate", "measured", "efficient",
    "specific", "particular", "quietly", "hum", "fluorescent", "ozone",
    "architecture", "system", "the way", "with the", "somehow",
    "rhythm", "catalogue"
]

TENTATIVE_MODIFIERS = [
    "almost", "seemed to", "looked like", "something like", "as if to"
]

def check_text(content: str):
    # Strip markdown code blocks, links, tables, and frontmatter
    lines = content.splitlines()
    clean_lines = []
    in_code = False
    in_frontmatter = False
    frontmatter_count = 0

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "---":
            frontmatter_count += 1
            if frontmatter_count <= 2:
                in_frontmatter = (frontmatter_count == 1)
                continue
        if in_frontmatter:
            continue
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        # Skip markdown table rows and headings
        if stripped.startswith("|") or stripped.startswith("#") or stripped.startswith("<!--") or stripped.startswith("{%"):
            continue
        clean_lines.append((idx + 1, line))

    errors = []

    # Check banned words and tentative modifiers
    for line_num, line in clean_lines:
        lower_line = line.lower()
        for bw in BANNED_WORDS:
            # Word boundary check
            pattern = rf"\b{re.escape(bw)}\b"
            if re.search(pattern, lower_line):
                errors.append(f"Line {line_num}: BANNED WORD '{bw}' found in: '{line.strip()}'")

        for tm in TENTATIVE_MODIFIERS:
            pattern = rf"\b{re.escape(tm)}\b"
            if re.search(pattern, lower_line):
                errors.append(f"Line {line_num}: TENTATIVE MODIFIER '{tm}' found in: '{line.strip()}'")

        # Check negative pairings like 'not x. not y'
        if re.search(r"\bnot\s+[^.!?]+[.!?]\s+not\s+[^.!?]+[.!?]\s+(just|but)\b", lower_line):
            errors.append(f"Line {line_num}: BANNED NEGATIVE PAIRING: '{line.strip()}'")
        if re.search(r"\bit\s+wasn['’]t\s+[^,]+,\s*it\s+was\b", lower_line):
            errors.append(f"Line {line_num}: BANNED CONTRASTING NEGATION: '{line.strip()}'")

    # Split into sentences for length and staccato checks
    # Treat double newlines, headings, and images as sentence boundaries
    full_text = "\n\n".join(line for _, line in clean_lines)
    # Remove markdown link formatting e.g. [text](url) -> text
    full_text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", "\n\n", full_text)
    full_text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", full_text)
    full_text = re.sub(r"[*_`#>]", "", full_text)

    # Split paragraphs first
    paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]
    sentences = []
    for p in paragraphs:
        # Split sentences by . ! ?
        p_clean = re.sub(r"\n+", " ", p)
        raw_s = re.split(r"(?<=[.!?])\s+", p_clean)
        for s in raw_s:
            s_str = s.strip()
            if s_str and not s_str.startswith("-") and not s_str.startswith("*"):
                sentences.append(s_str)

    prev_short = False
    for s in sentences:
        words = s.split()
        word_count = len(words)
        if word_count == 0:
            continue
        # Ignore bullet points or single digits
        if word_count < 3 and words[0] not in [">", "-", "*", "1.", "2.", "3.", "4."]:
            errors.append(f"STACCATO (< 3 words, count={word_count}): '{s}'")
        if word_count < 5:
            if prev_short:
                errors.append(f"CONSECUTIVE SHORT (< 5 words): '{s}'")
            prev_short = True
        else:
            prev_short = False

        if word_count >= 30:
            errors.append(f"RUN-ON / BLOAT (>= 30 words, count={word_count}): '{s}'")

    return errors

if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/SUBMISSION_POST.md")
    content = path.read_text(encoding="utf-8")
    errs = check_text(content)
    if errs:
        print(f"Found {len(errs)} deslop issues in {path}:")
        for e in errs[:25]:
            print(" -", e)
        if len(errs) > 25:
            print(f" ... and {len(errs) - 25} more.")
        sys.exit(1)
    else:
        print(f"SUCCESS: {path} passed all deslop-copyeditor checks!")
