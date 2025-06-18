import difflib
import os
import zipfile
from xml.etree import ElementTree as ET
from copy import deepcopy

WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


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


def _load_docx_elements(docx_path: str):
    """Return (elements, texts, tree) for a docx file."""
    with zipfile.ZipFile(docx_path) as zf:
        xml_bytes = zf.read("word/document.xml")
    tree = ET.fromstring(xml_bytes)
    body = tree.find(f"{WORD_NS}body")
    elems = list(body)
    texts = [ET.tostring(e, encoding="unicode") for e in elems]
    return elems, texts, tree


def merge_docx(base_path: str, local_path: str, remote_path: str, output_path: str) -> None:
    """Merge docx files at paragraph level and write result to ``output_path``."""
    base_elems, base_texts, _ = _load_docx_elements(base_path)
    local_elems, _, local_tree = _load_docx_elements(local_path)
    remote_elems, remote_texts, _ = _load_docx_elements(remote_path)

    sm = difflib.SequenceMatcher(None, base_texts, remote_texts)
    merged: list = []
    local_idx = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            merged.extend(local_elems[local_idx: local_idx + (i2 - i1)])
            local_idx += i2 - i1
        elif tag == "replace":
            merged.extend(remote_elems[j1:j2])
            local_idx += i2 - i1
        elif tag == "delete":
            local_idx += i2 - i1
        elif tag == "insert":
            merged.extend(remote_elems[j1:j2])
    merged.extend(local_elems[local_idx:])

    body = local_tree.find(f"{WORD_NS}body")
    for child in list(body):
        body.remove(child)
    for el in merged:
        body.append(deepcopy(el))

    xml_bytes = ET.tostring(local_tree, encoding="utf-8", xml_declaration=True)

    with zipfile.ZipFile(local_path) as src:
        with zipfile.ZipFile(output_path, "w") as dst:
            for item in src.infolist():
                data = src.read(item.filename)
                if item.filename == "word/document.xml":
                    data = xml_bytes
                dst.writestr(item, data)


def merge_documents(base_path: str, local_path: str, remote_path: str, output_path: str) -> None:
    """Merge ``remote_path`` over ``local_path`` using ``base_path``."""
    ext = os.path.splitext(local_path)[1].lower()
    if ext == ".docx":
        merge_docx(base_path, local_path, remote_path, output_path)
    else:
        with open(base_path, "r", encoding="utf-8", errors="ignore") as fp:
            base_text = fp.read()
        with open(local_path, "r", encoding="utf-8", errors="ignore") as fp:
            local_text = fp.read()
        with open(remote_path, "r", encoding="utf-8", errors="ignore") as fp:
            remote_text = fp.read()
        merged = three_way_merge(base_text, local_text, remote_text)
        with open(output_path, "w", encoding="utf-8") as fp:
            fp.write(merged)
