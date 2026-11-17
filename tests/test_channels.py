from docpipe import channels, generator


def test_channels(tmp_path):
    files = generator.generate_all("data/customers.json", "templates/statement.html", tmp_path)
    batch = channels.deliver_print(files, tmp_path)
    assert batch.read_text().splitlines()[0] == "0001|C1001.html"
    receipts = channels.deliver_secure_inbox(files, tmp_path)
    assert len(receipts) == 3 and all(r.exists() for r in receipts)
