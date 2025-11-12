#!/usr/bin/env python3
"""Simple test to verify button styles are correctly defined."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.models.gui_models import (
    LOAD_BUTTON_STYLE,
    SERVICE_BUTTON_STYLE,
    EXIT_BUTTON_STYLE,
)


def simple_test():
    """Test that button styles are correctly defined."""
    print("=== Button Style Test ===")
    print(f"LoadButton font_size: {LOAD_BUTTON_STYLE.font_size}")
    print(f"LoadButton font_weight: {LOAD_BUTTON_STYLE.font_weight}")
    print(f"ServiceButton font_size: {SERVICE_BUTTON_STYLE.font_size}")
    print(f"ServiceButton font_weight: {SERVICE_BUTTON_STYLE.font_weight}")
    print(f"ExitButton font_size: {EXIT_BUTTON_STYLE.font_size}")
    print(f"ExitButton font_weight: {EXIT_BUTTON_STYLE.font_weight}")

    # Verify the changes
    if (
        LOAD_BUTTON_STYLE.font_size == '15pt'
        and LOAD_BUTTON_STYLE.font_weight == 'bold'
    ):
        print("\n✅ SUCCESS: LoadButtonStyle correctly updated to 15pt bold")
        return True
    else:
        print("\n❌ FAILURE: LoadButtonStyle not updated correctly")
        return False


if __name__ == '__main__':
    success = simple_test()
    sys.exit(0 if success else 1)
