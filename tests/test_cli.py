from docpipe.cli import main


def test_generate_then_verify(tmp_path):
    out = str(tmp_path / "out")
    assert main(["generate", "--out", out]) == 0
    assert main(["verify", "--out", out]) == 0


def test_verify_fails_on_tamper(tmp_path):
    out = tmp_path / "out"
    main(["generate", "--out", str(out)])
    (out / "C1002.html").write_text("tampered", encoding="utf-8")
    assert main(["verify", "--out", str(out)]) == 1
