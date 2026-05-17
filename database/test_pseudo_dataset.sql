DO $$
DECLARE
    actual_count integer;
    actual_sum integer;
BEGIN
    SELECT count(*)
    INTO actual_count
    FROM part
    WHERE internal_code LIKE 'PD-%';

    IF actual_count <> 21 THEN
        RAISE EXCEPTION 'Expected 21 pseudo dataset parts, got %', actual_count;
    END IF;

    SELECT COALESCE(sum(i.quantity_on_hand), 0)
    INTO actual_sum
    FROM inventory_stock i
    JOIN part p ON p.part_id = i.part_id
    WHERE p.internal_code LIKE 'PD-%'
      AND i.location_name = 'main';

    IF actual_sum <> 65 THEN
        RAISE EXCEPTION 'Expected pseudo dataset stock sum 65, got %', actual_sum;
    END IF;

    SELECT count(*)
    INTO actual_count
    FROM vehicle_model
    WHERE make = 'Kia'
      AND model IN (
          'Carens',
          'Niro',
          'Rio',
          'Seltos',
          'Seltos China',
          'Seltos India',
          'Soluto',
          'Sonet',
          'Sportage'
      )
      AND year_from IS NULL
      AND year_to IS NULL;

    IF actual_count <> 9 THEN
        RAISE EXCEPTION 'Expected 9 pseudo dataset vehicle models, got %', actual_count;
    END IF;

    SELECT count(*)
    INTO actual_count
    FROM part_compatibility pc
    JOIN part p ON p.part_id = pc.part_id
    JOIN vehicle_model vm ON vm.vehicle_model_id = pc.vehicle_model_id
    WHERE p.internal_code LIKE 'PD-%'
      AND vm.make = 'Kia';

    IF actual_count <> 20 THEN
        RAISE EXCEPTION 'Expected 20 pseudo dataset compatibilities, got %', actual_count;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM part p
        JOIN inventory_stock i ON i.part_id = p.part_id
        WHERE p.internal_code = 'PD-009'
          AND p.name = 'EVAPORADOR'
          AND i.quantity_on_hand = 0
    ) THEN
        RAISE EXCEPTION 'Expected PD-009 EVAPORADOR with zero stock';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM part p
        JOIN inventory_stock i ON i.part_id = p.part_id
        WHERE p.internal_code = 'PD-018'
          AND p.name = 'STOP'
          AND i.quantity_on_hand = 0
    ) THEN
        RAISE EXCEPTION 'Expected PD-018 STOP with zero stock';
    END IF;
END $$;

SELECT
    'pseudo_dataset_test_passed' AS result,
    count(*) AS seeded_parts,
    sum(i.quantity_on_hand) AS total_quantity
FROM part p
JOIN inventory_stock i ON i.part_id = p.part_id
WHERE p.internal_code LIKE 'PD-%'
  AND i.location_name = 'main';
