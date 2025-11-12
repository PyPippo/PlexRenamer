#!/usr/bin/env python3
"""Test to verify button styles are applied correctly."""

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


def test_button_styles():
    """Test that button styles have the correct values."""
    print("Testing button styles...")

    # Test LoadButtonStyle
    print(f"LoadButton font_size: {LOAD_BUTTON_STYLE.font_size}")
    print(f"LoadButton font_weight: {LOAD_BUTTON_STYLE.font_weight}")

    # Test ServiceButtonStyle
    print(f"ServiceButton font_size: {SERVICE_BUTTON_STYLE.font_size}")
    print(f"ServiceButton font_weight: {SERVICE_BUTTON_STYLE.font_weight}")

    # Test ExitButtonStyle
    print(f"ExitButton font_size: {EXIT_BUTTON_STYLE.font_size}")
    print(f"ExitButton font_weight: {EXIT_BUTTON_STYLE.font_weight}")

    # Verify the changes
    if (
        LOAD_BUTTON_STYLE.font_size == '12pt'
        and LOAD_BUTTON_STYLE.font_weight == 'bold'
    ):
        print("✅ LoadButtonStyle correctly updated")
    else:
        print("❌ LoadButtonStyle not updated correctly")

    if (
        SERVICE_BUTTON_STYLE.font_size == '9pt'
        and SERVICE_BUTTON_STYLE.font_weight == 'normal'
    ):
        print("✅ ServiceButtonStyle correctly inherited defaults")
    else:
        print("❌ ServiceButtonStyle inheritance issue")

    if (
        EXIT_BUTTON_STYLE.font_size == '9pt'
        and EXIT_BUTTON_STYLE.font_weight == 'normal'
    ):
        print("✅ ExitButtonStyle correctly inherited defaults")
    else:
        print("❌ ExitButtonStyle inheritance issue")


if __name__ == '__main__':
    test_button_styles()
