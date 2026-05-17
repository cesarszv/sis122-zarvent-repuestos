# Scripts

Esta carpeta contiene comandos auxiliares para crear, recrear y aplicar el
schema de la base de datos.

Comandos principales:

```bash
make db-up
make db-reset
make db-native-create
make db-native-reset
make db-pseudo-refresh
```

`make db-pseudo-refresh` aplica migraciones, carga `pseudo_dataset.csv` y corre
tests basicos sobre la carga.
