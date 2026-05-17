DOCKER ?= docker
DOCKER_COMPOSE ?= $(DOCKER) compose
NATIVE_POSTGRES_USER ?= $(USER)

ifneq (,$(wildcard .env))
include .env
export
endif

POSTGRES_DB ?= zarvent_repuestos
POSTGRES_USER ?= zarvent
POSTGRES_PASSWORD ?= zarvent_dev_password
POSTGRES_HOST ?= localhost
POSTGRES_PORT ?= 5432
DATABASE_URL ?= postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)

.PHONY: db-up db-down db-reset db-status db-logs db-migrate db-native-create db-native-reset db-apply db-pseudo-seed db-pseudo-test db-pseudo-refresh

db-up:
	$(DOCKER_COMPOSE) up -d postgres

db-down:
	$(DOCKER_COMPOSE) down

db-reset:
	$(DOCKER_COMPOSE) down -v
	$(DOCKER_COMPOSE) up -d postgres

db-status:
	$(DOCKER_COMPOSE) ps

db-logs:
	$(DOCKER_COMPOSE) logs -f postgres

db-migrate:
	@for file in scripts/migrations/*.sql; do \
		if [ -f "$$file" ]; then \
			echo "Applying $$file"; \
			$(DOCKER_COMPOSE) exec -T postgres psql -U "$(POSTGRES_USER)" -d "$(POSTGRES_DB)" --file - < "$$file"; \
		fi; \
	done

db-native-create:
	NATIVE_POSTGRES_USER="$(NATIVE_POSTGRES_USER)" scripts/database/create_native_database.sh

db-native-reset:
	NATIVE_POSTGRES_USER="$(NATIVE_POSTGRES_USER)" scripts/database/reset_native_database.sh

db-apply:
	DATABASE_URL="$(DATABASE_URL)" scripts/database/apply_schema.sh

db-pseudo-seed:
	python3 scripts/database/generate_pseudo_dataset_seed_sql.py database/seeds/pseudo_dataset.csv | \
		$(DOCKER_COMPOSE) exec -T postgres psql -U "$(POSTGRES_USER)" -d "$(POSTGRES_DB)"

db-pseudo-test:
	$(DOCKER_COMPOSE) exec -T postgres psql -U "$(POSTGRES_USER)" -d "$(POSTGRES_DB)" --file - < database/test_pseudo_dataset.sql

db-pseudo-refresh: db-migrate db-pseudo-seed db-pseudo-test
