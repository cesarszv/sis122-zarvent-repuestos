# Pseudo Dataset

Este documento explica como se usa `pseudo_dataset.csv` para probar la base de
datos local.

La imagen `pseudo_dataset.jpeg` parece una tabla manual o de hoja de calculo. El
CSV es la version estructurada de esa imagen.

## Source Files

| File | Purpose |
| --- | --- |
| [`../../database/seeds/pseudo_dataset.jpeg`](../../database/seeds/pseudo_dataset.jpeg) | Fuente visual original. |
| [`../../database/seeds/pseudo_dataset.csv`](../../database/seeds/pseudo_dataset.csv) | Datos tabulares extraidos de la imagen. |
| [`../../scripts/database/generate_pseudo_dataset_seed_sql.py`](../../scripts/database/generate_pseudo_dataset_seed_sql.py) | Convierte el CSV en SQL de carga. |
| [`../../database/test_pseudo_dataset.sql`](../../database/test_pseudo_dataset.sql) | Tests SQL para validar la carga. |

## CSV Columns

| Column | Meaning |
| --- | --- |
| `item_id` | Numero de fila de la imagen. |
| `part_description` | Descripcion del repuesto. |
| `quantity` | Cantidad disponible. Si esta vacio, se carga como `0` para stock de prueba. |
| `vehicle_application` | Modelo o modelos donde aplica el repuesto. |

## Mapping To The Relational Model

El CSV no se carga como una tabla suelta. Eso seria flojo.

Se transforma hacia el modelo relacional:

| CSV field | Database target |
| --- | --- |
| `item_id` | `part.internal_code`, usando formato `PD-001`, `PD-002`, etc. |
| `part_description` | `part.name` |
| `quantity` | `inventory_stock.quantity_on_hand` |
| `vehicle_application` | `vehicle_model` y `part_compatibility` |

Todos los repuestos se agrupan en la categoria:

```text
Pseudo Dataset
```

La ubicacion de inventario usada para la prueba es:

```text
main
```

## Vehicle Applications

La columna `vehicle_application` puede traer varios modelos:

```text
SONET, RIO, CARENS
SPORTAGE Y NIRO
```

El script separa modelos por coma y por `Y`.

Ejemplo:

```text
SPORTAGE Y NIRO
```

se convierte en:

```text
Sportage
Niro
```

La imagen no trae anios de vehiculo. Por eso `vehicle_model.year_from` y
`vehicle_model.year_to` pueden quedar en `NULL`. Inventar anios seria peor que
dejar el dato como desconocido.

## Expected Results

La carga correcta debe producir:

| Check | Expected |
| --- | ---: |
| Parts from pseudo dataset | 21 |
| Total stock quantity | 65 |
| Vehicle models | 9 |
| Part compatibility rows | 20 |

Las filas con cantidad vacia en el CSV son:

- `PD-009` EVAPORADOR
- `PD-018` STOP

Para poder probar inventario sin inventar cantidades, esas filas se cargan con
stock `0`.

## Commands

Primero levanta la base:

```bash
make db-up
```

Luego carga y prueba el dataset:

```bash
make db-pseudo-refresh
```

Si Docker requiere `sudo`:

```bash
make db-pseudo-refresh DOCKER="sudo docker"
```

## What The Test Does

El test SQL falla si:

- no hay 21 repuestos cargados
- la suma de stock no es 65
- no existen los 9 modelos esperados
- no existen 20 compatibilidades
- `EVAPORADOR` o `STOP` no quedaron con stock 0

Esto no prueba toda la aplicacion. Prueba que el schema acepta datos reales de
ejemplo y que las relaciones principales funcionan.
