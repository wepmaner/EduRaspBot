# Makefile для запуска тестов Telegram бота

.PHONY: help install test test-unit test-integration test-cov test-html test-fast clean

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Показать справку
	@echo "$(GREEN)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости для тестирования
	@echo "$(GREEN)📦 Установка зависимостей...$(NC)"
	pip install -r requirements-test.txt

test: ## Запустить все тесты
	@echo "$(GREEN)🧪 Запуск всех тестов...$(NC)"
	pytest tests/ -v

test-unit: ## Запустить только unit тесты
	@echo "$(GREEN)🔬 Запуск unit тестов...$(NC)"
	pytest tests/test_command_handlers.py tests/test_callback_handlers.py tests/test_utils.py -v

test-integration: ## Запустить интеграционные тесты
	@echo "$(GREEN)🔗 Запуск интеграционных тестов...$(NC)"
	pytest tests/test_integration.py -v

test-cov: ## Запустить тесты с покрытием кода
	@echo "$(GREEN)📊 Запуск тестов с покрытием...$(NC)"
	pytest tests/ --cov=. --cov-report=html --cov-report=term-missing --cov-exclude=tests/*

test-html: ## Запустить тесты с HTML отчетом
	@echo "$(GREEN)📄 Запуск тестов с HTML отчетом...$(NC)"
	pytest tests/ --html=reports/test_report.html --self-contained-html

test-fast: ## Запустить быстрые тесты
	@echo "$(GREEN)⚡ Запуск быстрых тестов...$(NC)"
	pytest tests/ -x -v

test-watch: ## Запустить тесты в режиме наблюдения
	@echo "$(GREEN)👀 Запуск тестов в режиме наблюдения...$(NC)"
	pytest-watch tests/ -- -v

test-parallel: ## Запустить тесты параллельно
	@echo "$(GREEN)🚀 Запуск параллельных тестов...$(NC)"
	pytest tests/ -n auto

test-debug: ## Запустить тесты в режиме отладки
	@echo "$(GREEN)🐛 Запуск тестов в режиме отладки...$(NC)"
	pytest tests/ -v -s --tb=long

clean: ## Очистить временные файлы
	@echo "$(GREEN)🧹 Очистка временных файлов...$(NC)"
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf reports/
	rm -rf __pycache__/
	rm -rf tests/__pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

setup: install ## Настроить проект для тестирования
	@echo "$(GREEN)⚙️  Настройка проекта...$(NC)"
	mkdir -p reports
	mkdir -p htmlcov
	@echo "$(GREEN)✅ Проект настроен!$(NC)"

# Команда по умолчанию
.DEFAULT_GOAL := help

