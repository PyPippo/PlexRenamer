"""Media type definitions and constants."""

from typing import Literal, TypeAlias, get_args

FileContentType: TypeAlias = Literal['series', 'film']
FILE_CONTENT_TYPES = list(get_args(FileContentType))

FILE_CONTENT_TYPE_SERIES = 'series'
FILE_CONTENT_TYPE_FILM = 'film'
