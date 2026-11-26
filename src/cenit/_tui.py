"""Textual table explorer for CENIT values."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import DataTable, Footer, Header, Static

from .view import View


class CenitExplorer(App[None]):
    CSS = """
    Screen {
        background: #111827;
    }

    Header, Footer {
        background: #273449;
    }

    .heading {
        color: #d8b4fe;
        text-style: bold;
        padding: 1 2;
    }

    .section-title {
        color: #93c5fd;
        text-style: bold;
        padding: 1 2 0 2;
    }

    .grid {
        height: auto;
        max-height: 18;
        border: round #4b5563;
        background: #1b2130;
        margin: 0 2 1 2;
    }

    .grid:focus {
        border: round #93c5fd;
    }

    .footnotes {
        color: #fda4af;
        padding: 1 2 2 2;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, config: View, value: object) -> None:
        super().__init__()
        self._config = config
        self._sections = tuple(
            section for section in config.sections(value) if section.columns
        )
        self._footnotes = config.footnote_items(value) if config.show_footnotes else ()
        self.title = config.title or "CENIT data"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with VerticalScroll():
            yield Static(self.title, classes="heading")
            for section in self._sections:
                yield Static(section.title, classes="section-title")
                table = DataTable(
                    show_header=self._config.show_columns,
                    show_row_labels=False,
                    zebra_stripes=True,
                    cell_padding=1,
                    classes="grid",
                )
                table.add_columns(*(label for _, label in section.columns))
                table.add_rows(section.rows)
                table.border_title = section.title
                table.border_subtitle = f"{len(section.rows)} row(s)"
                yield table
            if self._footnotes:
                lines = [self._config._label("footnotes")]
                lines.extend(f"{marker} {definition}" for marker, definition in self._footnotes)
                yield Static("\n".join(lines), classes="footnotes")
            if not self._sections and not self._footnotes:
                yield Static("No data to display", classes="heading")
        yield Footer()


def run_explorer(config: View, value: object) -> None:
    """Run the Textual explorer for ``value``."""
    CenitExplorer(config, value).run()
