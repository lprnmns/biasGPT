# Deployment Guide

## Prerequisites
- Python 3.11+
- Node.js 20+ (web PWA)
- Docker 24+ (optional for container builds)
- Access to required secrets (OKX, Groq, etc.)

## Environment Setup
1. Klonla:
   ```bash
   git clone https://github.com/lprnmns/biasGPT.git
   cd biasGPT
   ```
2. Python bağımlılıkları (`.venv` önerilir):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Web/PWA bağımlılıkları:
   ```bash
   cd apps/web
   pnpm install
   pnpm run build
   ```

## CI/CD
- GitHub Actions `CI` workflow (pull request tetikleme) `make test` çalıştırır.
- Coverage threshold coverage.ini'de `fail_under=80` olarak tanımlı.

## Env Dosyaları
Örnek:
```bash
DATABASE_URL=postgresql://...
GROQ_API_KEY=...
OKX_API_KEY=...
# ...
```

## Deployment Adımları
1. Testleri çalıştır: `make test`
2. Coverage raporu (HTML): `pytest --cov=services --cov=workers --cov-report=html`
3. Docker (isteğe bağlı): `docker build -t biasgpt .`
4. Prod ortamlarda secret yönetimi için CI/CD pipeline'ına güven.
