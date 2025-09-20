# Documentation Updates

## Runbook notları
- **CI**: `.github/workflows/ci.yml` → PR tetiklenir, `make test` çalışır.
- **Coverage**: `%80` altına düşerse `coverage.ini` sayesinde pytest-cov başarısız.
- **Logging/Tracing**: `packages/telemetry` altındaki yardımcılar tüm servislerde kullanılmalı.
- **LLM Budget**: `services/api/monitoring/llm_budget.py` ile günlük limitler izlenir.

Düzenli olarak bu dosyada güncelleme tarihi ve yapılan değişiklikleri belirtin.
