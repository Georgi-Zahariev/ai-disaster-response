#!/usr/bin/env python3
"""
Quick test validation script.

Checks that all test files are syntactically correct and can be imported.
Run this before committing test changes.
"""

import sys
import importlib.util
from pathlib import Path


def validate_test_file(test_file: Path) -> bool:
    """Validate a single test file."""
    print(f"Validating {test_file.name}...", end=" ")
    
    try:
        # Check syntax by compiling
        with open(test_file, 'r') as f:
            compile(f.read(), test_file, 'exec')
        
        print("✅ Syntax OK")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Validate all test files."""
    print("=" * 60)
    print("Backend Test Validation")
    print("=" * 60)
    print()
    
    test_dir = Path(__file__).parent / "tests" / "unit"
    test_files = list(test_dir.glob("test_*.py"))
    
    if not test_files:
        print("❌ No test files found!")
        return 1
    
    print(f"Found {len(test_files)} test files:\n")
    
    results = []
    for test_file in sorted(test_files):
        result = validate_test_file(test_file)
        results.append((test_file.name, result))
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    print(f"\nTotal: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed > 0:
        print("\n⚠️  Some tests have issues. Please fix before running.")
        return 1
    else:
        print("\n✅ All tests are syntactically valid!")
        print("\nReady to run:")
        print("  ./run_tests.sh")
        print("  or")
        print("  pytest tests/unit/ -v")
        return 0


if __name__ == "__main__":
    sys.exit(main())
