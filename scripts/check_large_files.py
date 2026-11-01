#!/usr/bin/env python3
"""Pre-commit hook: warn if any tracked file exceeds size thresholds.

GitHub limits:
  - Warning at 50 MB
  - Hard limit at 100 MB
  - LFS recommended above 50 MB

Run manually: python3 scripts/check_large_files.py
Add to .git/hooks/pre-commit for automatic checking.
"""
import os
import subprocess
import sys

THRESHOLD_WARN_MB = 50
THRESHOLD_ERROR_MB = 100

def get_tracked_files():
    result = subprocess.run(
        ['git', 'ls-files'],
        capture_output=True, text=True, cwd=ROOT
    )
    return result.stdout.strip().split('\n') if result.stdout.strip() else []

def check_file_sizes():
    oversized = []
    for rel_path in get_tracked_files():
        abs_path = os.path.join(ROOT, rel_path)
        if not os.path.exists(abs_path):
            continue
        size_mb = os.path.getsize(abs_path) / (1024 * 1024)
        if size_mb >= THRESHOLD_ERROR_MB:
            oversized.append((rel_path, size_mb, 'ERROR'))
        elif size_mb >= THRESHOLD_WARN_MB:
            oversized.append((rel_path, size_mb, 'WARN'))
    return oversized

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    issues = check_file_sizes()
    if issues:
        print("Large file check:")
        for path, size_mb, level in issues:
            print(f"  {level}: {path} = {size_mb:.1f} MB")
        if any(level == 'ERROR' for _, _, level in issues):
            print(f"\nERROR: Files >= {THRESHOLD_ERROR_MB} MB will be REJECTED by GitHub.")
            sys.exit(1)
        else:
            print(f"\nWARNING: Files >= {THRESHOLD_WARN_MB} MB trigger GitHub warnings.")
            print("Consider: git lfs track '<pattern>'")
            sys.exit(0)
    else:
        print("Large file check: OK (no files >= 50 MB)")
        sys.exit(0)
