"""GUI-specific data models for the Renamer application."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# =============================================================================
# UI LAYOUT CONSTANTS
# =============================================================================

# Window dimensions - Default size
DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 800

# Window dimensions - Minimum size (not resizable below these values)
MIN_WINDOW_WIDTH = 900
MIN_WINDOW_HEIGHT = 500

# Layout spacing
LAYOUT_MARGIN = 10
LAYOUT_SPACING = 10
BUTTON_SPACING = 10


# =============================================================================
# FILES TABLE
# =============================================================================

# Table columns
TABLE_COL_ORIGINAL = 0
TABLE_COL_NEW = 1
TABLE_COL_STATUS = 2


# =============================================================================
# STATUS BAR
# =============================================================================

# Status bar
STATUS_BAR_MIN_HEIGHT = 25


class MessageType(Enum):
    """Types of messages for the status area."""

    INFO = 'info'  # ℹ️ Informational message
    WARNING = 'warning'  # ⚠️ Warning message
    ERROR = 'error'  # ❌ Error message
    SUCCESS = 'success'  # ✅ Success message
    PROCESSING = 'processing'  # 🔄 Processing/loading message


# =============================================================================
# MEDIA INFO PANEL
# =============================================================================

# Media Info Panel - Dimensions
MEDIA_INFO_PANEL_HEIGHT_RATIO = 0.20  # 20% of main window height
MEDIA_INFO_PANEL_MIN_HEIGHT = 150     # Minimum panel height (ensures readability)
MEDIA_INFO_PANEL_MAX_HEIGHT = 600     # Maximum panel height (prevents excessive space usage)

# Media Info Panel - Layout spacing
MEDIA_INFO_PANEL_MARGIN = 10          # Outer margin for the panel
MEDIA_INFO_PANEL_SPACING = 10         # General spacing in the panel
MEDIA_INFO_SECTIONS_LEFT_PADDING = 100  # Left padding for sections row

# Media Info Panel - Content Layout spacing
MEDIA_INFO_SECTION_TITLE_SPACING = 3  # Spacing between section title and content
MEDIA_INFO_CONTENT_SPACING = 8        # Spacing for content layout
MEDIA_INFO_SECTIONS_SPACING = 8       # Spacing between sections (General, Video, Audio, Subtitles)

# Media Info Panel - Grids Layout spacing
MEDIA_INFO_GRID_LEFT_MARGIN = 5       # Left margin for content grids
MEDIA_INFO_GRID_HORIZONTAL_SPACING = 8  # Horizontal spacing in grids (label-value)
MEDIA_INFO_GRID_VERTICAL_SPACING = 2  # Vertical spacing in grids (between rows)

# Media Info Panel - Animation
MEDIA_INFO_ANIMATION_DURATION = 250   # Animation duration in milliseconds


# =============================================================================
# BUTTON STYLES - Independent of the themes
# =============================================================================


@dataclass
class ButtonStyle:
    """Configurazione stile per un gruppo di bottoni.

    Questi attributi sono indipendenti dal tema e definiscono
    l'aspetto strutturale dei bottoni.
    """

    # Font
    font_family: str = 'Segoe UI'
    font_size: str = '9pt'
    font_weight: str = 'normal'

    # Dimensioni
    padding: str = '6px 12px'
    min_height: str = '15px'
    min_width: str = '50px'

    # Borders and shapes
    border_radius: str = '4px'
    border_width: str = '1px'
    border_style: str = 'solid'

    # Icon configuration
    icon_size: int = 16  # Icon size in pixels


# Default styles for the three groups of buttons
LOAD_BUTTON_STYLE = ButtonStyle(
    font_family='Segoe UI',
    font_size='10pt',
    font_weight='normal',
    padding='6px 6px',
    min_height='20px',
    min_width='100px',
    border_radius='4px',
    border_width='1px',
    border_style='solid',
    icon_size=20,
)

SERVICE_BUTTON_STYLE = ButtonStyle(
    font_family='Segoe UI',
    font_size='9pt',
    font_weight='normal',
    padding='8px 10px',
    min_height='12px',
    min_width='100px',
    border_radius='4px',
    border_width='1px',
    border_style='solid',
    icon_size=16,
)

REMOVE_BUTTON_STYLE = ButtonStyle(
    font_family='Segoe UI',
    font_size='9pt',
    font_weight='bold',
    padding='8px 10px',
    min_height='12px',
    min_width='100px',
    border_radius='4px',
    border_width='1px',
    border_style='solid',
    icon_size=16,
)

EXIT_BUTTON_STYLE = ButtonStyle(
    font_family='Segoe UI',
    font_size='9pt',
    font_weight='normal',
    padding='6px 30px',
    min_height='15px',
    min_width='50px',
    border_radius='4px',
    border_width='1px',
    border_style='solid',
    icon_size=16,
)


# =============================================================================
# STATUS DESCRIPTORS - UI Presentation Layer
# =============================================================================

from typing import Callable
from .core_models import FileStatus


@dataclass(frozen=True)
class StatusDescriptor:
    """
    Descriptor per la visualizzazione UI di uno status file.

    NOTA ARCHITETTURALE: Questo è un modello UI, non business logic.
    Contiene solo informazioni di presentazione (icone, colori, messaggi).

    Attributes:
        icon: Emoji/icon da mostrare (es. "✅", "❌", "⚠️")
        message_type: Tipo di messaggio per styling (SUCCESS, WARNING, ERROR, INFO)
        label: Funzione che genera il label testuale dato il count
        priority: Priorità per ordinamento (1=most critical, 6=least critical)
        action_hint: Suggerimento azione per l'utente (es. "Click to edit")
    """

    icon: str
    message_type: MessageType
    label: Callable[[int], str]
    priority: int
    action_hint: str = ""


# UI Status Descriptors - Single Source of Truth per display info
UI_STATUS_DESCRIPTORS: dict[FileStatus, StatusDescriptor] = {
    # Critical (priority 1-3): Issues che richiedono azione immediata
    FileStatus.DUPLICATE: StatusDescriptor(
        icon="⚠️",
        message_type=MessageType.ERROR,
        label=lambda count: f"Duplicates: {count}",
        priority=1,
        action_hint="Please edit or remove duplicates",
    ),
    FileStatus.INVALID: StatusDescriptor(
        icon="❌",
        message_type=MessageType.ERROR,
        label=lambda count: f"Invalid: {count}",
        priority=2,
        action_hint="Click to edit or use Remove button",
    ),
    FileStatus.NOT_VIDEO: StatusDescriptor(
        icon="❌",
        message_type=MessageType.ERROR,
        label=lambda count: f"Not Video: {count}",
        priority=3,
        action_hint="Use Remove button",
    ),
    # Warning (priority 4): Richiede input ma non blocca
    FileStatus.NEEDS_YEAR: StatusDescriptor(
        icon="⚠️",
        message_type=MessageType.WARNING,
        label=lambda count: f"Needs Year: {count}",
        priority=4,
        action_hint="Double-click to edit",
    ),
    # Success (priority 5): Pronto per azione
    FileStatus.READY: StatusDescriptor(
        icon="✅",
        message_type=MessageType.SUCCESS,
        label=lambda count: f"Ready: {count}",
        priority=5,
        action_hint="Click Apply Changes to proceed",
    ),
    # Info (priority 6): Informativo, no action needed
    FileStatus.ALREADY_NORMALIZED: StatusDescriptor(
        icon="⏭️",
        message_type=MessageType.INFO,
        label=lambda count: f"Already Normalized: {count}",
        priority=6,
        action_hint="",
    ),
}


# Convenience dict per FileTable (solo icone)
STATUS_ICONS: dict[FileStatus, str] = {
    status: descriptor.icon for status, descriptor in UI_STATUS_DESCRIPTORS.items()
}


def build_status_message(stats: dict[FileStatus, int]) -> tuple[str, MessageType]:
    """
    Costruisce messaggio completo per status bar da statistiche file.

    Logica:
    1. Filtra solo status con count > 0
    2. Ordina per priority (most critical first)
    3. Costruisce message parts: "icon label | icon label | ..."
    4. Aggiunge action hint dello status più critico
    5. Determina MessageType dello status più critico

    Args:
        stats: Dizionario FileStatus -> count

    Returns:
        Tuple (message, message_type)

    Examples:
        >>> stats = {FileStatus.READY: 2, FileStatus.INVALID: 1}
        >>> msg, type = build_status_message(stats)
        >>> msg
        '❌ Invalid: 1 | ✅ Ready: 2 • Click to edit or use Remove button'
        >>> type
        MessageType.ERROR
    """
    # Filtra status attivi e recupera descriptors
    active_statuses = [
        (status, count, UI_STATUS_DESCRIPTORS[status])
        for status, count in stats.items()
        if count > 0 and status in UI_STATUS_DESCRIPTORS
    ]

    # Caso: nessun file
    if not active_statuses:
        return "Ready to process files", MessageType.INFO

    # Ordina per priority (1 = most critical)
    active_statuses.sort(key=lambda x: x[2].priority)

    # Costruisci message parts
    message_parts = [
        f"{descriptor.icon} {descriptor.label(count)}"
        for status, count, descriptor in active_statuses
    ]

    # Status più critico determina MessageType e action hint
    most_critical_descriptor = active_statuses[0][2]

    # Costruisci messaggio finale
    message = " | ".join(message_parts)

    # Aggiungi action hint se presente
    if most_critical_descriptor.action_hint:
        message += f" • {most_critical_descriptor.action_hint}"

    return message, most_critical_descriptor.message_type
