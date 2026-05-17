#!/usr/bin/env python3
"""Generate PostgreSQL seed SQL from pseudo_dataset.csv."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


EXPECTED_HEADERS = ["item_id", "part_description", "quantity", "vehicle_application"]
SOURCE_NAME = "pseudo_dataset.csv"
MAKE = "Kia"
CATEGORY_NAME = "Pseudo Dataset"
LOCATION_NAME = "main"


class RawSql(str):
    """SQL fragment that must not be quoted as a string literal."""


def sql_literal(value: str | None) -> str:
    if value is None:
        return "NULL"
    return "'" + value.replace("'", "''") + "'"


def parse_quantity(raw: str, item_id: str) -> int:
    value = raw.strip()
    if value == "":
        return 0
    try:
        quantity = int(value)
    except ValueError as exc:
        raise ValueError(f"item_id {item_id}: quantity must be an integer") from exc
    if quantity < 0:
        raise ValueError(f"item_id {item_id}: quantity cannot be negative")
    return quantity


def normalize_model_name(raw: str) -> str:
    words = raw.strip().split()
    return " ".join(word.capitalize() for word in words)


def parse_vehicle_application(raw: str) -> list[str]:
    value = raw.strip()
    if not value:
        return []

    models: list[str] = []
    for chunk in value.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        for part in re.split(r"\s+Y\s+", chunk):
            part = part.strip()
            if part:
                models.append(normalize_model_name(part))

    return list(dict.fromkeys(models))


def read_rows(path: Path) -> list[dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != EXPECTED_HEADERS:
            raise ValueError(
                f"CSV headers must be {EXPECTED_HEADERS}, got {reader.fieldnames}"
            )

        rows: list[dict[str, object]] = []
        seen_ids: set[int] = set()
        for line_number, row in enumerate(reader, start=2):
            item_id_raw = (row["item_id"] or "").strip()
            description = (row["part_description"] or "").strip()
            vehicle_application = (row["vehicle_application"] or "").strip()

            if not item_id_raw:
                raise ValueError(f"line {line_number}: item_id is required")
            if not description:
                raise ValueError(f"line {line_number}: part_description is required")

            item_id = int(item_id_raw)
            if item_id in seen_ids:
                raise ValueError(f"line {line_number}: duplicated item_id {item_id}")
            seen_ids.add(item_id)

            rows.append(
                {
                    "item_id": item_id,
                    "internal_code": f"PD-{item_id:03d}",
                    "description": description,
                    "quantity": parse_quantity(row["quantity"] or "", item_id_raw),
                    "vehicle_application": vehicle_application,
                    "models": parse_vehicle_application(vehicle_application),
                }
            )

    if not rows:
        raise ValueError("CSV has no data rows")

    return rows


def values_clause(rows: list[tuple[object, ...]]) -> str:
    rendered_rows = []
    for row in rows:
        values = []
        for value in row:
            if isinstance(value, RawSql):
                values.append(str(value))
            elif isinstance(value, int):
                values.append(str(value))
            elif value is None:
                values.append("NULL")
            else:
                values.append(sql_literal(str(value)))
        rendered_rows.append("        (" + ", ".join(values) + ")")
    return ",\n".join(rendered_rows)


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else SOURCE_NAME)
    rows = read_rows(path)

    part_values = [
        (
            row["internal_code"],
            row["description"],
            row["quantity"],
            row["vehicle_application"],
        )
        for row in rows
    ]

    model_names = sorted({model for row in rows for model in row["models"]})
    compatibility_values = [
        (row["internal_code"], model)
        for row in rows
        for model in row["models"]
    ]

    print("-- Generated from pseudo_dataset.csv. Do not edit this SQL by hand.")
    print("BEGIN;")
    print(
        f"""
INSERT INTO part_category (name, description)
VALUES (
    {sql_literal(CATEGORY_NAME)},
    'Repuestos cargados desde pseudo_dataset.csv para pruebas locales.'
)
ON CONFLICT (name) DO UPDATE
SET description = EXCLUDED.description;
"""
    )

    print(
        f"""
WITH source_data (internal_code, part_description, quantity, vehicle_application) AS (
    VALUES
{values_clause(part_values)}
)
INSERT INTO part (
    part_category_id,
    internal_code,
    name,
    unit,
    sale_price,
    purchase_cost,
    warranty_days,
    status
)
SELECT
    pc.part_category_id,
    sd.internal_code,
    sd.part_description,
    'unit',
    0,
    0,
    0,
    'active'
FROM source_data sd
CROSS JOIN part_category pc
WHERE pc.name = {sql_literal(CATEGORY_NAME)}
ON CONFLICT (internal_code) DO UPDATE
SET
    part_category_id = EXCLUDED.part_category_id,
    name = EXCLUDED.name,
    unit = EXCLUDED.unit,
    sale_price = EXCLUDED.sale_price,
    purchase_cost = EXCLUDED.purchase_cost,
    warranty_days = EXCLUDED.warranty_days,
    status = EXCLUDED.status;
"""
    )

    print(
        f"""
WITH source_data (internal_code, part_description, quantity, vehicle_application) AS (
    VALUES
{values_clause(part_values)}
)
INSERT INTO inventory_stock (
    part_id,
    location_name,
    quantity_on_hand,
    reorder_level
)
SELECT
    p.part_id,
    {sql_literal(LOCATION_NAME)},
    sd.quantity,
    0
FROM source_data sd
JOIN part p ON p.internal_code = sd.internal_code
ON CONFLICT (part_id, location_name) DO UPDATE
SET
    quantity_on_hand = EXCLUDED.quantity_on_hand,
    reorder_level = EXCLUDED.reorder_level;
"""
    )

    if model_names:
        model_values = [
            (MAKE, model, RawSql("NULL::integer"), RawSql("NULL::integer"))
            for model in model_names
        ]
        print(
            f"""
WITH source_models (make, model, year_from, year_to) AS (
    VALUES
{values_clause(model_values)}
)
INSERT INTO vehicle_model (make, model, year_from, year_to)
SELECT make, model, year_from, year_to
FROM source_models
ON CONFLICT ON CONSTRAINT uk_vehicle_model DO NOTHING;
"""
        )

    if compatibility_values:
        print(
            f"""
WITH source_compatibility (internal_code, vehicle_model) AS (
    VALUES
{values_clause(compatibility_values)}
)
INSERT INTO part_compatibility (
    part_id,
    vehicle_model_id,
    engine_code,
    notes
)
SELECT
    p.part_id,
    vm.vehicle_model_id,
    NULL,
    'Imported from pseudo_dataset.csv'
FROM source_compatibility sc
JOIN part p
    ON p.internal_code = sc.internal_code
JOIN vehicle_model vm
    ON vm.make = {sql_literal(MAKE)}
   AND vm.model = sc.vehicle_model
   AND vm.year_from IS NULL
   AND vm.year_to IS NULL
ON CONFLICT ON CONSTRAINT uk_part_compatibility DO UPDATE
SET notes = EXCLUDED.notes;
"""
        )

    print("COMMIT;")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
