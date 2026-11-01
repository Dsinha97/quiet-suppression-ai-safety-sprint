"""Build the submission docx from report_source.txt (adapted from Codex's v1/build_v1.py, 25 Oct).

Title block comes from template_base.docx; its abstract is swapped for the source's.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from lxml import etree
from docx import Document

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ORIGINAL = HERE / 'template_base.docx'
OUT = HERE / 'Quiet-Suppression-report-v2.docx'
SOURCE = HERE / 'report_source.txt'

spec = importlib.util.spec_from_file_location('report_builder_original', HERE/'build_report.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
original_abstract = 'Large projects must run grievance mechanisms where workers and communities report harms. As AI agents take over intake, rating and escalation, a team of agents could keep serious complaints from the people able to act through selective summaries and escalation decisions. We built a grievance pipeline from separate LLM agents on synthetic complaints. A hidden operator instruction to keep escalations low cut escalation from 92% to 64% of complaints in MiniMax and from 89% to 44% in Gemma, and a private notes channel between agents cut it to 28% in both. Notes written under the instruction recruited agents that never received it; in seven replayed cases, deleting one verdict sentence restored escalation. A notes-reading watchdog caught 42–63% of suppression, and almost none after seeing three past cases a review board had “accepted.” Matched arms show that the board’s endorsement does the damage: of thirteen watchdogs tested on all six arms, the endorsement lowered detection in eight, with non-overlapping read-level intervals, while the same precedents shown plainly left it near baseline; three frontier models caught every endorsed case (two ran on that arm only). One sentence telling the watchdog that the written policy outranks past cases raised detection in seven of those eight when the violation showed on the rating (four back to 100%), and recovered only part of it when an agent had quietly downgraded the case. Oversight should check outcomes against policy and treat a watchdog’s calibration material as an attack surface.'
source = SOURCE.read_text(encoding='utf-8')

# Build against the existing report so its Apart title block and author details survive intact.
links = {}
def link_id(url):
    if url not in links: links[url]='rIdV1Link'+str(len(links)+1)
    return links[url]

citations = {
 'Arike':('2026','https://arxiv.org/abs/2601.21112'),
 'Fish':('2024','https://arxiv.org/abs/2404.00806'),
 'Hu':('2026','https://arxiv.org/abs/2601.01685'),
 'Kovacic':('2011','https://repository.law.umich.edu/mlr/vol110/iss3/1/'),
 'Lin':('2025','https://arxiv.org/abs/2410.00031'),
 'Nakamura':('2026','https://arxiv.org/abs/2602.15198'),
 'Nguyen':('2026','https://arxiv.org/abs/2604.03968'),
 'Radev':('2026','https://arxiv.org/abs/2605.29178'),
 'Ren':('2025','https://arxiv.org/abs/2503.03750'),
 'Scheurer':('2024','https://arxiv.org/abs/2311.07590'),
 'Shi':('2026','https://arxiv.org/abs/2607.05132'),
}

def autolink(text):
    if '](' in text:return text
    for name,(year,url) in citations.items():
        text=re.sub(r'\b'+name+r' et al\.(?:, '+year+r'| \('+year+r'\))',lambda m:f'[{m.group()}]({url})',text)
    text=re.sub(r'\bIFC, 2012', '[IFC, 2012](https://www.ifc.org/en/insights-reports/2012/ifc-performance-standards)',text)
    text=re.sub(r'arXiv:(\d{4}\.\d{4,5})',lambda m:f'[{m.group()}](https://arxiv.org/abs/{m.group(1)})',text)
    if text.startswith('IFC (2012).'):
        text='[IFC (2012)](https://www.ifc.org/en/insights-reports/2012/ifc-performance-standards)'+text[len('IFC (2012)'):]
    if text.startswith('Kovacic, W. E.'):
        text=text.replace('Michigan Law Review','[Michigan Law Review](https://repository.law.umich.edu/mlr/vol110/iss3/1/)')
    return text

def v1_runs(text,size=None,bold=False,italic=False,_nested=False):
    if not _nested:text=autolink(text)
    chunks=[]
    pat=r'(\[[^\]]+\]\(https?://[^)]+\)|\*\*.+?\*\*|\*[^*\s][^*]*?\*)'
    for part in re.split(pat,text):
        if not part:continue
        if part.startswith('[') and '](' in part:
            m=re.fullmatch(r'\[([^\]]+)\]\((https?://[^)]+)\)',part)
            if m:
                rid=link_id(m[2]); inner=v1_runs(m[1],size,bold,italic,True)
                chunks.append(f'<w:hyperlink r:id="{rid}" w:history="1">{inner}</w:hyperlink>');continue
        if part.startswith('**') and part.endswith('**'):
            chunks.append(v1_runs(part[2:-2],size,True,italic,True));continue
        if part.startswith('*') and part.endswith('*'):
            chunks.append(v1_runs(part[1:-1],size,bold,True,True));continue
        rpr=b.FONT+('<w:b w:val="1"/><w:bCs w:val="1"/>' if bold else '')+('<w:i w:val="1"/><w:iCs w:val="1"/>' if italic else '')
        if size:rpr+=f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
        chunks.append(f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(part)}</w:t></w:r>')
    return ''.join(chunks)

b.runs=v1_runs
original_table=b.table
def v1_table(rows,widths):
    max_width=9360
    if sum(widths)>max_width:
        factor=max_width/sum(widths);widths=[round(w*factor) for w in widths];widths[-1]+=max_width-sum(widths)
    return original_table(rows,widths)
b.table=v1_table
original_heading=b.heading
def template_heading(text,level):
    xml=original_heading(text,level)
    if level==3:
        xml=xml.replace('<w:sz w:val="24"/>','<w:sz w:val="26"/>').replace('<w:szCs w:val="24"/>','<w:szCs w:val="26"/>')
    return xml
b.heading=template_heading
original_item=b.item
def template_item(text,num,size=None):
    return original_item(text,num,22 if size==20 else size)
b.item=template_item
xml_body,meta=b.body(source.splitlines())
with zipfile.ZipFile(ORIGINAL) as z: files={n:z.read(n) for n in z.namelist()}
doc=files['word/document.xml'].decode('utf-8')
start=doc.index('<w:body>')+len('<w:body>')
depth=0;end=None
for m in re.finditer(r'<w:tbl>|</w:tbl>',doc[start:]):
    depth+=1 if m.group()=='<w:tbl>' else -1
    if depth==0:end=start+m.end();break
assert end
head=doc[:end]
old_abstract=original_abstract
assert head.count(escape(old_abstract))==1
head=head.replace(escape(old_abstract),escape(meta['abstract']))
sect=doc[doc.rindex('<w:sectPr'):]
files['word/document.xml']=(head+xml_body+sect).encode('utf-8')
# The retained title block used a compacted 10 pt abstract. Restore the
# template's 11 pt while preserving its geometry and all other title settings.
doc_tree=etree.fromstring(files['word/document.xml'])
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
abstract_nodes=doc_tree.xpath('//w:t[text()=$value]',namespaces=ns,value=meta['abstract'])
assert len(abstract_nodes)==1
abstract_run=abstract_nodes[0].getparent()
for tag in ('sz','szCs'):
    abstract_run.find('w:rPr/w:'+tag,ns).set('{'+ns['w']+'}val','22')
# Tighten the template's empty spacer after the abstract at the user's request.
abstract_p=abstract_run.getparent()
abstract_p.find('w:pPr/w:spacing',ns).set('{'+ns['w']+'}after','120')
title_table=doc_tree.find('w:body/w:tbl',ns)
trailing=title_table.xpath('.//w:p',namespaces=ns)[-1]
assert not trailing.xpath('.//w:t/text()',namespaces=ns)
spacing=trailing.find('w:pPr/w:spacing',ns)
for key,value in [('after','0'),('before','0'),('line','20'),('lineRule','exact')]:
    spacing.set('{'+ns['w']+'}'+key,value)
for size in trailing.xpath('./w:pPr/w:rPr/w:sz|./w:pPr/w:rPr/w:szCs',namespaces=ns):
    size.set('{'+ns['w']+'}val','2')
for margin in title_table.xpath('./w:tr[last()]/w:tc/w:tcPr/w:tcMar/w:bottom',namespaces=ns):
    margin.set('{'+ns['w']+'}w','0')
files['word/document.xml']=etree.tostring(doc_tree,encoding='utf-8',xml_declaration=True,standalone=True)
rels=files['word/_rels/document.xml.rels'].decode('utf-8')
new_rels=''.join(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="{escape(url)}" TargetMode="External"/>' for url,rid in links.items())
files['word/_rels/document.xml.rels']=rels.replace('</Relationships>',new_rels+'</Relationships>').encode('utf-8')
for name in ('word/document.xml','word/_rels/document.xml.rels'):
    etree.fromstring(files[name])
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    for name,data in files.items():z.writestr(name,data)

# Preserve all report numbers in the untouched quantitative tables, apart from clarified labels.
d=Document(OUT)
assert len(d.inline_shapes)==2
assert len(d.tables)==17
assert len(meta['abstract'].split())>=150 and len(meta['abstract'].split())<=250
assert all(s in ''.join(d.element.xpath('.//w:t/text()')) for s in ('Liezl Coetzee','Deepayan Sinha','Prashanth Vijay'))
assert all('`' not in p.text and '—' not in p.text for p in d.paragraphs)
(HERE/'source-integrity.json').write_text(json.dumps({'original_docx_sha256':hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),'original_abstract_sha256':hashlib.sha256(original_abstract.encode()).hexdigest(),'v2_docx_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'abstract_words':len(meta['abstract'].split()),'hyperlinks':len(links)},indent=2),encoding='utf-8')
print('WROTE',OUT)
print('ABSTRACT WORDS',len(meta['abstract'].split()),'LINKS',len(links))
print('MAIN WORDS',len(source.split('## References')[0].split()))
