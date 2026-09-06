from angvey_gather.extract import extract_relevant, html_to_clean_markdown


def test_html_clean():
    html = "<html><body><nav>Menu</nav><main><p>Hello agent world</p></main><script>x</script></body></html>"
    md = html_to_clean_markdown(html)
    assert "Hello agent world" in md
    assert "script" not in md.lower() or "x" not in md


def test_extract_relevant():
    text = "Cats are soft.\n\nAgent self-reflection helps recovery.\n\nDogs bark."
    out = extract_relevant(text, "agent reflection recovery", max_chars=200)
    assert "self-reflection" in out.lower()
