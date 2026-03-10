"""Storage layer: JSON file persistence for the Task Manager."""

import json
import os
import tempfile


class Storage:
    """Reads and writes tasks as a JSON file.

    Uses a write-then-rename strategy so that the store is never left in a
    partially-written state.
    """

    def __init__(self, filepath: str) -> None:
        self._filepath = filepath

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self) -> list[dict]:
        """Return the list of task dicts from the JSON file.

        Returns an empty list if the file does not exist yet.

        Raises:
            RuntimeError: If the file exists but contains invalid JSON.
        """
        if not os.path.exists(self._filepath):
            return []
        try:
            with open(self._filepath, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Failed to parse task store '{self._filepath}': {exc}"
            ) from exc

    def save(self, tasks: list[dict]) -> None:
        """Persist *tasks* to the JSON file atomically.

        Writes to a temporary file in the same directory then renames it over
        the target file to avoid corruption on crashes.
        """
        directory = os.path.dirname(os.path.abspath(self._filepath))
        fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(tasks, fh, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self._filepath)
        except Exception:
            # Clean up the temporary file if something went wrong.
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
