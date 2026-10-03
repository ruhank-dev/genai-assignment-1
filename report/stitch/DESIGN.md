---
name: Luminous Studio Glass
colors:
  surface: '#f7f9ff'
  surface-dim: '#d1dbe8'
  surface-bright: '#f7f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#edf4ff'
  surface-container: '#e4effd'
  surface-container-high: '#dfe9f7'
  surface-container-highest: '#d9e3f1'
  on-surface: '#121d26'
  on-surface-variant: '#534434'
  inverse-surface: '#27313c'
  inverse-on-surface: '#e8f2ff'
  outline: '#867461'
  outline-variant: '#d8c3ad'
  surface-tint: '#855300'
  primary: '#855300'
  on-primary: '#ffffff'
  primary-container: '#f59e0b'
  on-primary-container: '#613b00'
  inverse-primary: '#ffb95f'
  secondary: '#2a4dd7'
  on-secondary: '#ffffff'
  secondary-container: '#4868f1'
  on-secondary-container: '#fffbff'
  tertiary: '#006c49'
  on-tertiary: '#ffffff'
  tertiary-container: '#30c88f'
  on-tertiary-container: '#004e34'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffddb8'
  primary-fixed-dim: '#ffb95f'
  on-primary-fixed: '#2a1700'
  on-primary-fixed-variant: '#653e00'
  secondary-fixed: '#dde1ff'
  secondary-fixed-dim: '#b9c3ff'
  on-secondary-fixed: '#001257'
  on-secondary-fixed-variant: '#0034c0'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#f7f9ff'
  on-background: '#121d26'
  surface-variant: '#d9e3f1'
typography:
  display-hero:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  title-card:
    fontFamily: Plus Jakarta Sans
    fontSize: 15px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: -0.005em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-prominent:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-caption:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.02em
  data-metric:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 28px
    letterSpacing: -0.02em
  data-tabular:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  gutter: 1.25rem
  margin: 1.5rem
  space-xs: 0.375rem
  space-sm: 0.75rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style
The design system manifests an ultra-refined, high-end creative workspace for next-generation generative AI workflows. Designed for creative technologists, art directors, and prompt engineers, it creates an environment of calm, weightless precision. 

The aesthetic is pure **Luxury Glassmorphism**:
- Multi-layered frosted glass panels suspended above an ethereal, slow-shifting organic mesh gradient composed of warm peach, solar butter-yellow, gentle lavender, and pale mint-grey.
- Every viewport evokes the sensation of polished crystal, physical depth, and optical refraction.
- Precision specular highlights simulate ambient studio edge lighting along top borders, providing crisp separation without harsh, opaque lines.
- Interfaces feel lightweight, tactile, and radiant rather than flat or clinically stark.

## Colors
The palette balances translucent optical surfaces with high-energy radiant focal points.

### Background Canvas
- **Ethereal Base Canvas:** Multi-point radial mesh gradients featuring Soft Peach (`#FED7AA`), Butter Yellow (`#FEF08A`), Wisteria Lavender (`#E9D5FF`), and Pale Mint (`#D1FAE5`) overlaid on a warm white core (`#FAFAF9`).

### Surface Translucencies
- **Primary Bento Card Fill:** Gradient fill from `rgba(255, 255, 255, 0.48)` down to `rgba(255, 255, 255, 0.35)`.
- **Inner Active Surface / Nested Tile:** `rgba(255, 255, 255, 0.65)`.
- **Ghost Input / Recessed Wells:** `rgba(255, 255, 255, 0.22)`.
- **Glass Borders:** `rgba(255, 255, 255, 0.60)` to `rgba(255, 255, 255, 0.75)`.

### Accents & Semantic Signals
- **Primary Radiant Accent:** Linear gradient (`135deg, #F59E0B 0%, #FACC15 100%`) applied to primary pill buttons, generation progress bars, active sliders, and glow rings.
- **Secondary Accent:** Electric Periwinkle (`#4F6EF7`) for model routing status, precision dial indicators, and secondary data readouts.
- **Success / Ready:** Soft Emerald Green (`#10B981`) for completed inferences, ready states, and low-latency metrics.
- **Alert / Warning:** Warm Amber (`#F59E0B`).
- **Error / Occlusion:** Coral Rose (`#F43F5E` to `#FB7185`).

### Typography Contrast
- **Primary Ink:** Deep Charcoal (`#1F2933`) providing AAA-grade legibility through translucent backings.
- **Secondary Ink:** Slate Grey (`#64748B`) for metadata, subheadings, and structural unit labels.
- **Muted Ink:** Soft Slate (`#94A3B8`) for placeholders and inactive icons.

## Typography
Typography is crisp, structured, and legible against frosted surfaces.

- **Headlines & Card Titles:** Set in **Plus Jakarta Sans**, providing modern geometric contours with subtle warmth and rounded letterforms that align with the curved glass aesthetic.
- **Body & Controls:** Set in **Inter** for neutral readability, neutral x-height, and precise alignment within inputs, toggles, and toolbars.
- **Telemetry & Numbers:** All numeric readouts (latencies, token counters, VRAM usage, aspect ratios) must enable tabular numerals (`font-feature-settings: "tnum" 1, "cv05" 1`) to eliminate character jitter during real-time streaming updates.

## Layout & Spacing
The layout is optimized for high-density, fixed-ratio desktop workstations (target viewport `1440x1024` with flexible fluid scaling across `1280px` to `1920px`).

### Master Canvas Construction
- The app viewport is framed by a **Master Outer Glass Shell** (`width: calc(100vw - 48px)`, `height: calc(100vh - 48px)`, centered) floating above the ambient blurred canvas.
- Outer container incorporates `margin: 1.5rem` and internal master padding of `1.5rem`.

### Bento Grid Structure
- Internal views utilize a 12-column bento architecture with a uniform `1.25rem` (`20px`) gutter.
- Bento cards span modular units:
  * Primary Canvas/Preview: 8 columns × 8 rows
  * Generation Controls/Parameters: 4 columns × 8 rows
  * Prompt Stream & Status Metrics: 12 columns × 3 rows
- Sub-component padding strictly adheres to:
  * Tight UI groups (pill chips, segmented tabs): `space-xs` (6px) to `space-sm` (12px)
  * Bento card interiors: `space-lg` (24px)
  * Major module separations: `space-xl` (32px)

## Elevation & Depth
Elevation is achieved through light transmission, multi-pass blur filters, and specular micro-reflections rather than heavy dark shadows.

### Optical Layer Tiers
- **Tier 0 (Ethereal Canvas Base):**
  Unfiltered, rich pastel radial meshes with CSS `filter: blur(80px)`.
- **Tier 1 (Giant Outer Shell Container):**
  - Surface: `rgba(255, 255, 255, 0.28)`
  - Backdrop Blur: `blur(40px) saturate(190%)`
  - Border: `1px solid rgba(255, 255, 255, 0.65)`
  - Shadow: `0 24px 64px -12px rgba(31, 38, 135, 0.12), inset 0 1px 2px rgba(255, 255, 255, 0.9)`
  - Radius: `40px`
- **Tier 2 (Bento Grid Cards):**
  - Surface: Linear gradient `180deg, rgba(255, 255, 255, 0.48) 0%, rgba(255, 255, 255, 0.35) 100%`
  - Backdrop Blur: `blur(24px) saturate(180%)`
  - Border: `1px solid rgba(255, 255, 255, 0.60)`
  - Specular Highlight: `inset 0 1px 1px 0 rgba(255, 255, 255, 0.85)`
  - Ambient Shadow: `0 8px 32px 0 rgba(31, 38, 135, 0.08)`
  - Radius: `24px`
- **Tier 3 (Floating Toolbars, Modals & Floating Pills):**
  - Surface: `rgba(255, 255, 255, 0.72)`
  - Backdrop Blur: `blur(32px) saturate(200%)`
  - Border: `1px solid rgba(255, 255, 255, 0.90)`
  - Specular Highlight: `inset 0 1px 0 rgba(255, 255, 255, 1.0)`
  - Ambient Shadow: `0 12px 40px -4px rgba(31, 38, 135, 0.16)`

## Shapes
The design embraces a hyper-rounded, pebble-smooth curvature hierarchy. Sharp angles are entirely avoided to maintain organic glass tactile qualities.

- **Tier 1 Outer Frame:** Exact `40px` outer curvature.
- **Tier 2 Bento Containers:** Exact `24px` corner radius.
- **Tier 3 Nested Control Modules & Cards:** `16px` corner radius.
- **Interactive Controls (Buttons, Inputs, Badges, Search Bars):** Fully rounded pill geometry (`rounded-full` or `9999px`).
- **Circular Display Gauges & Avatars:** Strict `50%` circles with matching inner frosted glass masks.

## Components

### Buttons & Call-to-Actions
- **Hero Radiant Pill Button:**
  - Background: `linear-gradient(135deg, #F59E0B 0%, #FACC15 100%)`
  - Text: `#1F2933`, font-weight 600, label-prominent
  - Border: `1px solid rgba(255, 255, 255, 0.6)`
  - Glow: `box-shadow: 0 4px 20px rgba(245, 158, 11, 0.35), inset 0 1px 1px rgba(255, 255, 255, 0.5)`
  - Radius: `9999px` (Pill)
  - Hover: Subtle scale `1.02`, glow expands to `0 6px 28px rgba(245, 158, 11, 0.5)`.
- **Secondary Frosted Pill Button:**
  - Background: `rgba(255, 255, 255, 0.55)`
  - Backdrop Blur: `blur(12px)`
  - Border: `1px solid rgba(255, 255, 255, 0.7)`
  - Text: `#1F2933`
  - Hover: Background shifts to `rgba(255, 255, 255, 0.85)`.

### Input Fields & Prompt Bars
- **Glass Text Wells:**
  - Background: `rgba(255, 255, 255, 0.28)`
  - Border: `1px solid rgba(255, 255, 255, 0.50)`
  - Inset Depth: `box-shadow: inset 0 2px 4px rgba(31, 38, 135, 0.04)`
  - Focus State: Border illuminates to `#4F6EF7` at `0.8` opacity with an outer ring `0 0 0 3px rgba(79, 110, 247, 0.20)`.
  - Placeholder: `#94A3B8`.

### Chips, Pills & Tags
- **Parameter & Status Badges:**
  - Height: `28px` to `32px`, pill-shaped (`9999px`).
  - Surface: `rgba(255, 255, 255, 0.40)` with `1px solid rgba(255, 255, 255, 0.60)`.
  - Text: `12px`, tabular/semibold.
  - Active Filter State: Background takes on radiant amber tint `rgba(245, 158, 11, 0.15)` with border `rgba(245, 158, 11, 0.5)`.

### Switches & Toggles
- **Frosted Toggle Switch:**
  - Track: `width: 48px`, `height: 26px`, pill-shaped, background `rgba(255, 255, 255, 0.35)` with inset shadow.
  - Thumb: `20px` solid white circle with `0 2px 8px rgba(31, 38, 135, 0.15)`.
  - Checked State: Track shifts to Electric Periwinkle `#4F6EF7` or Radiant Gradient `#F59E0B`.

### Telemetry Gauges & Rings
- **Circular SVG Gauge Rings:**
  - Track: `stroke: rgba(255, 255, 255, 0.25)` with `stroke-width: 6px`.
  - Fill: Conic or gradient stroke (`#4F6EF7` to `#10B981` or `#F59E0B`).
  - Center readout: Tabular metrics with sub-labels underneath.

### Avatars & Asset Thumbnails
- **Pet & Subject Thumbnails:**
  - Radius: `20px` inner rounding within bento slots, or `50%` circles.
  - Framing: `2px solid rgba(255, 255, 255, 0.80)` with specular drop reflection.