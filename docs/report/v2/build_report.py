"""Build Quiet-Suppression-report.docx from report_source.txt on top of the template-styled draft (24 Oct 2026).

Keeps the draft's title block (Apart template layout) and styles, swaps title, authors and abstract,
and regenerates the body from a small line markup:
  ## / ###  headings      %list N  then "+ " items   "- " bullets     %cols w1,w2,..  then "| a | b" rows
  %cap caption   %fig1 / %fig2   %pagebreak   %meta italic note   **bold**  *italic*
usage: python build_report.py
"""
from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).parent
BASE = HERE / "Quiet-Suppression-draft.docx"
OUT = HERE.parent / "for-google-drive" / "writeups" / "Quiet-Suppression-report.docx"
FIG2 = HERE / "fig2_monitor_arms.png"
FONT = '<w:rFonts w:ascii="Old Standard TT" w:cs="Old Standard TT" w:eastAsia="Old Standard TT" w:hAnsi="Old Standard TT"/>'


def runs(text, size=None, bold=False, italic=False):
    out = []
    for part in re.split(r"(\*\*.+?\*\*|\*[^*\s][^*]*?\*)", text):
        if not part:
            continue
        b, i = bold, italic
        if part.startswith("**") and part.endswith("**"):
            part, b = part[2:-2], True
        elif part.startswith("*") and part.endswith("*"):
            part, i = part[1:-1], True
        rpr = FONT + ('<w:b w:val="1"/><w:bCs w:val="1"/>' if b else "") + ('<w:i w:val="1"/><w:iCs w:val="1"/>' if i else "")
        if size:
            rpr += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
        out.append(f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(part)}</w:t></w:r>')
    return "".join(out)


def para(text, size=None, italic=False, jc="both", after=160, extra=""):
    return (f'<w:p><w:pPr>{extra}<w:spacing w:after="{after}" w:line="264" w:lineRule="auto"/><w:jc w:val="{jc}"/>'
            f'<w:rPr>{FONT}</w:rPr></w:pPr>{runs(text, size, italic=italic)}</w:p>')


def heading(text, level):
    sty, sz, sp = ("Heading2", 28, 'w:after="60" w:before="200" w:line="300"') if level == 2 else \
                  ("Heading3", 24, 'w:after="40" w:before="140" w:line="264"')
    return (f'<w:p><w:pPr><w:pStyle w:val="{sty}"/><w:keepNext/><w:spacing {sp} w:lineRule="auto"/>'
            f'<w:rPr>{FONT}<w:b w:val="1"/><w:sz w:val="{sz}"/></w:rPr></w:pPr>'
            f'{runs(text, sz, bold=True)}</w:p>')


def item(text, num, size=None):
    return (f'<w:p><w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num}"/></w:numPr>'
            f'<w:spacing w:after="60" w:line="264" w:lineRule="auto"/><w:ind w:left="720" w:hanging="360"/>'
            f'<w:jc w:val="both"/><w:rPr>{FONT}</w:rPr></w:pPr>{runs(text, size)}</w:p>')


def cell(text, w, head, left, keep=True):
    shd = '<w:shd w:val="clear" w:color="auto" w:fill="EDEDED"/>' if head else ""
    return (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{shd}<w:vAlign w:val="center"/></w:tcPr>'
            f'<w:p><w:pPr>{"<w:keepNext/>" if keep else ""}<w:spacing w:after="20" w:before="20" w:line="240" w:lineRule="auto"/>'
            f'<w:jc w:val="{"left" if left else "center"}"/></w:pPr>{runs(text, 17, bold=head)}</w:p></w:tc>')


def table(rows, widths):
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    x = (f'<w:tbl><w:tblPr><w:tblW w:w="{sum(widths)}" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>'
         '<w:top w:val="single" w:sz="4" w:color="808080"/><w:bottom w:val="single" w:sz="4" w:color="808080"/>'
         '<w:insideH w:val="single" w:sz="2" w:color="BFBFBF"/></w:tblBorders><w:tblLayout w:type="fixed"/>'
         '<w:tblCellMar><w:left w:w="70" w:type="dxa"/><w:right w:w="70" w:type="dxa"/></w:tblCellMar></w:tblPr>'
         f'<w:tblGrid>{grid}</w:tblGrid>')
    for r, row in enumerate(rows):
        head = r == 0
        trpr = "<w:tblHeader/><w:cantSplit/>" if head else "<w:cantSplit/>"
        x += f"<w:tr><w:trPr>{trpr}</w:trPr>" + "".join(
            cell(c, w, head, k == 0, r < len(rows) - 1 or True) for k, (c, w) in enumerate(zip(row, widths))) + "</w:tr>"
    return x + "</w:tbl>"


def figure(n, rid, cx, cy):
    return (f'<w:p><w:pPr><w:keepNext/><w:spacing w:after="40"/><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
            f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
            f'<wp:docPr id="{500 + n}" name="Figure {n}"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:nvPicPr><pic:cNvPr id="{500 + n}" name="fig{n}.png"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic>'
            '</wp:inline></w:drawing></w:r></w:p>')


def body(lines):
    out, meta, lst, widths, rows, in_refs = [], {}, 5, None, [], False

    def flush():
        nonlocal rows, widths
        if rows:
            out.append(table(rows, widths))
            rows, widths = [], None

    for ln in lines:
        if not ln.strip():
            continue
        if not ln.startswith("| "):
            flush()
        if ln.startswith(("%title ", "%abstract ")):
            k, v = ln[1:].split(" ", 1)
            meta[k] = v
        elif ln.startswith("%meta "):
            out.append(para(ln[6:], italic=True))
        elif ln.startswith("%list "):
            lst = int(ln[6:])
        elif ln.startswith("%cols "):
            widths = [int(w) for w in ln[6:].split(",")]
        elif ln.startswith("| "):
            rows.append([c.strip() for c in ln[2:].split(" | ")])
        elif ln.startswith("%cap "):
            out.append(para(ln[5:], size=18, after=200))
        elif ln == "%fig1":
            out.append(figure(1, "rIdFig1", 5669280, 2523744))
        elif ln == "%fig2":
            out.append(figure(2, "rIdFig2", 5943600, round(5943600 * 779 / 1977)))
        elif ln == "%pagebreak":
            out.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        elif ln.startswith("## "):
            in_refs = ln[3:] == "References"
            out.append(heading(ln[3:], 2))
        elif ln.startswith("### "):
            out.append(heading(ln[4:], 3))
        elif ln.startswith("+ "):
            out.append(item(ln[2:], lst, 20 if in_refs else None))
        elif ln.startswith("- "):
            out.append(item(ln[2:], 3))
        else:
            out.append(para(ln))
    flush()
    return "".join(out), meta


def main():
    src = (HERE / "report_source.txt").read_text(encoding="utf-8").splitlines()
    xml_body, meta = body(src)
    zin = zipfile.ZipFile(BASE)
    files = {n: zin.read(n) for n in zin.namelist()}
    doc = files["word/document.xml"].decode("utf-8")

    # title block: everything up to the end of the first top-level table
    start = doc.index("<w:body>") + len("<w:body>")
    depth, i = 0, start
    for m in re.finditer(r"<w:tbl>|</w:tbl>", doc[start:]):
        depth += 1 if m.group() == "<w:tbl>" else -1
        if depth == 0:
            i = start + m.end()
            break
    head = doc[:i]
    head = head.replace("Quiet Suppression: Auditing Collusion in Multi-Agent Grievance Pipelines", escape(meta["title"]))
    ab = re.search(r"Project grievance mechanisms let.*?</w:t>", head, re.S)
    head = head[:ab.start()] + escape(meta["abstract"]) + "</w:t>" + head[ab.end():]
    head = head.replace("[Team member]", "Deepayan Sinha", 1)
    head = head.replace("[Team member]", "Prashanth Vijay", 1)
    for aff in ("Sociable Systems", "Altiora Systems", "Altiora Systems"):
        head = head.replace("[Affiliation]", aff, 1)
    head = head.replace("[Team member]", "").replace("[Affiliation]", "")
    sect = doc[doc.rindex("<w:sectPr"):]
    files["word/document.xml"] = (head + xml_body + sect).encode("utf-8")

    rels = files["word/_rels/document.xml.rels"].decode("utf-8")
    if "rIdFig2" not in rels:
        rels = rels.replace("</Relationships>", '<Relationship Id="rIdFig2" Type="http://schemas.openxmlformats.org/'
                            'officeDocument/2006/relationships/image" Target="media/fig2.png"/></Relationships>')
    files["word/_rels/document.xml.rels"] = rels.encode("utf-8")
    files["word/media/fig2.png"] = FIG2.read_bytes()

    num = files["word/numbering.xml"].decode("utf-8")
    if 'w:numId="6"' not in num:
        num = num.replace("</w:numbering>", '<w:num w:numId="6"><w:abstractNumId w:val="5"/><w:lvlOverride w:ilvl="0">'
                          '<w:startOverride w:val="1"/></w:lvlOverride></w:num></w:numbering>')
    files["word/numbering.xml"] = num.encode("utf-8")

    ct = files["[Content_Types].xml"].decode("utf-8")
    if 'Extension="png"' not in ct:
        ct = ct.replace("<Types ", '<Types ', 1).replace(">", '><Default Extension="png" ContentType="image/png"/>', 1)
    files["[Content_Types].xml"] = ct.encode("utf-8")

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in files.items():
            z.writestr(n, b)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
