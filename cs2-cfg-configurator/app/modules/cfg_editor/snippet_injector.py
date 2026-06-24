# cfg_editor/snippet_injector.py
# Backend: fuegt rohe CFG-Bloecke (alias, bind, Kommentare) in .cfg-Dateien ein
from pathlib import Path


def inject_snippet(
    snippet: str,
    output_path: Path,
    mode: str = "append",
    header_comment: str = "",
) -> None:
    """
    Fuegt einen rohen CFG-Schnipsel in eine .cfg-Datei ein.

    Args:
        snippet:        Der rohe CFG-Text (alias, bind, Kommentare, etc.)
        output_path:    Pfad zur Ziel-.cfg-Datei
        mode:           "append"    = an bestehende Datei anhaengen
                        "prepend"   = vor bestehenden Inhalt stellen
                        "overwrite" = Datei komplett ersetzen
        header_comment: Optionaler Kommentar-Header fuer den Schnipsel
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    block_parts = []
    if header_comment:
        for line in header_comment.strip().splitlines():
            block_parts.append(f"// {line}" if not line.startswith("//") else line)
    block_parts.append(snippet.strip())
    block = "\n".join(block_parts) + "\n"

    if mode == "overwrite" or not output_path.exists():
        output_path.write_text(block, encoding="utf-8")
        return

    existing = output_path.read_text(encoding="utf-8")

    if mode == "prepend":
        output_path.write_text(block + "\n" + existing, encoding="utf-8")
    else:  # append
        separator = "\n" if existing.endswith("\n") else "\n\n"
        output_path.write_text(existing + separator + block, encoding="utf-8")
