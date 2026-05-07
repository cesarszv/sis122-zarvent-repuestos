---
name: "Zarvent Repuestos"
description: "Sistema administrativo para venta de repuestos de vehiculos, inventario, compras, ventas, pagos y garantias."
assets:
  logo: "assets/logo.png"
  banner: "assets/banner.jpg"
identity:
  tone: "operativo, confiable, tecnico, automotriz"
  keywords:
    - "control"
    - "confianza"
    - "orden"
    - "inventario"
    - "repuestos"
colors:
  primary: "#1F1B1E"
  secondary: "#404146"
  tertiary: "#E50914"
  neutral: "#F1F1F3"
  surface: "#FFFFFF"
  border: "#D9D8D9"
  muted: "#ECECEC"
  text: "#1F1B1E"
  textMuted: "#787675"
  action: "#E50914"
  actionHover: "#C7000B"
  actionStrong: "#B0000A"
semanticColors:
  success: "#1F7A3F"
  warning: "#B86B00"
  danger: "#B0000A"
  info: "#2563A8"
typography:
  fontFamily: "Inter, Roboto, Segoe UI, Arial, sans-serif"
  h1:
    fontFamily: "Inter"
    fontSize: "1.75rem"
    fontWeight: 700
    lineHeight: "2.25rem"
  h2:
    fontFamily: "Inter"
    fontSize: "1.25rem"
    fontWeight: 700
    lineHeight: "1.75rem"
  body-md:
    fontFamily: "Inter"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: "1.5rem"
  body-sm:
    fontFamily: "Inter"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: "1.25rem"
  label:
    fontFamily: "Inter"
    fontSize: "0.8125rem"
    fontWeight: 600
    lineHeight: "1.125rem"
  table:
    fontFamily: "Inter"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: "1.25rem"
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
  popover: "0 12px 28px rgba(31, 27, 30, 0.14)"
components:
  button:
    radius: "6px"
    minHeight: "40px"
    primaryBg: "#E50914"
    primaryText: "#FFFFFF"
    secondaryBg: "#FFFFFF"
    secondaryText: "#1F1B1E"
    secondaryBorder: "#D9D8D9"
  input:
    radius: "6px"
    bg: "#FFFFFF"
    border: "#D9D8D9"
    focusBorder: "#C7000B"
  card:
    radius: "8px"
    bg: "#FFFFFF"
    border: "#D9D8D9"
  table:
    headerBg: "#FFFFFF"
    rowHoverBg: "#ECECEC"
    border: "#D9D8D9"
  badge:
    radius: "999px"
accessibility:
  normalTextContrast: "4.5:1"
  largeTextContrast: "3:1"
  uiContrast: "3:1"
rules:
  do:
    - "Use a light operational interface with white surfaces and graphite text."
    - "Use red only for primary actions, critical states, and small brand accents."
    - "Use labels, text, and icons together for operational states."
    - "Make tables, filters, forms, stock alerts, and status badges the core UI patterns."
  avoid:
    - "Do not create a marketing landing page for the admin system."
    - "Do not use pastel, purple, beige, or blue-gradient themes."
    - "Do not fill full sections with brand red."
    - "Do not communicate status using color alone."
    - "Do not nest cards inside cards."
---

# Overview

Zarvent Repuestos is an administrative system for a vehicle spare parts sales
business. The UI must feel like an operational tool for managing customers,
suppliers, products, compatibility, stock, purchases, sales, payments,
receipts, returns, and warranties.

The visual identity comes from `logo.png` and `banner.jpg`: strong red brand
letters, graphite gray, black uniforms, a clean light background, and an
automotive service atmosphere. The interface should translate that into a clear,
firm, high-contrast admin product.

The visible product name is **Zarvent Repuestos**. Even though the banner
mentions "Autoservicio", this project models spare parts sales, so "Repuestos"
is the canonical name inside the system.

## Design Direction

Automotive Parts Operations meets Clean Administration. The UI should feel
practical, reliable, and direct: light surfaces, dark text, compact tables,
clear forms, and red accents used with restraint.

This is not a public marketing website. The first screen should be a dashboard
or operational module, not a hero section.

## Colors

The palette is rooted in graphite, black, white, light gray, and one strong
brand red.

- **Primary (#1F1B1E):** main text, sidebar, headings, strong navigation.
- **Secondary (#404146):** secondary text, icons, table metadata.
- **Tertiary (#E50914):** brand accent and primary call-to-action.
- **Neutral (#F1F1F3):** app background.
- **Surface (#FFFFFF):** forms, tables, cards, modals.
- **Border (#D9D8D9):** dividers and component boundaries.
- **Muted (#ECECEC):** row hover, subtle backgrounds, disabled surfaces.

Use `#C7000B` or `#B0000A` when red appears as text on a light background. Use
semantic colors only for meaning: available, low stock, paid, pending, returned,
or critical.

## Typography

Use a sans-serif system that feels modern and readable. `Inter` is preferred;
`Roboto`, `Segoe UI`, `Arial`, and generic `sans-serif` are acceptable
fallbacks.

Headings should be firm and compact. Body text should stay between 14px and
16px. Avoid decorative fonts, justified paragraphs, and tiny text below 12px.

## Layout

Use an 8px-based spacing rhythm. Forms should be grouped by meaning: customer,
product, compatibility, stock, supplier, payment, receipt, and warranty.
Tables should include filters above, actions at the row end, and visible status
badges.

Cards are allowed for dashboard summaries such as today's sales, pending
payments, low-stock products, pending purchases, and returns under review. Do
not turn the whole interface into floating decorative cards.

## Components

Primary buttons use red background and white text. Secondary buttons use white
background, graphite text, and a light border. Destructive actions use the danger
red and require confirmation.

Inputs keep visible labels. Errors appear under the field and describe the
problem. Placeholders can help, but they must not replace labels.

Tables are the main working surface. They should be dense enough for repeated
administrative use while keeping row height, contrast, and alignment readable.

## States

Use badges with both color and text:

- `Activo`: success.
- `Inactivo`: muted.
- `Agotado`: danger.
- `Stock bajo`: warning.
- `Disponible`: success.
- `Venta pendiente`: warning.
- `Venta pagada`: success.
- `Venta anulada`: danger.
- `Compra pendiente`: warning.
- `Compra recibida`: success.
- `Devolucion en revision`: warning.
- `Devolucion aprobada`: success.
- `Devolucion rechazada`: danger.

Never use a colored dot alone for business-critical status.

## Screen Patterns

The dashboard should show today's sales, pending payments, products with stock
below minimum, pending purchase orders, recent inventory movements, and returns
under review.

Product screens should prioritize internal code, OEM code, description,
category, brand, compatibility, stock, price, cost, warranty, and location.

Inventory screens should prioritize product, warehouse, shelf/location, current
stock, minimum stock, maximum stock, and movement history.

Sales screens should prioritize customer, product search, compatibility,
quantity, price, discount, payment, receipt/factura, and stock deduction.

Purchase screens should prioritize supplier, requested items, received items,
cost, pending quantity, and stock update.

Return screens should compare the original sale, returned product, reason,
physical condition, warranty status, resolution, refund amount, and whether the
product returns to stock.

## Accessibility

Normal text must meet at least 4.5:1 contrast. Large text and UI components must
meet at least 3:1. Brand red `#E50914` works with white text for buttons, but
red text over light gray should use `#C7000B` or `#B0000A`.

Do not depend on color alone. Every important state needs visible text and, when
useful, an icon.
