---
name: "Zarvent Repuestos"
description: "Administrative system for vehicle spare parts operations: inventory, purchases, sales, payments, receipts, returns, and warranties."
assets:
  logo: "assets/logo.png"
  banner: "assets/banner.jpg"
identity:
  positioning: "Automotive service discipline with human trust and industrial precision."
  tone: "direct, technical, reliable, close, operational"
  keywords:
    - "control"
    - "precision"
    - "service"
    - "trust"
    - "inventory"
    - "motion"
colors:
  primary: "#0D0B0C"
  secondary: "#2D3036"
  tertiary: "#E00010"
  neutral: "#F4F5F7"
  surface: "#FFFFFF"
  surfaceAlt: "#E9EAEE"
  border: "#D1D3D8"
  muted: "#6F747B"
  text: "#0D0B0C"
  textMuted: "#5B6168"
  action: "#E00010"
  actionHover: "#C9000E"
  actionStrong: "#A9000C"
semanticColors:
  success: "#1F7A3F"
  warning: "#B86B00"
  danger: "#A9000C"
  info: "#2563A8"
typography:
  fontFamily: "Inter, Roboto, Segoe UI, Arial, sans-serif"
  display:
    fontFamily: "Inter"
    fontSize: "2rem"
    fontWeight: 800
    lineHeight: "2.5rem"
    letterSpacing: "0"
  h1:
    fontFamily: "Inter"
    fontSize: "1.75rem"
    fontWeight: 800
    lineHeight: "2.25rem"
    letterSpacing: "0"
  h2:
    fontFamily: "Inter"
    fontSize: "1.25rem"
    fontWeight: 700
    lineHeight: "1.75rem"
    letterSpacing: "0"
  body-md:
    fontFamily: "Inter"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: "1.5rem"
    letterSpacing: "0"
  body-sm:
    fontFamily: "Inter"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: "1.25rem"
    letterSpacing: "0"
  label:
    fontFamily: "Inter"
    fontSize: "0.8125rem"
    fontWeight: 700
    lineHeight: "1.125rem"
    letterSpacing: "0"
  label-caps:
    fontFamily: "Inter"
    fontSize: "0.75rem"
    fontWeight: 800
    lineHeight: "1rem"
    letterSpacing: "0.04em"
  table:
    fontFamily: "Inter"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: "1.25rem"
    letterSpacing: "0"
rounded:
  sm: "4px"
  md: "6px"
  lg: "8px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  xxl: "48px"
shadows:
  raised: "0 8px 24px rgba(13, 11, 12, 0.12)"
  popover: "0 16px 40px rgba(13, 11, 12, 0.18)"
motion:
  fast: "120ms ease-out"
  normal: "180ms ease-out"
  emphasis: "240ms cubic-bezier(0.2, 0.8, 0.2, 1)"
components:
  button:
    radius: "6px"
    minHeight: "40px"
    primaryBg: "#E00010"
    primaryText: "#FFFFFF"
    primaryHoverBg: "#C9000E"
    secondaryBg: "#FFFFFF"
    secondaryText: "#0D0B0C"
    secondaryBorder: "#D1D3D8"
  input:
    radius: "6px"
    bg: "#FFFFFF"
    border: "#D1D3D8"
    focusBorder: "#C9000E"
    errorBorder: "#A9000C"
  card:
    radius: "8px"
    bg: "#FFFFFF"
    border: "#D1D3D8"
  table:
    headerBg: "#F4F5F7"
    rowHoverBg: "#E9EAEE"
    border: "#D1D3D8"
  sidebar:
    bg: "#0D0B0C"
    text: "#FFFFFF"
    activeBg: "#E00010"
  badge:
    radius: "999px"
accessibility:
  normalTextContrast: "4.5:1"
  largeTextContrast: "3:1"
  uiContrast: "3:1"
rules:
  do:
    - "Keep the app operational: dashboard, tables, filters, forms, receipts, and status workflows first."
    - "Use red as the active signal, not as page decoration."
    - "Use graphite and black to carry authority, hierarchy, and navigation."
    - "Let white and cold gray surfaces provide the workshop-clean background."
    - "Use diagonal accents only where they add motion or brand recognition."
  avoid:
    - "Do not build a marketing landing page for the admin system."
    - "Do not flood screens with red backgrounds."
    - "Do not use pastel, purple, beige, or blue-gradient themes."
    - "Do not hide business status behind color alone."
    - "Do not nest cards inside cards."
---

# Overview

Zarvent Repuestos is an administrative system for a vehicle spare parts
business. It must feel like a serious operational tool: fast to scan, easy to
trust, and built for people who manage products, stock, purchases, sales,
payments, receipts, returns, and warranties every day.

The visual soul comes from `assets/logo.png` and `assets/banner.jpg`: a heavy
red wordmark, graphite shadows, white textured surfaces, black uniforms, service
staff, location signage, automotive icons, and a sharp diagonal red line that
cuts through the banner with movement. This is not soft retail. This is clean
workshop discipline.

The visible product name is **Zarvent Repuestos**. The banner says
**Autoservicio**, but the system domain is spare parts administration, so
**Zarvent Repuestos** is the canonical name inside the product.

## Design Direction

**Industrial Service Operations** meets **Clean Automotive Administration**.

The interface should feel precise, firm, and human. The logo gives the product
its confidence: black and graphite for mechanical seriousness, red for action,
white and steel gray for clean working surfaces. The banner adds the missing
ingredient: real service staff. The product should not feel like a sterile
spreadsheet; it should feel like the command center behind a real automotive
operation.

Use visual restraint. The brand is strong because the red is concentrated. If
everything is red, nothing is important. That is beginner design. Red is for the
thing the user must notice or do.

## Artistic DNA

- **Red wordmark energy:** `#E00010` is the signature accent. It should drive
  primary actions, active navigation, alerts that need attention, and thin brand
  lines.
- **Graphite authority:** black and charcoal from the uniforms and banner base
  create weight. Use them for navigation, headings, and strong text.
- **Clean textured field:** the logo background is not pure sterile white; it is
  a cold workshop white with subtle gray texture. Translate that as light app
  backgrounds, quiet borders, and controlled contrast.
- **Diagonal motion:** the red diagonal in the banner suggests speed, service,
  and automotive movement. Use it sparingly in headers, empty states, and report
  covers. Do not turn every card into a race stripe.
- **Human service:** the banner shows a team, not just parts. The UI should
  support accountability: users, roles, approvals, receipts, warranty decisions,
  and visible status history.
- **Mechanical clarity:** icons should be practical: package, barcode, car,
  wrench, receipt, warehouse, shield-check, credit-card, truck, rotate-ccw.

## Colors

The palette is rooted in black, graphite, cold whites, steel grays, and one
brand red.

- **Primary (#0D0B0C):** deep workshop black for main text, sidebar, high
  emphasis areas, and strong navigation.
- **Secondary (#2D3036):** graphite for headings, icons, dark dividers, and
  dense operational surfaces.
- **Tertiary (#E00010):** Zarvent red for primary actions, active states, key
  alerts, and small brand accents.
- **Neutral (#F4F5F7):** cold white-gray app background inspired by the logo
  texture.
- **Surface (#FFFFFF):** forms, tables, modals, receipts, and focused work
  panels.
- **Surface Alt (#E9EAEE):** subtle panels, hover rows, disabled fills, and
  grouped form zones.
- **Border (#D1D3D8):** table lines, input borders, dividers, and section
  boundaries.
- **Muted (#6F747B):** secondary copy, metadata, helper text, and inactive
  icons.

Use `#C9000E` or `#A9000C` when red appears as text on a light background or in
compact UI. Keep semantic colors reserved for actual business meaning:
available, low stock, paid, pending, returned, cancelled, approved, or rejected.

## Typography

Use a modern sans-serif system that feels technical and readable. `Inter` is the
preferred UI typeface; `Roboto`, `Segoe UI`, `Arial`, and generic `sans-serif`
are acceptable fallbacks.

Headings should be compact, bold, and direct. Body text should stay between 14px
and 16px for working screens. Avoid decorative fonts, justified paragraphs, and
tiny text below 12px. This is an admin system, not a poster.

Use uppercase labels only for compact metadata such as order codes, stock
status, short section labels, or report tags. Letter spacing stays controlled;
do not fake sophistication with unreadable spaced-out text.

## Layout

Use an 8px spacing rhythm. Screens should prioritize speed and comprehension:
filters at the top, tables in the center, row actions at the end, and summary
metrics where they reduce searching.

The app should open into an operational dashboard or module, not a public hero
section. Hero layouts belong to marketing pages; this product is a tool.

Use density intentionally. Inventory, purchase, sales, and return screens need
more information than a portfolio site. Keep row heights stable, align numbers
right, align labels left, and place destructive actions behind confirmation.

Cards are allowed for repeated dashboard summaries or focused entities. Do not
wrap whole page sections in decorative cards, and do not put cards inside cards.

## Shape and Texture

Corners stay practical: 4px for compact controls, 6px for buttons and inputs,
8px for cards and modals. Avoid pill-shaped components except badges, chips, and
status labels.

The brand assets use texture and shadow, but the app should translate that into
subtle depth, not photographic noise. Use clean surfaces, fine borders, and
occasional shadows for popovers or dialogs.

Diagonal red accents may appear as thin separators, module headers, report
covers, or selected navigation details. Keep them structural. Random decoration
is visual laziness.

## Components

Primary buttons use red background and white text. Secondary buttons use white
background, black text, and a steel border. Tertiary actions should be text or
icon buttons. Destructive actions use danger red, clear labels, and
confirmation.

Inputs always keep visible labels. Placeholders may help, but they must never
replace labels. Error text appears below the field and tells the user exactly
what failed.

Tables are the main working surface. They should include search, filters,
sortable columns, visible row status, pagination, and clear row actions. Numeric
columns such as quantity, cost, price, discount, tax, and totals must align
right.

Badges must combine color and text. Icons are useful when the meaning is
important, but never rely on color alone.

Modals should be used for focused decisions: confirm sale cancellation, approve
return, receive purchase items, adjust stock, or register warranty resolution.
Do not use modals for full workflows that need comparison across multiple
records.

## Iconography

Use simple line icons with consistent stroke width. Prefer familiar operational
symbols over abstract branding shapes.

Recommended icon meanings:

- `Package`: product or spare part.
- `Barcode`: internal code, OEM code, or scan action.
- `Warehouse`: stock location.
- `Truck`: supplier delivery or purchase order.
- `ReceiptText`: sale receipt or invoice.
- `CreditCard`: payment.
- `ShieldCheck`: warranty.
- `RotateCcw`: return.
- `AlertTriangle`: low stock, overdue payment, or critical issue.
- `Wrench`: compatibility, service, or technical detail.

## Imagery

Use the logo cleanly on login, receipts, PDF headers, and print documents. Do
not stretch it, recolor it, or place it on noisy backgrounds.

Use the banner only where the human service story matters: login background,
about page, internal welcome panel, or report cover. Do not use it as a repeated
background texture inside working modules.

When a screen needs an empty state, prefer product, warehouse, receipt, payment,
or warranty iconography over generic illustrations. If a photo is used, it must
show real automotive context or real team/service context.

## States

Use badges with both color and text:

- `Active`: success.
- `Inactive`: muted.
- `Out of Stock`: danger.
- `Low Stock`: warning.
- `Available`: success.
- `Sale Pending`: warning.
- `Sale Paid`: success.
- `Sale Cancelled`: danger.
- `Purchase Pending`: warning.
- `Purchase Received`: success.
- `Return Under Review`: warning.
- `Return Approved`: success.
- `Return Rejected`: danger.
- `Warranty Active`: success.
- `Warranty Expired`: muted.
- `Warranty Claim`: warning.

Business labels in the UI may be localized to LatAm Spanish, but database names,
table names, variable names, enum keys, and design tokens must stay in native
USA English. Do not mix `productoStatus` nonsense with English schemas. Pick a
language per layer and respect it.

## Screen Patterns

The dashboard should show today's sales, pending payments, low-stock products,
pending purchase orders, recent inventory movements, returns under review, and
warranty claims that require action.

Product screens should prioritize internal code, OEM code, description,
category, brand, compatibility, current stock, minimum stock, price, cost,
warranty, and location.

Inventory screens should prioritize product, warehouse, shelf/location, current
stock, minimum stock, maximum stock, movement type, movement reason, and
movement history.

Sales screens should prioritize customer, product search, compatibility,
quantity, price, discount, payment, receipt/invoice, and stock deduction.

Purchase screens should prioritize supplier, requested items, received items,
cost, pending quantity, expected date, received date, and stock update.

Return screens should compare original sale, returned product, reason, physical
condition, warranty status, resolution, refund amount, and whether the product
returns to stock.

Warranty screens should prioritize product, customer, sale reference, warranty
period, claim reason, inspection notes, resolution, replacement/refund decision,
and responsible user.

## Navigation

Primary navigation should be dark graphite or black, echoing the uniforms and
banner base. Active navigation uses a red accent or red fill depending on
contrast. Keep labels clear and direct.

Recommended module names:

- `Dashboard`
- `Products`
- `Inventory`
- `Sales`
- `Purchases`
- `Customers`
- `Suppliers`
- `Payments`
- `Returns`
- `Warranties`
- `Reports`
- `Settings`

Keep module names in English for technical consistency unless the whole UI copy
layer is intentionally localized. Half-translated navigation is mediocre and
confusing.

## Accessibility

Normal text must meet at least 4.5:1 contrast. Large text and UI components must
meet at least 3:1. The brand red `#E00010` works for primary buttons with white
text, but red text over light gray should use `#C9000E` or `#A9000C`.

Do not depend on color alone. Every important state needs visible text and, when
useful, an icon. Focus states must be visible, keyboard navigation must work,
and modals must trap focus until closed.

## Implementation Notes

Use these design tokens directly in CSS variables, Tailwind config, theme
objects, or component libraries. Do not invent near-duplicate grays because "it
looks close". That is how design systems rot.

Suggested CSS variable names:

- `--color-primary`
- `--color-secondary`
- `--color-tertiary`
- `--color-neutral`
- `--color-surface`
- `--color-surface-alt`
- `--color-border`
- `--color-muted`
- `--color-text`
- `--color-text-muted`
- `--color-action`
- `--radius-sm`
- `--radius-md`
- `--radius-lg`
- `--space-xs`
- `--space-sm`
- `--space-md`
- `--space-lg`
- `--space-xl`
- `--space-xxl`

Before shipping a screen, check three things: can a worker scan it quickly, can
they trust the status, and can they complete the next action without hunting. If
the answer is no, the design is not done.
