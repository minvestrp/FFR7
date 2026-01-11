# SmartSec Audit — шаблон проекта

Коротко: фреймворк для аудита смарт-контрактов и крипто-криминалистики.

Структура:

- modules/
  - analyzer/ — интеграция со Slither/Mythril/Manticore
  - extractors/ — получение исходников и данных (Etherscan, IPFS)
  - forensics/ — трассировка транзакций, графы адресов
  - reports/ — генерация отчётов (CSV, PDF, визуализации)

- interface/ — CLI, API (FastAPI), GUI (PyQt5)
- configs/, tests/, main.py

Начало работы:

1. Создайте виртуальное окружение (Python 3.11)
2. Установите зависимости: `pip install -r requirements.txt`
3. Создайте `.env` по примеру `.env.example`
4. Пример запуска: `python main.py --contract path/to/Contract.sol`

Безопасность: используйте инструменты в изолированных средах и проверяйте ключи API.

Тестирование и CI:

- Запуск тестов локально: `pytest -q`
- Настроен GitHub Actions workflow (`.github/workflows/python-app.yml`) для автоматического запуска тестов при push/PR. CI теперь генерирует `junit.xml` и `coverage.xml` и загружает их как артефакты (`pytest-artifacts`) — их можно найти в панели Actions при просмотре конкретного прогона.


БД расследований:

- Простая SQLite-схема доступна в `modules/forensics/db.py` — используйте её для сохранения расследований и графов транзакций.

Если нужно, могу добавить Dockerfile и подробный `pyproject.toml` с фиксацией зависимостей.

---

## Пример использования (реальный сценарий) ✅

1. Анализ контракта по файлу:

```bash
python main.py --contract ./contracts/Token.sol
```

1. Анализ контракта по адресу (Etherscan) и сохранение результата расследования в БД:

```bash
python main.py --contract 0x123456... --address
```

1. Быстрая трассировка адреса и экспорт в JSON:

```bash
python interface/cli.py --address 0xabc... --export json --out report.json
```

1. REST API — создать расследование по адресу (POST) и получить экспорт (GET):

- POST /investigations { "address": "0xabc..." } → возвращает { "investigation_id": 1 }
- GET /investigations/1/export?format=json → возвращает JSON-репорт

---

📦 Рекомендации по развёртыванию

- Используйте Docker (опция): добавление `Dockerfile` и `docker-compose.yml` позволит быстро развернуть сервис с базой и окружением.
- Для безопасного хранения ключей используйте секцию секретов в CI/CD (GitHub Secrets) или HashiCorp Vault.

✨ Дальше мы можем:

- Добавить экспорт в PDF (шаблон отчёта), интеграцию с IPFS/Arweave для архивирования отчётов.
- Построение графов связей с `networkx` + `graphviz` и экспорт в SVG/PDF/PNG.
- Интеграция с Mythril/Manticore и Brownie/Hardhat для динамического анализа и симуляций.

---

## Docker и развёртывание

Добавлены `Dockerfile` (dev), `Dockerfile.prod` (multi-stage production), `docker-compose.yml` и `Makefile` для простого развёртывания и тестирования сервиса.

Базовые команды:

- Сборка dev-образа: `make build` или `docker build -t smartsec:latest .`
- Сборка production-образа: `make build-prod` или `docker build -f Dockerfile.prod -t smartsec:prod .`
- Запуск в фоне (compose): `make up` или `docker-compose up -d --build`
- Остановка: `make down` или `docker-compose down`
- Запуск тестов в контейнере: `make test`

CI: Добавлен workflow `docker-ci.yml` который собирает Docker-образ и запускает `pytest` внутри контейнера, а также отдельную задачу `build-prod`, которая собирает `Dockerfile.prod` (см. `.github/workflows/docker-ci.yml`).

Примечания по WeasyPrint: в production Dockerfile (`Dockerfile.prod`) установлены только необходимые runtime-библиотеки (cairo, pango, gdk-pixbuf). Для сборки колёс требуется наличие build-зависимостей, но они содержатся только в builder-стадии, поэтому итоговый образ получается компактным.



### Экспорт графа и архивирование

- CLI: `--graph-out /path/to/graph.png` — экспорт изображения графа расследования
- CLI: `--upload-ipfs` — загрузить сгенерированный JSON-отчёт в IPFS (Pinata или локальный IPFS)
- CLI: `--upload-arweave` — попытаться загрузить отчёт в Arweave (требует конфигурации)

IPFS: реализован вариант через Pinata API, `ipfshttpclient` или через IPFS CLI. Arweave/Bundlr: добавлена заглушка и первый адаптер для Bundlr.

PDF-отчёты:

- Добавлена возможность экспорта в PDF через WeasyPrint + Jinja2 шаблон (`modules/reports/templates/investigation.html.j2`).
- Требования для WeasyPrint: обратите внимание на системные зависимости (cairo, pango, gdk-pixbuf) — на Windows рекомендуется использовать официальный wheel и инструкции WeasyPrint.
- CLI поддерживает `--export pdf` и `--upload-ipfs` / `--upload-arweave` для автоматического архивирования PDF-отчёта.

Bundlr / Arweave (конфигурация):

- Для загрузки через Bundlr задайте переменные окружения:
  - `BUNDLR_URL` — URL узла Bundlr
  - `BUNDLR_PRIVATE_KEY` — приватный ключ или путь к ключу
  - `BUNDLR_CURRENCY` — валюта (по умолчанию `ar`)

- При отсутствии прямого Arweave клиента `modules/storage/arweave.py` попытается делегировать загрузку через Bundlr при наличии соответствующих переменных.

Админка (защита):

- Для закрытия доступа к админке используйте `ADMIN_API_TOKEN` в `.env`.
- При включённом `ADMIN_API_TOKEN`, UI требует авторизации: можно передавать токен в заголовке `Authorization: Bearer <token>`, через cookie `admin_token` (после /admin/login) или через query param `?token=`.

Пример использования CLI для PDF + загрузки в Bundlr/Arweave:

```bash
python interface/cli.py --address 0x... --export pdf --out report.pdf --upload-arweave
```

Если хочешь, могу добавить пример конфигурации Bundlr и короткий пример скрипта с использованием `bundlr-client` (или инструкции по установке клиента) в следующем шаге.


Если хочешь, могу сразу добавить Dockerfile, Makefile и стальную часть экспорта в PDF.
