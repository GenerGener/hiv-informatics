# HIV Informatics — the book

The web edition of *HIV Informatics* (Alejandro Rafael Gener, PhD dissertation, Baylor College of
Medicine, 2021), built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and
versioned with [mike](https://github.com/jimporter/mike). Readers land on the latest release and
can switch to any earlier one from the version menu in the header.

Live site (once published): <https://genergener.github.io/hiv-informatics/>

## Repository layout

| Path | What it is |
| --- | --- |
| `docs/` | **The book.** One Markdown file per chapter, plus `index.md` (abstract, acknowledgments). Edit these. |
| `docs/assets/chNN/media/` | Figures, converted to PNG from the Word originals. |
| `docs/stylesheets/extra.css` | Style tweaks (figure sizing, caption headings, wide tables) and the Heelbent brand. |
| `docs/assets/brand/` | The Heelbent logo mark and wordmark. |
| `nav.yml` | Sidebar: Parts One–Three and their chapters. |
| `mkdocs.yml` | Site settings: title, theme, license footer, version menu. |
| `sources/` | Original Word chapters and the dissertation PDF, kept for reference and re-import. |
| `tools/build_book.py` | One-time importer: Word → Markdown, with figure conversion and clean-up. |
| `tools/tables/` | Tables that exist in the Word files only as pictures, transcribed into Markdown. |
| `tools/import_log.txt` | Every automatic change the importer made (fixes, numbering, recovered figures). |
| `.github/workflows/publish.yml` | Publishes a version to GitHub Pages when you push a tag. |

## Tutorial

### 1. Put it on GitHub (once)

```bash
cd hiv-informatics
git init -b main
git add .
git commit -m "HIV Informatics book, v1.0"
gh repo create GenerGener/hiv-informatics --public --source . --push
```

Then on GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch →
Branch: `gh-pages` / root**. (The `gh-pages` branch appears after the first publish in step 3.)

If you use a different repo name or account, update `site_url`, `repo_url`, and `repo_name`
in `mkdocs.yml`.

### 2. Preview locally

```bash
python -m pip install -r requirements.txt
mkdocs serve            # http://127.0.0.1:8000, reloads as you edit docs/
```

`mkdocs serve` shows the current draft without the version menu. To preview the versioned
site exactly as readers see it:

```bash
mike deploy 1.0 latest --update-aliases
mike set-default latest
mike serve              # http://127.0.0.1:8000
```

### 3. Publish a version

Every release is a git tag. Pushing a tag runs `.github/workflows/publish.yml`, which builds the
book, publishes it under `/<version>/`, and moves the `latest` alias (the default landing page)
to it. Earlier versions stay online at their own URLs and in the version menu.

```bash
git tag v1.0
git push origin v1.0
```

Next edition:

```bash
# edit docs/*.md, commit
git tag v1.1
git push origin v1.1    # 1.1 becomes "latest"; 1.0 is still selectable
```

To publish a work-in-progress `dev` version without moving `latest`, run the **Publish book**
workflow from the Actions tab and leave the version blank.

Useful mike commands:

```bash
mike list                       # versions currently published
mike delete 0.9 --push          # remove a version
mike retitle 1.0 "1.0 (defense)" --push
```

### 4. Editing the book

Edit the Markdown in `docs/` directly; it is now the source of truth. A few conventions the
importer used:

- Each chapter page starts with `# Chapter N: Title`. Sections are `##`, subsections `###`.
- Chapters 5–8 contain a full manuscript: the chapter's own abstract is **Chapter abstract**,
  and the paper (title, abstract, methods…) is nested one level under its title.
- Figures sit in the text, right after the paragraph that first cites them, with the legend as
  the caption underneath. To move one, cut and paste its whole `<figure>…</figure>` block:

  ```html
  <figure markdown="1" id="figure-4" class="book-figure">

  ![Figure 4: MSTRG.2.16](assets/ch06/media/image12.png){ loading=lazy }

  <figcaption markdown="1">

  **Figure 4: MSTRG.2.16 (GENER1A, GENER1B, GENER13, GENER14, GENER15).**

  Legend text, as many paragraphs as needed.

  </figcaption>
  </figure>
  ```

  Keep the blank lines inside the block; they let the Markdown inside render.
- Link to a figure with its id: `[Figure 4](#figure-4)`, or from another chapter
  `[Chapter 1 Figure 5](01-what-we-believe-about-hiv.md#figure-5)`. Panels get their own ids
  (`#figure-1a`), and supplemental figures are `#supplemental-figure-3`.
- Tables work the same way, in a `class="book-table"` figure, with the caption **above** the
  table (the usual convention) instead of below. Link to one with `[Table 1](#table-1)`.
- Supplemental figures and tables stay in each chapter's "Supplemental" section at the end.
  To move them into the text like the main ones, set `INLINE_SUPPLEMENTAL = True` near the top
  of `tools/build_book.py` and re-run the importer.
- Strikethrough: `~~know~~` (used in the Chapter 1 title).
- Footnotes: `text[^1]` … `[^1]: note`.

### 5. Re-importing from Word (optional)

Only needed if you revise the `.docx` files instead of the Markdown. Requires pandoc ≥ 3,
LibreOffice, poppler-utils, ImageMagick, and `python-docx`.

```bash
python tools/build_book.py                  # full import, including figure conversion (~2 min)
python tools/build_book.py --reuse-media    # text clean-up only, keeps converted figures
```

Re-importing overwrites `docs/*.md` and `nav.yml`, so commit any Markdown edits first.

## What the importer changed (v1.0)

- Copy-edits: "is **market** by" → "marked by" (Ch 2); "known unknown" → "known unknowns",
  "unknown **unknows**" → "unknowns", "Cautionary **tails**" → "tales" (Ch 3);
  "HIV **liner** reference genomes" → "linear" (Ch 10).
- Figure and table numbers lost from Word caption fields ("Figure : …") were renumbered in
  order within each chapter, and in-text references were matched to them by caption title.
- Duplicate captions (heading repeated above the legend) were relabeled "Figure N Legend".
- Captions typed as bold paragraphs were promoted to caption headings.
- Chapter 1 Figure 1 (a native Word chart that pandoc cannot export) was recovered from
  page 50 of the dissertation PDF.
- Figures stored as EMF/TIFF were converted to 200 dpi PNG.
- Figures were moved from end-of-chapter "Figures" sections to just after the paragraph that
  first cites them, legend as caption. Figures never cited by number (Ch 9 Figures 1, 5, 6;
  Ch 10 Figure 3) were placed in numeric order beside their neighbours. In-text mentions such
  as "Figure 2" now link to the figure.
- pandoc escapes that MkDocs prints literally (`\<`, `\>`) were converted.
- Tables were inlined the same way as figures, and five that were pictures in the Word files
  (Ch 7 Table 1; Ch 8 Tables 1–3; Ch 9 Table 1) were transcribed into real Markdown tables, so
  they can be searched, sorted, copied and read on a phone. Ch 9's "x times improvement" column
  was checked against the read counts in the same row.

### Tables still stored as pictures

Seven remain as images, because transcribing a table of data by hand is only worth doing if
every digit is verified:

| Table | Size |
| --- | --- |
| Ch 5 Table 1: pHXB2 divergence from HXB2 | 20 rows × 11 columns |
| Ch 6 Table 1: NL4-3 transcript models | large |
| Ch 6 Table 2: predicted protein domains | medium |
| Ch 6 Table 3: HIV-1/SIV sequences used | large |
| Ch 6 Supplemental Tables 3, 4, 5 | 4, 1 and 6 screens |

To transcribe one, add `tools/tables/ch06-table-1.md` (or `ch06-supplemental-table-3.md`)
containing just the Markdown table, then re-run the importer: it drops the picture, uses the
table, and deletes the now-unused image. Highlighted cells use `<mark>…</mark>`.

The full list is in `tools/import_log.txt`.

## Branding

The header carries the Heelbent gradient, red `#F80309` on the left running to fuchsia
`#FA01F9` on the right, defined once as `--hb-gradient` in `docs/stylesheets/extra.css`.
Change the two hex values there and the header, mobile drawer and accents all follow.

- **Header logo**: `docs/assets/brand/logo-mark.png`, set as `theme.logo` and `theme.favicon`
  in `mkdocs.yml`. The mark has its own red-to-fuchsia gradient, so the CSS gives it a small
  white chip; without it the mark dissolves into the header behind it.
- **Footer wordmark**: `docs/assets/brand/heelbent-wordmark.png`, black on transparent. The CSS
  uses it as a mask and paints it in the footer's own text colour, so one file reads correctly
  in both light and dark mode. It is placed by the `.footer-wordmark` span in `copyright:`.
- **Link colours** are a darkened fuchsia in light mode (`#C2008F`) and a lightened one in dark
  mode (`#FF5CD0`), both of which clear WCAG AA against their backgrounds; the pure brand
  fuchsia does not, at body-text size.

## License

&copy; 2021–2026 Alejandro Rafael Gener. All rights reserved.

Text and figures: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) —
free to share and adapt with credit for non-commercial use; commercial use needs permission.
Importer and workflow code (`tools/`, `.github/`): MIT. See `LICENSE`.

`requirements.txt` pins MkDocs 1.6.x. MkDocs 2.0 is not compatible with Material's
theme or plugins, so keep the pin unless Material announces support.
