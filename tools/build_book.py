#!/usr/bin/env python3
"""
build_book.py - Import the HIV Informatics dissertation (.docx chapters) into a
MkDocs Material book.

One-time (or re-runnable) import step. After it runs, the Markdown in docs/ is
the source of truth: edit it directly, commit, and tag a release.

Pipeline, per chapter:
  1. pandoc .docx -> GitHub-flavored Markdown, extracting embedded media
  2. clean up headings (Word bold/italic markers, empty headings)
  3. apply copy-edits (typos found in the TOC review)
  4. auto-number "Figure :" / "Table :" captions whose Word SEQ fields were lost
  5. relabel repeated figure headings as legends
  6. nest embedded manuscripts (Ch5-8) under their paper title
  7. convert EMF/WMF/TIFF figures to web PNGs (LibreOffice -> PDF -> PNG)
  8. recover native Word charts that pandoc drops, from the dissertation PDF

Requirements (import step only; the website build does not need these):
  pandoc >= 3, LibreOffice (soffice), poppler-utils (pdftocairo, pdftotext),
  ImageMagick (convert), python-docx

Usage:
  python tools/build_book.py                       # defaults: sources/ -> docs/
  python tools/build_book.py --sources sources --docs docs --pdf sources/HIV_Informatics_v1.pdf
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import docx  # python-docx

# --------------------------------------------------------------------------
# Book structure
# --------------------------------------------------------------------------


@dataclass
class Chapter:
    number: int
    source: str          # file name in sources/
    slug: str            # output page name (without .md)
    part: int            # 1, 2, or 3
    has_paper: bool = False  # chapter embeds a manuscript (title + own abstract)
    chart_fallbacks: list = field(default_factory=list)


@dataclass
class ChartFallback:
    """A native Word chart pandoc cannot export; recovered from the PDF."""
    heading_contains: str
    pdf_page: int
    verify_text: str
    crop_points: tuple  # (x0, y0, x1, y1) in PDF points
    output_name: str


CHAPTERS = [
    Chapter(1, "ch01.docx", "01-what-we-believe-about-hiv", 1,
            chart_fallbacks=[ChartFallback(
                heading_contains="New HIV-1 Genomes by Sampling Year",
                pdf_page=50,
                verify_text="Figure made in Excel",
                crop_points=(86, 112, 528, 460),
                output_name="figure1-new-genomes-by-year.png")]),
    Chapter(2, "ch02.docx", "02-how-we-know-what-we-know", 1),
    Chapter(3, "ch03.docx", "03-hiv-informatics-framework", 1),
    Chapter(4, "ch04.docx", "04-problems-and-challenges", 1),
    Chapter(5, "ch05.docx", "05-dna-space", 2, has_paper=True),
    Chapter(6, "ch06.docx", "06-rna-space-mrna-models", 2, has_paper=True),
    Chapter(7, "ch07.docx", "07-rna-space-virion-mrna", 2, has_paper=True),
    Chapter(8, "ch08.docx", "08-rna-space-transductions", 2, has_paper=True),
    Chapter(9, "ch09.docx", "09-heterogeneous-samples", 3),
    Chapter(10, "ch10.docx", "10-conclusions", 3),
]

PARTS = {
    1: "Part One: HIV, HIV (re)sequencing, and a new framework to maximize HIV information from samples",
    2: "Part Two: Maximizing HIV sequencing information from control samples and model systems",
    3: "Part Three: Maximizing HIV sequence information from heterogeneous samples",
}

# Copy-edits: (chapter number, exact old heading text, new heading text)
HEADING_FIXES = [
    (2, "The pre-sequencing era of HIV informatics is market by qualitative datasets",
        "The pre-sequencing era of HIV informatics is marked by qualitative datasets"),
    (3, "HIV’s known unknown", "HIV’s known unknowns"),
    (3, "HIV’s unknown unknows", "HIV’s unknown unknowns"),
    (3, "Cautionary tails", "Cautionary tales"),
]

# Body-text copy-edits: (chapter number, old, new) - applied everywhere in the chapter
BODY_FIXES = [
    (2, "is market by qualitative", "is marked by qualitative"),
    (3, "unknown unknows", "unknown unknowns"),
    (10, "HIV liner reference genomes", "HIV linear reference genomes"),
]

# Supplemental figures and tables: False keeps them in each chapter's "Supplemental"
# section at the end (the convention in the published papers); True moves them into
# the text beside their first mention, like the main figures.
INLINE_SUPPLEMENTAL = False

WEB_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg"}
VECTOR_EXTENSIONS = {".emf", ".wmf"}
TIFF_EXTENSIONS = {".tif", ".tiff"}
RASTER_DPI = 200
MAX_IMAGE_PIXELS = 2400  # longest edge for web images

LOG: list[str] = []


def log(message: str) -> None:
    LOG.append(message)
    print(message)


def run(command: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(command)}\n{result.stderr}")
    return result.stdout


def check_tools() -> None:
    missing = [tool for tool in ("pandoc", "soffice", "pdftocairo", "pdftotext", "convert")
               if shutil.which(tool) is None]
    if missing:
        sys.exit(f"Missing required tools: {', '.join(missing)}")


# --------------------------------------------------------------------------
# Titles
# --------------------------------------------------------------------------


def chapter_title(docx_path: Path) -> str:
    """Read the Word 'Title' paragraph after 'Chapter N', keeping strikethrough as ~~x~~."""
    document = docx.Document(str(docx_path))
    titles = []
    for paragraph in document.paragraphs:
        if paragraph.style.name != "Title" or not paragraph.text.strip():
            continue
        pieces = []
        for run_ in paragraph.runs:
            text = run_.text
            if run_.font.strike and text.strip():
                pieces.append(f"~~{text.strip()}~~" + (" " if text.endswith(" ") else ""))
            else:
                pieces.append(text)
        titles.append(re.sub(r"\s+", " ", "".join(pieces)).strip())
    body_titles = [t for t in titles if not re.fullmatch(r"Chapter \d+", t)]
    if not body_titles:
        raise ValueError(f"No chapter title found in {docx_path.name}")
    return body_titles[0]


def plain_title(title: str) -> str:
    """Navigation title: drop struck-through words."""
    return re.sub(r"\s+", " ", re.sub(r"~~[^~]+~~", "", title)).strip()


# --------------------------------------------------------------------------
# Markdown clean-up
# --------------------------------------------------------------------------

HEADING_LINE = re.compile(r"^(#{1,6})\s*(.*?)\s*$")
CAPTION = re.compile(
    r"^(?P<prefix>Chapter \d+ )?(?P<supp>Supplemental )?(?P<kind>Figure|Table)"
    r"\s*(?P<num>\d+)?(?P<letter>[A-Z])?\s*(?P<legend>[Ll]egend)?\s*:\s*(?P<rest>.*)$")


def clean_heading_text(text: str) -> str:
    text = re.sub(r"</?u>", "", text)
    text = text.replace("**", "").replace("*", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def remove_empty_bold(markdown: str) -> str:
    # Word leaves empty bold runs around line breaks: "**  \n**"
    markdown = re.sub(r"(?m)^\*\*[ \t]*\\?\n\*\*[ \t]*$", "", markdown)
    markdown = re.sub(r"(?m)^\*\*[ \t]*$", "", markdown)
    return re.sub(r"\n{3,}", "\n\n", markdown)


def number_captions(heading: str, counters: dict, state: dict, chapter: int) -> str:
    """Fill in missing Figure/Table numbers and turn repeated headings into legends."""
    match = CAPTION.match(heading)
    if not match:
        return heading
    key = (match["supp"] or "") + match["kind"]
    rest = match["rest"].strip()
    legend = bool(match["legend"])
    explicit = f"{match['num']}{match['letter'] or ''}" if match["num"] else None
    last = state.get("last")  # (key, label, rest) of the previous caption (not legend)
    # A heading identical to the previous caption is that caption's legend
    if not legend and last and last[0] == key and last[2] == rest and explicit in (None, last[1]):
        legend = True
        label = last[1]
        log(f"  ch{chapter:02d}: relabeled repeat as legend: {key} {label}")
    elif explicit:
        counters[key] = int(match["num"])
        label = explicit
    elif legend:
        label = str(counters.get(key, 0))
    else:
        counters[key] = counters.get(key, 0) + 1
        label = str(counters[key])
        log(f"  ch{chapter:02d}: numbered {key} {label}: {rest[:60]}")
    if not legend:
        state["last"] = (key, label, rest)
    state.setdefault("captions", []).append((key, label, rest, legend))
    prefix = match["prefix"] or ""
    legend_text = " Legend" if legend else ""
    return f"{prefix}{match['supp'] or ''}{match['kind']} {label}{legend_text}: {rest}".strip()


def normalize_title(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text).replace("*", "").replace("\\", "")
    return re.sub(r"\s+", " ", text).strip().rstrip(".").lower()


def resolve_references(markdown: str, all_captions: dict, chapter: int) -> str:
    """Fill 'Figure : <title>' cross-references (lost Word REF fields) using caption titles.

    Search order: this chapter's captions, this chapter's legends, then other chapters
    (written as 'Chapter N Figure X').
    """
    lookup = []
    for owner, captions in all_captions.items():
        for key, label, rest, is_legend in captions:
            rank = (0 if owner == chapter else 2) + (1 if is_legend else 0)
            lookup.append((rank, -len(rest), owner, key, label, normalize_title(rest)))
    lookup.sort()
    reference = re.compile(r"(?<![#\w])(Supplemental )?(Figure|Table)\s?:\s?")
    resolved = unresolved = 0

    def substitute(match: re.Match) -> str:
        nonlocal resolved, unresolved
        key = (match.group(1) or "") + match.group(2)
        following = normalize_title(match.string[match.end():match.end() + 300])
        for _rank, _length, owner, caption_key, label, title in lookup:
            # in-text references are sometimes cut short, e.g. "(Figure : Rev Response Element)"
            cut = re.split(r"[)*;]", following)[0].strip()
            if caption_key == key and title and (following.startswith(title[:40])
                                                  or (len(cut) >= 15 and title.startswith(cut))):
                resolved += 1
                where = "" if owner == chapter else f"Chapter {owner} "
                return f"{where}{match.group(1) or ''}{match.group(2)} {label}: "
        unresolved += 1
        log(f"  ch{chapter:02d}: UNRESOLVED reference '{key} : {following[:50]}'")
        return match.group(0)

    output = []
    for line in markdown.split("\n"):
        if line.startswith("#") or line.startswith("!["):
            output.append(line)
        else:
            output.append(reference.sub(substitute, line))
    if resolved or unresolved:
        log(f"  ch{chapter:02d}: cross-references resolved {resolved}, unresolved {unresolved}")
    return "\n".join(output)


def fix_escapes(markdown: str) -> str:
    """pandoc's GFM escapes that Python-Markdown would print literally."""
    output = []
    for line in markdown.split("\n"):
        line = line.replace("\\<", "&lt;").replace("\\>", "&gt;")
        if not line.lstrip().startswith("|"):  # \| is only meaningful inside pipe tables
            line = line.replace("\\|", "|")
        output.append(line)
    return "\n".join(output)


def fix_unbalanced_bold(markdown: str) -> str:
    """Drop dangling ** left where a Word bold run crossed a paragraph break."""
    output = []
    for line in markdown.split("\n"):
        if line.count("**") % 2 == 1 and not line.startswith("#"):
            stripped = line.rstrip()
            if stripped.endswith("**"):
                line = stripped[:-2].rstrip()
            elif line.lstrip().startswith("**"):
                line = line.replace("**", "", 1)
        output.append(line)
    return "\n".join(output)


ALL_BOLD_LINE = re.compile(r"^(?:\*\*[^*]+\*\*\s*)+$")
CAPTION_TEXT = re.compile(r"^(?:Chapter \d+ )?(?:Supplemental )?(?:Figure|Table)\b[^:]*:\s*\S")
IMAGE = re.compile(r'<img src="([^"]+)"[^>]*/?>|!\[[^\]]*\]\(([^)\s]+)[^)]*\)(\{[^}]*\})?')


def bold_caption_text(line: str) -> str | None:
    """A caption typed as bold text rather than a heading.

    Word often splits one bold run into several, so the line may read
    '**Chapter 3** **Figure** **1: Title**' instead of '**Chapter 3 Figure 1: Title**'.
    """
    line = line.strip()
    if not ALL_BOLD_LINE.match(line):
        return None
    text = re.sub(r"\s+", " ", " ".join(re.findall(r"\*\*([^*]+)\*\*", line))).strip()
    return text if CAPTION_TEXT.match(text) else None


def process_markdown(markdown: str, chapter: Chapter, title: str) -> tuple[str, list]:
    """Clean one chapter. Returns (markdown, captions); references are resolved later."""
    markdown = remove_empty_bold(markdown)
    for number, old, new in BODY_FIXES:
        if number == chapter.number and old in markdown:
            markdown = markdown.replace(old, new)
            log(f"  ch{chapter.number:02d}: body fix '{old}' -> '{new}'")

    lines = markdown.split("\n")
    output: list[str] = []
    counters: dict = {}
    caption_state: dict = {}
    heading_index = 0
    paper_started = False
    last_heading = title
    caption_level = 3

    for line in lines:
        bold_caption = bold_caption_text(line)
        if bold_caption:  # caption typed as a bold paragraph instead of a heading
            line = f"{'#' * caption_level} {bold_caption}"
            log(f"  ch{chapter.number:02d}: promoted bold caption to heading: {bold_caption[:50]}")
        heading = HEADING_LINE.match(line) if line.startswith("#") else None
        if heading:
            level = len(heading.group(1))
            text = clean_heading_text(heading.group(2))
            if not text:
                continue  # drop empty headings
            for number, old, new in HEADING_FIXES:
                if number == chapter.number and text == old:
                    text = new
                    log(f"  ch{chapter.number:02d}: heading fix '{old}' -> '{new}'")
            text = number_captions(text, counters, caption_state, chapter.number)
            if chapter.has_paper:
                if heading_index == 0 and text.lower() in ("abstract", "chapter abstract"):
                    text = "Chapter abstract"
                elif heading_index == 1:
                    paper_started = True  # paper title stays at this level
                elif paper_started:
                    level = min(level + 1, 6)
            heading_index += 1
            last_heading = text
            if CAPTION.match(text):
                caption_level = level
            output.append(f"{'#' * level} {text}")
            continue

        def replace_image(match: re.Match) -> str:
            source = match.group(1) or match.group(2)
            target = str(Path(source).with_suffix(".png")) if Path(source).suffix.lower() in (
                VECTOR_EXTENSIONS | TIFF_EXTENSIONS) else source
            alt = re.sub(r"[\[\]]", "", last_heading)
            return f"![{alt}]({target}){{ loading=lazy }}"

        images = IMAGE.findall(line)
        line = IMAGE.sub(replace_image, line)
        if len(images) > 1:  # one figure per paragraph so each scales to the page width
            line = re.sub(r"\}\s*!\[", "}\n\n![", line)
        output.append(line)

    body = fix_escapes(fix_unbalanced_bold("\n".join(output))).strip() + "\n"
    return f"# Chapter {chapter.number}: {title}\n\n{body}", caption_state.get("captions", [])


# --------------------------------------------------------------------------
# Inline figures
# --------------------------------------------------------------------------

FIGURE_HEADING = re.compile(
    r"^(?P<hashes>#+) (?P<prefix>Chapter \d+ )?(?P<supp>Supplemental )?(?P<kind>Figure|Table) "
    r"(?P<num>\d+)(?P<letter>[A-Z]?)(?P<legend> Legend)?: ?(?P<rest>.*)$")
FIGURE_SECTION = re.compile(r"^(#+) (Supplemental )?(Figures|Tables)\s*$")
OTHER_END_SECTIONS = re.compile(r"^#+ (References|Supplemental Information)\s*$")
FIGURE_MENTION = re.compile(
    r"(?<![\[\w#-])(?P<supp>Supplemental )?(?:Chapter (?P<chapter>\d+) )?"
    r"(?P<word>Fig(?:ure)?s?\.?|Tables?)\s?(?P<num>\d+)(?P<letter>[A-Z])?(?![\w\]])")
LIST_ITEM = re.compile(r"^(\s*([-*+]|\d+[.)])\s|\s{2,}\S)")


def figure_id(kind: str, supp: str, num: str, letter: str) -> str:
    return f"{'supplemental-' if supp else ''}{kind.lower()}-{num}{letter.lower()}"


def transcribed_tables(table_dir: Path) -> dict:
    """Tables that exist in the Word files only as pictures, transcribed by hand.

    tools/tables/chNN-table-N.md (or -supplemental-table-N.md) replaces the picture
    with a real Markdown table, so it can be searched, copied, and read on a phone.
    """
    found = {}
    if not table_dir.is_dir():
        return found
    for path in sorted(table_dir.glob("ch*-*table-*.md")):
        match = re.fullmatch(r"ch(\d+)-(supplemental-)?table-(\d+)([a-z]?)", path.stem)
        if not match:
            log(f"  WARNING: ignoring oddly named table file {path.name}")
            continue
        chapter = int(match.group(1))
        key = ("Table", "Supplemental " if match.group(2) else "",
               match.group(3), match.group(4).upper())
        found.setdefault(chapter, {})[key] = path.read_text(encoding="utf-8").strip()
    return found


def mention_kind(match: re.Match) -> str:
    """'Fig. 3', 'Figures 1B' -> 'Figure'; 'Table 2', 'Tables 1' -> 'Table'."""
    return "Table" if match["word"].lower().startswith("table") else "Figure"


def split_blocks(markdown: str) -> list[str]:
    return [block for block in re.split(r"\n\s*\n", markdown.strip()) if block.strip()]


@dataclass
class FigureGroup:
    key: tuple          # (kind, supp, num, letter)
    prefix: str         # "Chapter 1 " for chapters that label figures that way
    title: str
    blocks: list        # image and legend blocks in source order
    extra_titles: list  # legend headings whose text differs from the title
    in_figure_section: bool  # sits in back matter, so it can be moved into the text
    start: int          # index of the first block, in the original block list
    end: int            # index after the last block
    absorbed: list = field(default_factory=list)  # extra (start, end) spans merged in
    transcription: str = ""  # Markdown table replacing a picture of a table

    def render(self) -> str:
        kind, supp, num, letter = self.key
        label = f"{self.prefix}{supp}{kind} {num}{letter}"
        is_body = lambda b: b.lstrip().startswith(("![", "|", "<table"))
        body_blocks = [b for b in self.blocks if is_body(b)]
        legend = [b for b in self.blocks if not is_body(b)]
        title = self.title.rstrip()
        if title and not title.endswith((".", "?", "!")):
            title += "."
        caption = [f"**{label}: {title}**" if title else f"**{label}.**"]
        caption += [f"**{t}**" for t in self.extra_titles]
        caption += legend
        body = self.transcription or "\n\n".join(body_blocks)
        css = "book-table" if kind == "Table" else "book-figure"
        head = f'<figure markdown="1" id="{figure_id(*self.key)}" class="{css}">'
        cap = '<figcaption markdown="1">\n\n' + "\n\n".join(caption) + "\n\n</figcaption>"
        # table captions go above the table, figure captions below the image
        parts = [cap, body] if kind == "Table" else [body, cap]
        return head + "\n\n" + "\n\n".join(x for x in parts if x) + "\n</figure>"


def collect_figure_groups(blocks: list[str]) -> list[FigureGroup]:
    groups: list[FigureGroup] = []
    by_key: dict = {}
    # Back matter: a "Figures"/"Tables" section, or anything after References, where
    # captions are collected away from the text that cites them.
    section_level = None
    back_matter = False
    index = 0
    while index < len(blocks):
        block = blocks[index]
        first_line = block.split("\n", 1)[0]
        section = FIGURE_SECTION.match(first_line)
        if section:
            section_level = len(section.group(1))
            back_matter = True
            index += 1
            continue
        if first_line.startswith("#"):
            level = len(first_line) - len(first_line.lstrip("#"))
            heading = FIGURE_HEADING.match(first_line)
            if OTHER_END_SECTIONS.match(first_line):
                back_matter = True
            if not heading and section_level is not None and level <= section_level:
                section_level = None
        heading = FIGURE_HEADING.match(first_line) if block.startswith("#") else None
        if not heading:
            index += 1
            continue
        key = (heading["kind"], heading["supp"] or "", heading["num"], heading["letter"] or "")
        start = index
        content: list[str] = []
        extra_titles: list[str] = []
        title = heading["rest"].strip()
        index += 1
        while index < len(blocks):  # absorb images, legend text, and the legend heading
            nxt = blocks[index]
            nxt_heading = FIGURE_HEADING.match(nxt.split("\n", 1)[0]) if nxt.startswith("#") else None
            if nxt_heading and (nxt_heading["kind"], nxt_heading["supp"] or "",
                                nxt_heading["num"], nxt_heading["letter"] or "") == key:
                legend_title = nxt_heading["rest"].strip()
                if normalize_title(legend_title) != normalize_title(title):
                    extra_titles.append(legend_title)
                index += 1
                continue
            if nxt.startswith("#"):
                break
            content.append(nxt)
            index += 1
        has_body = any(b.lstrip().startswith(("![", "|", "<table")) for b in content)
        if not has_body and not content:
            continue  # bare caption heading with nothing under it: leave as-is
        if key in by_key:  # same figure captioned twice (e.g. combined A/B legend): merge
            existing = by_key[key]
            existing.extra_titles.append(title)
            existing.blocks.extend(content)
            existing.extra_titles.extend(extra_titles)
            existing.end = index
            existing.absorbed.append((start, index))
            continue
        group = FigureGroup(key, heading["prefix"] or "", title, content, extra_titles,
                            back_matter, start, index)
        by_key[key] = group
        groups.append(group)
    return groups


def inline_figures(markdown: str, chapter: int, transcriptions: dict | None = None) -> tuple[str, dict]:
    """Turn figure caption/image/legend runs into <figure> blocks and move main
    figures from end-of-chapter 'Figures' sections to after their first mention."""
    lines = markdown.split("\n")
    title_line = lines[0]
    blocks = split_blocks("\n".join(lines[1:]))
    groups = collect_figure_groups(blocks)
    if not groups:
        return markdown, {}

    for group in groups:  # swap pictures of tables for their transcriptions
        text = (transcriptions or {}).get(group.key)
        if text:
            group.transcription = text
            log(f"  ch{chapter:02d}: {figure_id(*group.key)} rendered as a real table")
    unused = set(transcriptions or {}) - {g.key for g in groups}
    for key in sorted(unused):
        log(f"  WARNING: ch{chapter:02d} transcription {figure_id(*key)} matches no table")

    owned = {}  # block index -> group (for removal/replacement)
    for group in groups:
        spans = [(group.start, group.end)] + group.absorbed
        for start, end in spans:
            for i in range(start, end):
                owned[i] = group

    # Where may a figure be cited? Ordinary body text, outside figure/table/reference sections.
    citable = [True] * len(blocks)
    end_section_level = None
    for i, block in enumerate(blocks):
        first_line = block.split("\n", 1)[0]
        if block.startswith("#") and not FIGURE_HEADING.match(first_line):
            level = len(first_line) - len(first_line.lstrip("#"))
            if end_section_level is not None and level <= end_section_level:
                end_section_level = None
            if FIGURE_SECTION.match(first_line) or OTHER_END_SECTIONS.match(first_line):
                end_section_level = level
        if (end_section_level is not None or i in owned or block.startswith(("#", "![", "<", "|"))):
            citable[i] = False

    by_key = {g.key: g for g in groups}
    by_number: dict = {}
    for g in groups:
        by_number.setdefault(g.key[:3], []).append(g)

    def targets_for(match: re.Match) -> list:
        """'Figure 1B' -> panel 1B; 'Figure 1' -> every panel of Figure 1 (1, 1A, 1B, ...)."""
        if match["chapter"] and int(match["chapter"]) != chapter:
            return []
        kind, supp = mention_kind(match), match["supp"] or ""
        num, letter = match["num"], match["letter"] or ""
        if letter and (kind, supp, num, letter) in by_key:
            return [by_key[(kind, supp, num, letter)]]
        return by_number.get((kind, supp, num), [])

    def movable(group: FigureGroup) -> bool:
        return group.in_figure_section and (INLINE_SUPPLEMENTAL or not group.key[1])

    placement: dict[int, list[FigureGroup]] = {}
    moved = set()
    for i, block in enumerate(blocks):
        if not citable[i]:
            continue
        for match in FIGURE_MENTION.finditer(block):
            for group in targets_for(match):
                if id(group) in moved or not movable(group):
                    continue
                anchor = i
                while (anchor + 1 < len(blocks) and LIST_ITEM.match(blocks[anchor])
                       and LIST_ITEM.match(blocks[anchor + 1])):
                    anchor += 1  # keep lists intact: place after the whole list
                placement.setdefault(anchor, []).append(group)
                moved.add(id(group))

    # Figures never cited by number: keep numeric order, next to their neighbours
    main = [g for g in groups if movable(g)]
    for position, group in enumerate(main):
        if id(group) in moved:
            continue
        neighbour, after = None, True
        for previous in reversed(main[:position]):
            if id(previous) in moved:
                neighbour = previous
                break
        if neighbour is None:
            after = False
            neighbour = next((g for g in main[position + 1:] if id(g) in moved), None)
        if neighbour is None:
            continue  # nothing in this chapter was placed; leave the Figures section as-is
        for anchor, placed in placement.items():
            if neighbour in placed:
                index = placed.index(neighbour)
                placed.insert(index + 1 if after else index, group)
                break
        moved.add(id(group))
        log(f"  ch{chapter:02d}: {figure_id(*group.key)} is never cited; placed "
            f"{'after' if after else 'before'} {figure_id(*neighbour.key)}")

    output: list[str] = []
    emitted = set()
    for i, block in enumerate(blocks):
        group = owned.get(i)
        if group is not None:
            if id(group) not in moved and id(group) not in emitted:
                output.append(group.render())
                emitted.add(id(group))
        else:
            output.append(block)
        for placed in placement.get(i, []):
            output.append(placed.render())
            emitted.add(id(placed))

    # Drop "Figures" section headings left empty by the move
    cleaned: list[str] = []
    for i, block in enumerate(output):
        section = FIGURE_SECTION.match(block.split("\n", 1)[0])
        if section:
            level = len(section.group(1))
            following = output[i + 1] if i + 1 < len(output) else ""
            if not following or (following.startswith("#") and
                                 len(following) - len(following.lstrip("#")) <= level):
                continue
        cleaned.append(block)

    ids = {g.key: figure_id(*g.key) for g in groups}
    log(f"  ch{chapter:02d}: {len(groups)} figures formatted, {len(moved)} moved next to "
        f"their first mention, {len(groups) - len(moved)} left in place")
    return title_line + "\n\n" + "\n\n".join(cleaned) + "\n", ids


def link_figure_references(markdown: str, chapter: int, figure_ids: dict, slugs: dict) -> str:
    """Make 'Figure 3' / 'Chapter 1 Figure 5' in body text link to the figure."""
    count = 0

    def link(match: re.Match) -> str:
        nonlocal count
        target_chapter = int(match["chapter"]) if match["chapter"] else chapter
        ids = figure_ids.get(target_chapter, {})
        kind, supp = mention_kind(match), match["supp"] or ""
        num, letter = match["num"], match["letter"] or ""
        anchor = ids.get((kind, supp, num, letter)) or ids.get((kind, supp, num, ""))
        if not anchor:  # "Figure 1" when only panels 1A, 1B... exist: link to the first panel
            panels = sorted(k for k in ids if k[:3] == (kind, supp, num))
            anchor = ids[panels[0]] if panels else None
        if not anchor:
            return match.group(0)
        page = "" if target_chapter == chapter else f"{slugs[target_chapter]}.md"
        count += 1
        return f"[{match.group(0)}]({page}#{anchor})"

    blocks = markdown.split("\n\n")
    inside_figure = False
    for i, block in enumerate(blocks):
        if block.startswith("<figure"):
            inside_figure = True
        if not inside_figure and not block.startswith(("#", "![", "<", "|")):
            # skip text already inside a markdown link or image
            pieces = re.split(r"(!?\[[^\]]*\]\([^)]*\))", block)
            blocks[i] = "".join(p if p.startswith(("[", "![")) else FIGURE_MENTION.sub(link, p)
                                for p in pieces)
        if "</figure>" in block:
            inside_figure = False
    if count:
        log(f"  ch{chapter:02d}: linked {count} in-text figure references")
    return "\n\n".join(blocks)


# --------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------


def convert_media(media_dir: Path) -> None:
    if not media_dir.exists():
        return
    vector_files = sorted(p for p in media_dir.iterdir() if p.suffix.lower() in VECTOR_EXTENSIONS)
    if vector_files:
        with tempfile.TemporaryDirectory() as temp:
            run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", temp,
                 *[str(p) for p in vector_files]])
            for vector in vector_files:
                pdf = Path(temp) / f"{vector.stem}.pdf"
                png = vector.with_suffix(".png")
                if not pdf.exists():
                    log(f"  WARNING: LibreOffice could not convert {vector.name}")
                    continue
                run(["pdftocairo", "-png", "-r", str(RASTER_DPI), "-singlefile",
                     str(pdf), str(png.with_suffix(""))])
                run(["convert", str(png), "-trim", "+repage", "-bordercolor", "white",
                     "-border", "16", "-resize", f"{MAX_IMAGE_PIXELS}x{MAX_IMAGE_PIXELS}>", str(png)])
                vector.unlink()
    for tiff in sorted(p for p in media_dir.iterdir() if p.suffix.lower() in TIFF_EXTENSIONS):
        run(["convert", f"{tiff}[0]", "-resize", f"{MAX_IMAGE_PIXELS}x{MAX_IMAGE_PIXELS}>",
             str(tiff.with_suffix(".png"))])
        tiff.unlink()
    for raster in sorted(p for p in media_dir.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"}):
        run(["convert", str(raster), "-resize", f"{MAX_IMAGE_PIXELS}x{MAX_IMAGE_PIXELS}>", str(raster)])
    leftovers = [p.name for p in media_dir.iterdir() if p.suffix.lower() not in WEB_IMAGE_EXTENSIONS]
    if leftovers:
        log(f"  WARNING: non-web media left in {media_dir}: {leftovers}")


def recover_charts(markdown: str, chapter: Chapter, media_dir: Path, pdf: Path | None) -> str:
    for fallback in chapter.chart_fallbacks:
        if pdf is None or not pdf.exists():
            log(f"  WARNING: no PDF given; chart '{fallback.heading_contains}' left out")
            continue
        page_text = run(["pdftotext", "-f", str(fallback.pdf_page), "-l", str(fallback.pdf_page),
                         str(pdf), "-"])
        if fallback.verify_text not in page_text:
            log(f"  WARNING: PDF page {fallback.pdf_page} does not contain "
                f"'{fallback.verify_text}'; chart left out")
            continue
        scale = RASTER_DPI / 72
        x0, y0, x1, y1 = fallback.crop_points
        media_dir.mkdir(parents=True, exist_ok=True)
        output = media_dir / fallback.output_name
        run(["pdftocairo", "-png", "-r", str(RASTER_DPI), "-singlefile",
             "-f", str(fallback.pdf_page), "-l", str(fallback.pdf_page),
             "-x", str(int(x0 * scale)), "-y", str(int(y0 * scale)),
             "-W", str(int((x1 - x0) * scale)), "-H", str(int((y1 - y0) * scale)),
             str(pdf), str(output.with_suffix(""))])
        run(["convert", str(output), "-trim", "+repage", "-bordercolor", "white",
             "-border", "16", str(output)])
        relative = f"assets/ch{chapter.number:02d}/media/{fallback.output_name}"
        pattern = re.compile(rf"(?m)^(#+ [^\n]*{re.escape(fallback.heading_contains)}[^\n]*)$")
        markdown, count = pattern.subn(
            lambda m: f"{m.group(1)}\n\n![{fallback.heading_contains}]({relative}){{ loading=lazy }}",
            markdown, count=1)
        log(f"  ch{chapter.number:02d}: recovered Word chart from PDF page {fallback.pdf_page}"
            if count else f"  WARNING: heading for chart '{fallback.heading_contains}' not found")
    return markdown


# --------------------------------------------------------------------------
# Front matter (landing page)
# --------------------------------------------------------------------------


def build_index(front_matter: Path) -> str:
    markdown = run(["pandoc", str(front_matter), "-t", "gfm", "--wrap=none"])
    markdown = re.sub(r"(?m)^> ?", "", markdown)  # pandoc renders centered blocks as quotes
    acknowledgments = re.search(r"\*\*Acknowledgments\*\*\s*(.*?)\n\*\*Abstract\*\*", markdown, re.S)
    abstract = re.search(r"\*\*Abstract\*\*\s*(.*)$", markdown, re.S)
    if not (acknowledgments and abstract):
        raise ValueError("Could not find Acknowledgments/Abstract in front matter")
    committee = [
        "Paul E. Klotman, M.D. (Chair)", "Farhad R. Danesh, M.D.",
        "John Cijiang He, M.D., Ph.D.", "Jason T. Kimata, Ph.D.",
        "James R. Lupski, M.D., Ph.D.", "Michael J. Ross, M.D.",
    ]
    parts = "\n".join(f"- **{PARTS[n]}**: Chapters " + ", ".join(
        f"[{c.number}]({c.slug}.md)" for c in CHAPTERS if c.part == n) for n in PARTS)
    return f"""# HIV Informatics

**Alejandro Rafael Gener**<br>
A dissertation submitted to the Faculty of the Graduate School of Biomedical Sciences,
Baylor College of Medicine, in partial fulfillment of the requirements for the degree of
Doctor of Philosophy. Houston, Texas, September 22, 2021.

## Abstract

{remove_empty_bold(abstract.group(1)).strip()}

## How this book is organized

{parts}

## Acknowledgments

{remove_empty_bold(acknowledgments.group(1)).strip()}

## Dissertation committee

{chr(10).join('- ' + member for member in committee)}

Integrative Molecular and Biomedical Sciences Graduate Program, Baylor College of Medicine.
"""


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def build(sources: Path, docs: Path, pdf: Path | None, reuse_media: bool = False) -> list[tuple[Chapter, str]]:
    check_tools()
    docs.mkdir(parents=True, exist_ok=True)
    built = []
    pages: dict[int, str] = {}
    all_captions: dict[int, list] = {}
    for chapter in CHAPTERS:
        source = sources / chapter.source
        log(f"Chapter {chapter.number}: {source.name}")
        title = chapter_title(source)
        asset_root = Path("assets") / f"ch{chapter.number:02d}"
        if not reuse_media:
            shutil.rmtree(docs / asset_root, ignore_errors=True)
            markdown = run(["pandoc", str(source.resolve()), "-t", "gfm", "--wrap=none",
                            "--shift-heading-level-by=1", f"--extract-media={asset_root}"], cwd=docs)
            convert_media(docs / asset_root / "media")
        else:  # re-run text clean-up only; keep previously converted figures
            with tempfile.TemporaryDirectory() as temp:
                markdown = run(["pandoc", str(source.resolve()), "-t", "gfm", "--wrap=none",
                                "--shift-heading-level-by=1", f"--extract-media={asset_root}"], cwd=Path(temp))
        markdown, captions = process_markdown(markdown, chapter, title)
        markdown = recover_charts(markdown, chapter, docs / asset_root / "media", pdf)
        pages[chapter.number] = markdown
        all_captions[chapter.number] = captions
        built.append((chapter, title))

    transcriptions = transcribed_tables(Path(__file__).resolve().parent / "tables")
    slugs = {chapter.number: chapter.slug for chapter in CHAPTERS}
    resolved_pages = {}
    for chapter in CHAPTERS:  # second pass: cross-references can point to any chapter
        resolved_pages[chapter.number] = resolve_references(
            pages[chapter.number], all_captions, chapter.number)
    figure_ids = {}
    for chapter in CHAPTERS:  # third pass: place figures next to the text that cites them
        resolved_pages[chapter.number], figure_ids[chapter.number] = inline_figures(
            resolved_pages[chapter.number], chapter.number,
            transcriptions.get(chapter.number, {}))
    for chapter in CHAPTERS:  # fourth pass: in-text figure mentions become links
        markdown = link_figure_references(resolved_pages[chapter.number], chapter.number,
                                          figure_ids, slugs)
        (docs / f"{chapter.slug}.md").write_text(markdown, encoding="utf-8")

    remove_unused_media(docs)
    (docs / "index.md").write_text(build_index(sources / "front_matter.docx"), encoding="utf-8")
    log("Wrote index.md")
    return built


def remove_unused_media(docs: Path) -> None:
    """Delete extracted images no page references (e.g. pictures of transcribed tables)."""
    referenced = set()
    for page in docs.glob("*.md"):
        referenced |= {m for m in re.findall(r"\]\((assets/[^)]+)\)", page.read_text(encoding="utf-8"))}
    for media in sorted(docs.glob("assets/*/media/*")):
        if str(media.relative_to(docs)) not in referenced:
            media.unlink()
            log(f"  removed unused image {media.relative_to(docs)}")


def write_nav(built: list[tuple[Chapter, str]], nav_file: Path) -> None:
    """Write nav.yml, which mkdocs.yml pulls in with INHERIT."""
    lines = ["nav:", "  - Home: index.md"]
    for number, part_title in PARTS.items():
        lines.append(f'  - "{part_title}":')
        for chapter, title in built:
            if chapter.part == number:
                label = f"{chapter.number}. {plain_title(title)}".replace('"', "'")
                lines.append(f'      - "{label}": {chapter.slug}.md')
    nav_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"Wrote {nav_file}")


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sources", type=Path, default=root / "sources")
    parser.add_argument("--docs", type=Path, default=root / "docs")
    parser.add_argument("--pdf", type=Path, default=root / "sources" / "HIV_Informatics_v1.pdf")
    parser.add_argument("--nav", type=Path, default=root / "nav.yml")
    parser.add_argument("--log", type=Path, default=root / "tools" / "import_log.txt")
    parser.add_argument("--reuse-media", action="store_true",
                        help="skip figure extraction/conversion and reuse docs/assets (faster re-runs)")
    args = parser.parse_args()

    built = build(args.sources, args.docs, args.pdf, args.reuse_media)
    write_nav(built, args.nav)
    args.log.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"\nDone. {len(built)} chapters written to {args.docs}")


if __name__ == "__main__":
    main()
