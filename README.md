# scraper-queue-toy

Django + Celery + Redis + PostgreSQL 기반의 비동기 웹 스크래퍼 토이 프로젝트.

URL을 입력하면 Celery Worker가 비동기로 페이지를 스크래핑하고 결과를 DB에 저장한다.

## 기술 스택

- Backend: Django, Django REST Framework, Celery
- Database: PostgreSQL
- Broker: Redis
- Scraping: requests, BeautifulSoup4

## 로컬 개발 환경

**1. 인프라 실행**
```bash
docker compose up -d
```

**2. 백엔드 설정**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

**3. 서버 실행 (터미널 2개)**
```bash
# 터미널 1 - Django
python manage.py runserver

# 터미널 2 - Celery Worker
celery -A config worker -l info
```

## API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/tasks/` | URL 제출 → 스크래핑 태스크 생성 |
| GET | `/api/tasks/` | 전체 태스크 목록 |
| GET | `/api/tasks/{id}/` | 특정 태스크 상태 및 결과 조회 |

## GUI 툴

| 툴 | URL | 용도 |
|----|-----|------|
| pgAdmin | http://localhost:5050 | PostgreSQL 관리 |
| RedisInsight | http://localhost:5540 | Redis 관리 |

## MCP 설정 (Claude Code)

`.mcp.json`을 프로젝트 루트에 생성하고 아래 서버를 설정한다.
`.mcp.json`은 토큰 등 민감 정보가 포함되므로 `.gitignore`에 추가해야 한다.

```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "/path/to/scraper-queue-toy"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://DB_USER:DB_PASSWORD@localhost:5432/DB_NAME"]
    },
    "docker": {
      "command": "uvx",
      "args": ["docker-mcp"]
    },
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "OPENAPI_MCP_HEADERS": "{\"Authorization\": \"Bearer YOUR_NOTION_TOKEN\", \"Notion-Version\": \"2022-06-28\"}"
      }
    }
  }
}
```

| MCP 서버 | 용도 |
|---------|------|
| git | 코드 변경사항 조회 (read-only) |
| postgres | DB 직접 쿼리 |
| docker | 컨테이너 상태 및 로그 확인 |
| notion | 개발 계획 및 진행 상황 관리 |
