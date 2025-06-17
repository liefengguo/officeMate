import difflib


def three_way_merge(base_text: str, local_text: str, remote_text: str) -> str:
    """Return merged text using base, local and remote versions.

    This implementation performs a naive line based merge where changes from
    ``remote_text`` relative to ``base_text`` are applied on top of
    ``local_text``. When both local and remote modify the same region the
    remote change wins. The function returns the merged result as a single
    string.
    """
    base_lines = base_text.splitlines()
    local_lines = local_text.splitlines()
    remote_lines = remote_text.splitlines()

    sm = difflib.SequenceMatcher(None, base_lines, remote_lines)
    result_lines = []
    local_idx = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            result_lines.extend(local_lines[local_idx: local_idx + (i2 - i1)])
            local_idx += i2 - i1
        elif tag == "replace":
            result_lines.extend(remote_lines[j1:j2])
            local_idx += i2 - i1
        elif tag == "delete":
            local_idx += i2 - i1
        elif tag == "insert":
            result_lines.extend(remote_lines[j1:j2])
    result_lines.extend(local_lines[local_idx:])
    return "\n".join(result_lines)
