from pathlib import Path

import pytest

from ckanext.unckan import log_reader


def test_read_tail_is_bounded_by_line_count(tmp_path):
    log = tmp_path / "ckan.log"
    log.write_text("uno\ndos\ntres\n", encoding="utf-8")
    assert log_reader.read_tail(log, 2) == "dos\ntres"


def test_select_source_rejects_non_allowlisted_path(monkeypatch, tmp_path):
    allowed = tmp_path / "allowed.log"
    allowed.touch()
    monkeypatch.setattr(log_reader, "configured_sources", lambda: {str(allowed): allowed})
    with pytest.raises(ValueError):
        log_reader.select_source(str(Path("/etc/passwd")))
