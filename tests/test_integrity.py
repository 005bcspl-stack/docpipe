from docpipe import generator, integrity


def make(tmp_path):
    files = generator.generate_all("data/customers.json", "templates/statement.html", tmp_path)
    integrity.build_manifest(files, tmp_path)
    return files


def test_clean_run_verifies(tmp_path):
    make(tmp_path)
    assert integrity.verify_manifest(tmp_path) == []


def test_tampering_detected(tmp_path):
    files = make(tmp_path)
    files[0].write_text("changed", encoding="utf-8")
    assert any("TAMPERED" in p for p in integrity.verify_manifest(tmp_path))


def test_missing_detected(tmp_path):
    files = make(tmp_path)
    files[1].unlink()
    assert any("MISSING" in p for p in integrity.verify_manifest(tmp_path))


def test_signature_detects_manifest_edit(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCPIPE_KEY", "secret")
    make(tmp_path)
    assert integrity.verify_manifest(tmp_path) == []
    monkeypatch.setenv("DOCPIPE_KEY", "wrong")
    assert "MANIFEST SIGNATURE INVALID" in integrity.verify_manifest(tmp_path)
