---
version: alpha
name: GreenCompute Editorial
description: Institutional research-publication design system — Swiss editorial grid, warm paper neutrals, one green accent, serif display with tabular figures. Built to read like CarbonPlan / Our World in Data, not like an AI template.
colors:
  paper: "#FAFAF7"
  surface: "#FFFFFF"
  ink: "#1A1A18"
  ink-soft: "#4A4A45"
  ink-muted: "#7A7A72"
  rule: "#E4E2DA"
  accent: "#0E6B45"
  accent-deep: "#0A5236"
  accent-soft: "#E7F2EC"
  warn: "#9A6B00"
  warn-soft: "#F7EFDC"
  cool: "#1F4E79"
  cool-soft: "#E8F0F7"
  danger: "#A33A2A"
  danger-soft: "#F8E9E6"
  dark-paper: "#121210"
  dark-surface: "#1B1B18"
  dark-ink: "#F2F1EC"
  dark-ink-soft: "#B8B7AE"
  dark-ink-muted: "#8A8A80"
  dark-rule: "#2E2E29"
  dark-accent: "#4CC38A"
  dark-accent-soft: "#12301F"
typography:
  display:
    fontFamily: "Source Serif 4"
    fontSize: 2.75rem
    fontWeight: 700
    lineHeight: 1.08
    letterSpacing: "-0.015em"
  h2:
    fontFamily: "Source Serif 4"
    fontSize: 1.9rem
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  h3:
    fontFamily: "Source Serif 4"
    fontSize: 1.35rem
    fontWeight: 600
    lineHeight: 1.25
  body:
    fontFamily: "Source Sans 3"
    fontSize: 1.0625rem
    fontWeight: 400
    lineHeight: 1.7
  lead:
    fontFamily: "Source Serif 4"
    fontSize: 1.3rem
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "IBM Plex Mono"
    fontSize: 0.72rem
    fontWeight: 500
    letterSpacing: "0.08em"
    textTransform: uppercase
  figure:
    fontFamily: "IBM Plex Mono"
    fontSize: 0.95rem
    fontWeight: 400
  footnote:
    fontFamily: "Source Sans 3"
    fontSize: 0.85rem
    fontWeight: 400
    lineHeight: 1.5
rounded:
  sm: 2px
  md: 4px
  lg: 8px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  xxl: 64px
  section: 88px
components:
  link-inline:
    textColor: "{colors.accent}"
    textDecoration: underline
    textDecorationThickness: 1px
    textUnderlineOffset: 3px
  link-inline-hover:
    textColor: "{colors.accent-deep}"
    textDecoration: underline
  citation:
    textColor: "{colors.ink-soft}"
    fontSize: 0.85rem
    fontFamily: "Source Sans 3"
  source-ref:
    textColor: "{colors.accent}"
    fontFamily: "IBM Plex Mono"
    fontSize: 0.78rem
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "#FFFFFF"
    rounded: "{rounded.sm}"
    padding: 10px 18px
    fontWeight: 600
  button-primary-hover:
    backgroundColor: "{colors.accent-deep}"
  card:
    backgroundColor: "{colors.surface}"
    borderColor: "{colors.rule}"
    rounded: "{rounded.md}"
    padding: 24px
  table-header:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-soft}"
    fontFamily: "IBM Plex Mono"
    fontSize: 0.72rem
    letterSpacing: "0.06em"
    textTransform: uppercase
  figure-caption:
    textColor: "{colors.ink-muted}"
    fontSize: 0.85rem
  badge:
    fontFamily: "IBM Plex Mono"
    fontSize: 0.7rem
    letterSpacing: "0.06em"
    textTransform: uppercase
    rounded: "{rounded.sm}"
    padding: 3px 8px
---

# GreenCompute Editorial

## Overview

GreenCompute is an independent research publication tracking how the world builds, powers, and regulates data centers. The design must read as **institutional research journalism** — the visual register of CarbonPlan, Our World in Data, and IEEE Spectrum — not as a SaaS landing page or an AI template.

The core job of the design is to make dense technical research feel **readable, credible, and human**. That means: a warm paper canvas, a serif display face for editorial authority, tabular monospace figures for data, hairline rules instead of shadows, and one green accent used sparingly. Sources are woven into the prose as inline citations and contextual links — never dumped in a flat bibliography.

## Colors

- **Paper (#FAFAF7):** warm off-white canvas. Never pure white — the warmth is what separates this from a template.
- **Ink (#1A1A18):** near-black with a warm cast for headlines and body.
- **Accent (#0E6B45):** deep institutional green — the only saturated color in the system. Used for links, primary actions, and data highlights. It reads "sustainability" without the neon of AI-generated palettes.
- **Rule (#E4E2DA):** hairline borders and dividers. Structure comes from rules and whitespace, not shadows.
- **Semantic accents:** warn (amber), cool (blue), danger (red) — each with a soft tinted background for badges and status chips. Used sparingly.

## Typography

- **Display / headings:** Source Serif 4 — an editorial serif with real character. Tight line-height, slight negative tracking.
- **Body:** Source Sans 3 — a humanist sans that reads well at length. 1.7 line-height for comfortable long-form.
- **Labels / figures / citations:** IBM Plex Mono — tabular, technical, used for data, metadata, and source references. This is the "research instrument" register.
- **Lead paragraphs:** serif, larger, muted — the classic editorial deck.

## Layout

- Max content width ~1100px, generous vertical rhythm (88px sections).
- Editorial grid: prose column with a narrow margin for figures and pull-quotes where useful.
- Tables are the primary data surface — hairline rules, mono headers, hover row highlight.
- Figures (images) are full-width with captions that carry attribution and source links.

## Components

- **Inline links:** green, underlined, with a subtle offset. Every factual claim that has a source gets an inline citation link.
- **Citations:** small muted text following claims, linking to the source index anchor.
- **Source refs:** mono, green, arrow — "Read the statute ↗" style links that point to primary documents.
- **Cards:** flat, hairline-bordered, used for facility profiles and case studies — no shadows, no gradient.
- **Tables:** the workhorse. Mono uppercase headers, zebra-free, hover highlight.
- **Badges:** mono uppercase chips for status (e.g., "Enacted & In Force", "Target: 2027"). Tinted backgrounds, never neon.

## Do's and Don'ts

### Do
- Use the serif display for all headings — it's the editorial anchor.
- Link sources **in context**: every claim that cites a statute, docket, or press release gets an inline link to the source index.
- Use mono for all numbers, figures, and metadata — it makes data feel measured.
- Let whitespace and hairline rules carry structure. No drop shadows.
- Write like a journalist: bylines, dates, "last updated" stamps, and a clear narrative arc per page.

### Don't
- Don't use gradient backgrounds, glassmorphism, or neon accents.
- Don't center everything — editorial layouts are asymmetric and rhythm-driven.
- Don't use icon-topper cards or equal-weight feature grids (the #1 AI tell).
- Don't dump sources in a flat list at the bottom of a page — cite them where the claim is made.
- Don't use "Insights / Growth / Scale" style vague labels.
- Don't use Inter as the default font — it's the AI-template tell. Serif display + humanist sans + mono is the voice.
