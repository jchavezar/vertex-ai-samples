DETECT_REGIONS = """You are analyzing one PDF page rendered as an image. Identify every distinct content region on this page in reading order.

For each region, provide:
- type: one of [heading, body, table, chart, diagram, photo, quote, caption, footnote, header, footer]
- bbox: [x1, y1, x2, y2] as fractions of page dimensions (0.0 to 1.0, top-left origin)
- reading_order: integer starting at 1 (the order a human reads them)
- description: short sentence describing what is there

Rules:
- Reading order: top-to-bottom within a column, left-to-right across columns. Pull quotes and sidebars come AFTER the body text they relate to.
- Each text region should be a coherent block; do NOT split a single column of body text into multiple regions.
- Photos with overlay text count as `photo` (the overlay text will be captured during extraction).
- Page numbers, running titles at top → `header`. Page numbers at bottom → `footer`.
- Charts include bar, line, pie, stacked, scatter, etc. (anything with axes or data encoding).
- Diagrams are non-data visuals: flow charts, architecture diagrams, schematic illustrations.
- If the page is mostly a single full-bleed photo, emit a `photo` region covering the page. BUT if article text (titles, paragraphs, body copy, pull quotes) is painted on top of that photo, ALSO emit separate text regions for that article text. The photo region is for the visual; the text regions are for the words.
- IMPORTANT: only emit one region per visual element. Charts, photos, diagrams, and tables MUST each be a single region (do not subdivide them).
- Tiny overlay elements that are part of a photo's design (single-word taglines, large stat numbers like "71%", watermarks) do NOT need their own text region — they belong to the photo.

Return JSON only, matching the provided schema."""


PAGE_OCR_TEMPLATE = """You are converting a single PDF page (rendered as the attached image) into clean Markdown.

The page contains these STRUCTURED regions that have already been extracted separately. Each is given with its bbox in fractional [x1,y1,x2,y2] coordinates (top-left origin):
{regions_summary}

Hard rules:
1. For every STRUCTURED region above, emit ONLY a single placeholder line on its own:
       <!-- REGION:N -->
   where N is the reading_order number. NEVER describe, transcribe, summarize, or caption the structured region.
2. Suppression rules for text inside structured-region bboxes:
   - For chart, table, and diagram regions: do NOT transcribe ANY text that falls inside their bbox (axis labels, values, legend, headers, cells, etc.). The structured extractor captures it.
   - For photo regions: transcribe article text painted on the photo (titles, body paragraphs, pull quotes) AS NORMAL — they have their own text regions in the list above. Only skip purely decorative overlay (single big stat numbers like "71%", single-word taglines, watermarks); the photo extractor captures those.
3. Output the rest of the page as markdown in proper reading order (top-to-bottom within column, left-to-right across columns; pull quotes / sidebars come after the body they relate to).
4. Reflow body text into normal paragraphs — do NOT preserve hard line breaks from the column wrap.
5. Preserve markdown semantics:
   - Section/article titles → `## Title` (collapse multi-line title text into one single-line heading)
   - Sub-headings (short colored titles inside a section) → `### Subheading`
   - Pull quotes / blockquotes → `> ...` with attribution as `> — Author` on its own line
   - Footnotes / superscript references → keep as `[^N]`
   - Tables in the body (NOT in the structured list) → standard markdown tables
6. Drop running headers and footers (the running document title at the top, page numbers at the bottom).
7. If the page is mostly a structured region with no separate body text, output only the placeholder line.
8. Output Markdown only — no preamble, no commentary, no fences around the whole document."""


CHART_SCHEMA_PROMPT = """You are reading a chart on a PDF page. The chart you must extract is in the bbox region {bbox} (fractional coordinates, top-left origin) on the page image attached.

Your job for THIS pass: identify the chart's STRUCTURE only. Do not read any values yet.

Return JSON with:
- `chart_type` from the enum.
- `title`, `subtitle`, `x_axis_label`, `y_axis_label` if printed; else null.
- `x_categories`: literal bar / tick labels along the x axis (or row labels for non-axis charts like pies/sankeys/radars). Use the exact text shown.
- `series_names`: literal legend entries, in legend order (left-to-right or top-to-bottom). Use the EXACT text shown in the legend / color key. NEVER use placeholders like "Series 1", "Group A", color names, or invented labels.
- `value_unit`: '%' / 'USD' / 'count' / 'index' / etc.
- `legend_visible`: true ONLY if you can clearly read the legend in the image; false otherwise.

If `legend_visible` is false, set `series_names` to ["(legend not visible)"]. Do not invent legend text.
If the chart has a single series and no legend, infer the name from the y-axis label or chart title.
If x_categories appear cut off, only include the labels you can clearly read and set `legend_visible` accordingly."""


CHART_VALUES_PROMPT = """You are reading values from a chart on a PDF page. The chart is in the bbox region {bbox} (fractional coordinates, top-left origin) on the page image attached.

The chart's structure has already been identified:
- chart_type: {chart_type}
- x_categories ({n_categories}): {x_categories}
- series_names ({n_series}): {series_names}
- value_unit: {value_unit}

Your job: read the numeric values for each series at each x_category. Return a ChartData object where:
- Use the EXACT `x_categories` and series names listed above. Do not change, reorder, or relabel them.
- `series[i].values[j]` is the value of series i at x_category j (NUMERIC). Length of every `values` array MUST equal {n_categories}.
- `series[i].value_labels[j]` is the LITERAL TEXT shown on the chart for that cell (string), preserving the printed format. Length MUST equal {n_categories} when populated.
- For stacked bar / pie / donut charts in % unit: the segments at each x position should sum to ~100. Verify before returning; if a stack doesn't sum to 100 the values are wrong.
- For grouped bars: each series is a within-group dimension; values[j] is the bar height for that series at group j.
- If a value is not legible in the image, use null (NOT 0, NOT a guess) — for both `values` and `value_labels`.
- Map series to colors using the legend; do not confuse adjacent colors.
- Read EVERY data label visible. Cross-check against axis ticks for unlabelled bars.
- Write a one-sentence `summary` of the headline insight.
- Set `legend_visible` to the same value the schema pass returned ({legend_visible}).

CRITICAL — RANGES, UNITS, ANNOTATIONS:
- If a chart shows a cell as a RANGE (e.g. "560-850", "$1,370-$1,700", "1.0-1.1%", "(0.6)-1.2%", "490 to 720"):
    * Set `values[j]` to the MIDPOINT (e.g. 705 for "560-850"), so downstream math still works.
    * Set `value_labels[j]` to the LITERAL printed text VERBATIM (e.g. "560-850" or "$560-850" or "1.0-1.1%"). NEVER collapse to a single number in value_labels.
- If a chart shows a unit suffix (%, $, B, M, K) on the printed value, INCLUDE it in `value_labels[j]` (e.g. "53%", "$749B", "2,343").
- For SINGLE-VALUE cells like "53", set value_labels[j] to "53" (verbatim including any unit shown).
- For LIST-style cells (e.g. "$3.3B / 16 awards"), use the literal text in value_labels and a representative number in values.
- NEVER infer or compute a value the chart doesn't print. NEVER replace a printed range with a midpoint in value_labels."""


CHART_RETRY_PROMPT = """You previously extracted this chart but the following automated validators failed:
{failures}

Re-read the chart image (in bbox {bbox} on the attached page) and produce a corrected ChartData using the same schema. Pay special attention to the failure messages above — they describe exactly what's wrong with your previous attempt."""


TABLE_EXTRACT = """Extract this table verbatim. Preserve column order and row order. Empty cells become empty strings. Return JSON matching the schema."""


PHOTO_DESCRIBE = """Describe this image for a screen-reader user in one or two sentences.

`alt_text`: visual description only — what the photo depicts. Do not include any text shown in the image.

`overlay_text`: ONLY decorative overlay — large standalone statistics (e.g., "71%"), single-word taglines, watermarks, brand marks. Do NOT include article copy that is painted on the image (titles, body paragraphs, pull quotes, captions); that is captured separately in the page markdown. If there is no decorative overlay, set this to null.

`caption`: a printed caption underneath the photo (e.g., "Figure X: ..."), if any."""


DIAGRAM_EXTRACT = """This is a non-chart diagram (flowchart, architecture, process, schematic, etc.).

If the structure is a directed/undirected graph, tree, flow, or sequence, output a `mermaid` block (use flowchart, sequenceDiagram, classDiagram, erDiagram, or stateDiagram syntax as appropriate).

If the diagram is too irregular for mermaid (e.g., spatial illustration, infographic with mixed elements), set `mermaid` to null and write a structured prose description in `prose` that lists the components and how they relate.

Capture any printed title in `title` and printed caption in `caption`."""
