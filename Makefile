up:
	docker-compose up
up_bg:
	docker-compose up -d
down:
	docker-compose down
build:
	docker-compose build
web:
	docker-compose exec web bash
db:
	docker-compose exec db psql --username=postgres --dbname=postgres
.PHONY: up up_bg down build web db
