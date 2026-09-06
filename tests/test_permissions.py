from angvey_lam.permissions import Permission


def test_domain_allow_block():
    p = Permission(allowed_domains=["arxiv.org"], blocked_domains=["evil.com"])
    assert p.domain_allowed("https://arxiv.org/abs/123")
    assert not p.domain_allowed("https://evil.com/x")
    assert not p.domain_allowed("https://sub.evil.com/x")


def test_tool_read_only():
    p = Permission(allowed_tools=["web_gather", "send_mail"], read_only=True)
    assert p.tool_allowed("web_gather", is_write=False)
    assert not p.tool_allowed("send_mail", is_write=True)
