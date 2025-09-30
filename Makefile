.PHONY: dev api web up down

dev: ## run API + UI (dev)
	uvicorn apps.api.main:app --reload --port 8080 & (cd ui && npm run dev)

web: ## build web container
	docker build -f docker/Dockerfile.web -t perplex-web .

up: ## compose up
	docker compose up -d --build

down:
	docker compose down