#!/usr/bin/env python3
"""Check docstring coverage across all Python modules."""

import ast
import sys
from pathlib import Path
from typing import NamedTuple

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class DocstringChecker(ast.NodeVisitor):
    """AST visitor to check for docstrings."""

    def __init__(self):
        self.missing: list[tuple[str, int, str]] = []
        self.total_items = 0
        self.documented_items = 0

    def visit_Module(self, node):
        """Check module docstring."""
        self.total_items += 1
        if ast.get_docstring(node):
            self.documented_items += 1
        else:
            self.missing.append(("Module", 1, "Module docstring"))
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Check class docstring."""
        self.total_items += 1
        if ast.get_docstring(node):
            self.documented_items += 1
        else:
            self.missing.append(("Class", node.lineno, node.name))
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Check function/method docstring."""
        # Skip private methods starting with _ except __init__
        if node.name.startswith("_") and node.name != "__init__":
            self.generic_visit(node)
            return

        self.total_items += 1
        if ast.get_docstring(node):
            self.documented_items += 1
        else:
            self.missing.append(("Function", node.lineno, node.name))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Check async function docstring."""
        # Skip private methods starting with _ except __init__
        if node.name.startswith("_") and node.name != "__init__":
            self.generic_visit(node)
            return

        self.total_items += 1
        if ast.get_docstring(node):
            self.documented_items += 1
        else:
            self.missing.append(("Function", node.lineno, node.name))
        self.generic_visit(node)


def check_file(file_path: Path) -> tuple[int, int, list[tuple[str, int, str]]]:
    """Check docstrings in a Python file.

    Args:
        file_path: Path to Python file

    Returns:
        tuple: (total_items, documented_items, missing_list)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        checker = DocstringChecker()
        checker.visit(tree)

        return checker.total_items, checker.documented_items, checker.missing

    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
        return 0, 0, []


def main():
    """Run docstring coverage check."""
    print("=" * 70)
    print("DOCSTRING COVERAGE REPORT")
    print("=" * 70)

    src_path = project_root / "src"
    python_files = list(src_path.rglob("*.py"))

    total_items = 0
    documented_items = 0
    files_checked = 0

    issues_by_file = {}

    for file_path in sorted(python_files):
        # Skip __pycache__
        if "__pycache__" in str(file_path):
            continue

        items, documented, missing = check_file(file_path)

        if items == 0:
            continue

        files_checked += 1
        total_items += items
        documented_items += documented

        relative_path = file_path.relative_to(project_root)

        if missing:
            issues_by_file[str(relative_path)] = missing

        # Show file status
        coverage = (documented / items * 100) if items > 0 else 100
        status = "[OK]" if coverage == 100 else "[WARN]" if coverage >= 80 else "[FAIL]"

        print(f"\n{status} {relative_path}")
        print(f"   Coverage: {documented}/{items} ({coverage:.1f}%)")

        if missing:
            print("   Missing docstrings:")
            for item_type, lineno, name in missing:
                print(f"      Line {lineno}: {item_type} '{name}'")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Files checked: {files_checked}")
    print(f"Total items: {total_items}")
    print(f"Documented: {documented_items}")
    print(f"Missing: {total_items - documented_items}")

    if total_items > 0:
        coverage = documented_items / total_items * 100
        print(f"\nOverall coverage: {coverage:.1f}%")

        if coverage == 100:
            print("\n[SUCCESS] PERFECT! All items have docstrings!")
            return 0
        elif coverage >= 90:
            print("\n[OK] EXCELLENT! Coverage above 90%")
            return 0
        elif coverage >= 80:
            print("\n[WARN] GOOD: Coverage above 80%, but could be better")
            return 0
        else:
            print("\n[FAIL] NEEDS IMPROVEMENT: Coverage below 80%")
            return 1
    else:
        print("\n⚠️  No items found to check")
        return 0


if __name__ == "__main__":
    sys.exit(main())
