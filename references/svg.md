# Editable SVG output

Use when the user explicitly requests SVG or an SVG-specific edit.

## Construction

Use normal SVG primitives for layout, real `<text>` for wording, gradients for fills, and named groups for related elements. Preserve the canvas and source relationships. Keep recurring styles centralized. For Chinese text, a useful fallback stack is:

```css
font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", "Heiti SC", Arial, sans-serif;
```

Inspect the actual preview font; a fallback declaration does not prove availability.

Prefer supplied vector artwork for complex icons. If only a screenshot exists, preserve its contours and detail; do not simplify them without an explicit user request. Use a disclosed raster region when allowed, or report the limitation if faithful all-vector conversion is unavailable. Do not trace the entire layout or treat scanline path count as a quality metric. Explain reduced semantic editability when relevant.

Do not embed raster images in a promised all-vector SVG. A hybrid SVG is acceptable only when the user permits it; disclose embedded raster content. This restriction applies to the SVG output, not to the separately declared image-only icons in a native PPTX.

## Arrows

SVG markers can scale with stroke width. For important fixed-size arrowheads, use explicit shaft and head geometry, or set marker units deliberately and verify the render. Preserve arrow direction, thickness, length, and feedback loops.

## Presentation compatibility variants

If the user explicitly needs an SVG compatibility variant for presentation import:

- Keep the editable SVG master with real text.
- Make a separate outlined-text variant only when stable appearance is more important than changing words. Label it clearly as outlined, not text-editable.
- Inline needed presentation attributes and resolve supported references/transforms where useful. Test the target conversion if available; simplifying SVG syntax is not a guarantee of Office compatibility.
- For direct word editing in slides, return to the native PPTX workflow. Do not instruct the user to repeat a conversion that already corrupted their layout.

## Validate and iterate

Parse XML; verify all references resolve. Detect raster embedding using namespace-aware inspection of image elements and their hrefs, supplemented by text searches for data URIs. Render and visually compare with the source. Keep generator and SVG synchronized for font, coordinate, content, color, and geometry changes.

A successful XML parse proves syntax, not visual fidelity or import behavior. Deliver the SVG and optional useful preview, and state known mismatches without implying it was tested in an app that was not used.
