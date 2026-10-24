.PHONY: format

# приводит все питон-файлы к одному виду: импорты, отступы, кавычки
format:
	python -m ruff check --fix .
	python -m ruff format .
