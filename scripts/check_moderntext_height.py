"""ModernText の Height が Size に対して十分か（Height >= Size*1.5+10）を全画面でチェックする。
SCREEN_RENDERING_RULES.md 9章 ModernText の早見表に対応。違反があるとPlayモードでのみスクロールバーが出る。

使い方: python scripts/check_moderntext_height.py
"""
import re
import glob
import os

SRC = os.path.join(os.path.dirname(__file__), "..", "src")


def min_height(size):
    return size * 1.5 + 10


def find_violations(src_dir):
    violations = []
    for path in glob.glob(os.path.join(src_dir, "*.pa.yaml")):
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()

        i = 0
        n = len(lines)
        while i < n:
            m = re.search(r"^(\s*)Control:\s*ModernText\s*$", lines[i])
            if m:
                control_indent = len(m.group(1))
                name = "?"
                for back in range(i - 1, max(i - 3, -1), -1):
                    nm = re.search(r"-\s*([A-Za-z0-9_]+):\s*$", lines[back])
                    if nm:
                        name = nm.group(1)
                        break

                size_val = height_val = None
                j = i + 1
                while j < n:
                    l2 = lines[j]
                    if l2.strip() == "":
                        j += 1
                        continue
                    indent2 = len(l2) - len(l2.lstrip(" "))
                    if indent2 <= control_indent:
                        break
                    sm = re.search(r"^\s*Size:\s*=(\d+(?:\.\d+)?)\s*$", l2)
                    if sm:
                        size_val = float(sm.group(1))
                    hm = re.search(r"^\s*Height:\s*=(\d+(?:\.\d+)?)\s*$", l2)
                    if hm:
                        height_val = float(hm.group(1))
                    j += 1

                if size_val is not None and height_val is not None:
                    need = min_height(size_val)
                    if height_val < need:
                        violations.append((os.path.basename(path), name, size_val, height_val, need))
            i += 1
    return violations


if __name__ == "__main__":
    violations = find_violations(SRC)
    if violations:
        print(f"{'File':<28}{'Control':<24}{'Size':>6}{'Height':>8}{'MinNeeded':>10}")
        for v in violations:
            print(f"{v[0]:<28}{v[1]:<24}{v[2]:>6}{v[3]:>8}{v[4]:>10.1f}")
        print(f"\n{len(violations)} violation(s) found.")
        raise SystemExit(1)
    print("No violations found. All ModernText controls satisfy Height >= Size*1.5+10.")
