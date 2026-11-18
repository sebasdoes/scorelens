#!/usr/bin/env python3
"""Bar-rhythm checker for Scorelens ABC transcriptions.

Summed durations per bar must match M: per voice. Off-meter bars are where OMR
damage lives (dropped beats, phantom chords, ornament glyphs read as notes).

Handles: notes/chords/rests with int or k/n durations, ties (token '-' suffix,
chord-internal '-' and chord trailing '-'), broken rhythm >/< (single level,
ratio 3/2), volta tokens (|1,3, [|2), grace groups, !decorations!, "annotations"
stripped, structure tokens (| :| |] :: |]) ignored.

Usage: python3 check_rhythm.py file.abc [more.abc ...]
Exit 0 = every bar on meter; exit 1 = violations listed by bar + voice.
Limitations (fine for this repertoire): no tuplets `(n`, no double broken
rhythm `>>`; a tie across a bar skips the next bar's same-pitch continuation.
"""
import re
import sys

VOLTA = re.compile(r"^\[?\|(\d+(?:,\d+)*)")
DURN = re.compile(r"^(?P<h>[\^_=]*[A-Ga-g][,']*|\[[^\]]*\]|[zZ])(?P<d>\d*(?:/\d+)?)")


def tokens_of(line):
    out = []
    for tok in line.split():
        tok = re.sub(r"![^!]*!", "", tok)          # !decoration!
        tok = re.sub(r'"[^"]*"', "", tok)          # "annotation"
        if tok.startswith("{"):                     # grace group (may glue a note)
            tok = re.sub(r"\{[^}]*\}", "", tok)
        if not tok or set(tok) <= set("|[]"):
            continue
        out.append(tok)
    return out


def parse(tok):
    """Return (pitch_id | None(rest) | 'CHORD', units multiplier, tied_out, broken)"""
    m = VOLTA.match(tok)
    if m:
        tok = tok[len(m.group(0)) - 1:]
        if not re.search(r"[A-Ga-gzZ]", tok):
            return None, 0.0, False, ""
    broken = ""
    if tok and tok[-1] in "<>":
        broken, tok = tok[-1], tok[:-1]
    s = tok.rstrip(":|")
    tied = s.endswith("-")
    s = s[:-1] if tied else s
    s = s.rstrip(":|")
    if not s:
        return None, 0.0, tied, broken
    m2 = DURN.match(s)
    if not m2:
        return None, 0.0, tied, broken
    head, dtxt = m2.group("h"), m2.group("d")
    mult = 1.0
    if dtxt:
        if "/" in dtxt:
            n, _, d = dtxt.partition("/")
            mult = (int(n) if n else 1) / (int(d) if d else 2)
        else:
            mult = float(int(dtxt))
    if head.startswith("["):
        inner = head[:-1] if head.endswith("]") else head[1:]
        all_tied = len(re.findall("-", inner)) == len(re.findall(r"[A-Ga-g]", inner))
        return "CHORD", mult, tied or all_tied, broken
    if head[:1] in "zZ":
        return None, mult, tied, broken
    pm = re.match(r"[\^_=]*([A-Ga-g])([,']*)", head)
    pid = pm.group(1).upper() + pm.group(2)
    return pid, mult, tied, broken


def sum_bar(line):
    """Sum ONE &-segment. ABC voice overlay '&' splits a bar into segments,
    each of which must fill the bar individually. Ties count FULL duration —
    a held note fills time even though it is struck only once."""
    total = 0.0
    half_pending = False   # previous token carried '>'
    for tok in tokens_of(line):
        pid, mult, tied, broken = parse(tok)
        if mult == 0.0 and pid is None and not broken:
            continue
        if half_pending:
            total, half_pending = total + mult * 0.5, False
        elif broken == ">":
            total, half_pending = total + mult * 1.5, True
        elif broken == "<":
            total, half_pending = total + mult * 0.5, True
        else:
            total += mult
    return total



def check(text):
    mm = re.search(r"(?m)^M:\s*(\d+)\s*/\s*(\d+)", text)
    meter = (int(mm.group(1)), int(mm.group(2))) if mm else (4, 4)
    lm = re.search(r"(?m)^L:\s*1\s*/\s*(\d+)", text)
    Ld = int(lm.group(1)) if lm else 8
    expect = meter[0] * Ld / meter[1]              # L-units per bar (n/d whole notes x Ld units)
    blocks = re.split(r"(?m)^% bar (\d+)", text)
    problems = []
    for i in range(1, len(blocks), 2):
        num, body = int(blocks[i]), blocks[i + 1]
        for vm in re.finditer(r"(?m)^\[V:(\d+)\](.*)$", body):
            v, line = vm.group(1), vm.group(2)
            segs = re.split(r"\s*&\s*", line.strip().rstrip("|").strip())
            segs = [s for s in segs if s.strip()] or [line]
            for si, seg in enumerate(segs):
                total = sum_bar(seg + " |")
                if abs(total - expect) > 1e-6:
                    problems.append((num, f"{v}[{si}]" if len(segs) > 1 else v, total, expect))
    return problems, expect


def main():
    rc = 0
    for path in sys.argv[1:]:
        text = open(path).read()
        problems, expect = check(text)
        print(f"{'OK ' if not problems else 'BAD'} {path}  (expect {expect:g} L-units per bar)")
        for num, v, total, exp in problems:
            print(f"     bar {num} V:{v}: {total:g} vs {exp:g}")
            rc = 1
    sys.exit(rc)


if __name__ == "__main__":
    main()
