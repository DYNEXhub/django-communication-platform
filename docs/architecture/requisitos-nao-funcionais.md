# Requisitos Não-Funcionais + Tech Stack — Django Communication Platform

> **Product Owner:** @po (Pax)
> **Data:** 2026-03-21
> **Versão:** 1.0

---

## Parte 1: Requisitos Não-Funcionais (RNF)

| ID | Categoria | Descrição | Métrica/Critério |
|----|-----------|-----------|------------------|
| RNF-001 | Performance | Requisições de API devem responder em menos de 200ms (p95) para operações CRUD simples | Response time p95 < 200ms |
| RNF-002 | Performance | Dashboard principal deve carregar completamente em menos de 1.5s com 10.000 contatos na base | Time to Interactive < 1.5s |
| RNF-003 | Performance | Envio de campanhas deve processar mínimo 1.000 emails/minuto | Throughput >= 1.000 emails/min |
| RNF-004 | Performance | Sistema deve suportar importação de 50.000 contatos via CSV em menos de 5 minutos | Batch import time < 5min |
| RNF-005 | Scalability | Sistema deve suportar crescimento horizontal (escalar workers Celery independentemente do app Django) | Horizontal scaling capability |
| RNF-006 | Scalability | Banco de dados deve suportar mínimo 1 milhão de contatos sem degradação de performance | DB capacity >= 1M records |
| RNF-007 | Scalability | Sistema deve suportar 100 usuários concorrentes sem degradação | Concurrent users >= 100 |
| RNF-008 | Security | Todas as comunicações devem usar HTTPS/TLS 1.3 | TLS 1.3 enforcement |
| RNF-009 | Security | Senhas devem ser armazenadas com hash bcrypt/Argon2 (nunca plaintext) | Password hashing enforcement |
| RNF-010 | Security | API deve implementar autenticação JWT com refresh tokens | JWT auth implementation |
| RNF-011 | Security | Sistema deve implementar rate limiting (100 req/min por usuário) | Rate limit enforcement |
| RNF-012 | Security | Dados sensíveis (credenciais de API, tokens) devem ser criptografados at-rest | Encryption at-rest |
| RNF-013 | Compliance | Sistema deve ser compatível com GDPR (direito ao esquecimento, exportação de dados) | GDPR compliance |
| RNF-014 | Compliance | Sistema deve ser compatível com LGPD (consentimento, anonimização) | LGPD compliance |
| RNF-015 | Compliance | Sistema deve registrar logs de auditoria para todas operações sensíveis (CRUD de contatos, envio de campanhas) | Audit logging coverage >= 95% |
| RNF-016 | Reliability | Sistema deve ter uptime de 99.5% (máximo 3.6h downtime/mês) | Uptime >= 99.5% |
| RNF-017 | Reliability | Tarefas assíncronas (envio de emails, webhooks) devem ter retry automático (max 3 tentativas) | Retry mechanism implementation |
| RNF-018 | Reliability | Sistema deve ter backups automáticos diários do banco de dados com retenção de 30 dias | Backup frequency + retention |
| RNF-019 | Usability | Interface deve ser responsiva (mobile-first) e funcionar em resoluções 320px+ | Responsive design enforcement |
| RNF-020 | Usability | Sistema deve seguir padrões de acessibilidade WCAG 2.1 Level AA | WCAG 2.1 AA compliance |
| RNF-021 | Maintainability | Código deve ter cobertura de testes >= 80% (unit + integration) | Test coverage >= 80% |
| RNF-022 | Maintainability | Código deve seguir PEP 8 (Python) e ter documentação inline para funções complexas | Linting + documentation enforcement |
| RNF-023 | Observability | Sistema deve expor métricas Prometheus para monitoramento (latência, throughput, erros) | Prometheus metrics endpoint |
| RNF-024 | Observability | Sistema deve ter logging estruturado (JSON) com níveis apropriados (DEBUG, INFO, WARNING, ERROR) | Structured logging implementation |
| RNF-025 | Observability | Sistema deve integrar com Sentry/similar para tracking de erros em produção | Error tracking integration |

---

## Resumo por Categoria

| Categoria | Quantidade |
|-----------|------------|
| Performance | 4 |
| Scalability | 3 |
| Security | 5 |
| Compliance | 3 |
| Reliability | 3 |
| Usability | 2 |
| Maintainability | 2 |
| Observability | 3 |
| **TOTAL** | **25** |

---

## Parte 2: Tech Stack Recomendada

### Backend Framework
**Escolha:** Django 5.1.x + Django REST Framework 3.15+

**Justificativa:**
- Django 5.1 oferece suporte nativo a async views (performance em I/O bound operations como chamadas a APIs externas)
- ORM robusto com migrations automáticas (essencial para evolução rápida do schema)
- Admin panel out-of-the-box para operações internas
- DRF é padrão de mercado para APIs REST em Django (serializers, viewsets, permissions)
- Ecossistema maduro com bibliotecas para autenticação, tarefas assíncronas, email, etc.

**Alternativas Consideradas:**
- FastAPI: Melhor performance bruta, mas menor ecossistema e sem admin panel nativo
- Flask: Mais leve, mas requer configuração manual de muitos componentes (ORM, migrations, admin)

---

### Database
**Escolha:** PostgreSQL 16+

**Justificativa:**
- JSONB nativo (ideal para custom_fields, filter_criteria, template_variables)
- Full-text search (busca em contatos, notas, histórico de comunicação)
- Triggers e stored procedures (úteis para automações complexas)
- Row-Level Security (RLS) para isolamento de dados multi-tenant se necessário
- Replicação nativa (read replicas para queries pesadas de relatórios)
- Extensão pg_trgm para fuzzy search (detecção de duplicatas)

**Alternativas Consideradas:**
- MySQL: Menor suporte a JSONB e full-text search menos robusto
- MongoDB: NoSQL não é ideal para relacionamentos complexos (pipelines, deals, interactions)

---

### Cache
**Escolha:** Redis 7+

**Justificativa:**
- Cache de sessões Django (melhor performance que DB-backed sessions)
- Cache de queries complexas (dashboards, relatórios)
- Rate limiting (usando redis-py ou django-ratelimit)
- Lock distribuído para tarefas Celery (evitar duplicação de envios)
- Pub/Sub para WebSocket (Django Channels)

**Alternativas Consideradas:**
- Memcached: Mais simples, mas sem persistência e sem suporte a estruturas complexas (lists, sets)

---

### Task Queue
**Escolha:** Celery 5.4+ com Redis como broker/backend

**Justificativa:**
- Padrão de facto para tarefas assíncronas em Django
- Suporta retry, scheduling, priorities (essencial para campanhas agendadas)
- Monitoring via Flower (UI para visualizar filas, workers, tarefas)
- Escalável horizontalmente (adicionar workers conforme carga)

**Alternativas Consideradas:**
- Django-Q: Mais leve, mas menos maduro e menor ecossistema
- Dramatiq: Boa alternativa, mas Celery tem integração mais nativa com Django

---

### WebSocket (Real-time)
**Escolha:** Django Channels 4+ com Redis channel layer

**Justificativa:**
- WebSocket nativo para chat em tempo real (RF-018)
- Notificações push para agentes (nova mensagem, deal movido, etc.)
- Integração nativa com Django (usa mesma autenticação, routing)
- Escalável com Redis como backend (pub/sub entre workers)

**Alternativas Consideradas:**
- Socket.IO: Requer Node.js backend separado (complexidade adicional)
- Polling HTTP: Menos eficiente, maior latência

---

### Email Service
**Escolha:** django-anymail 12+ com suporte a múltiplos backends (SendGrid, Mailgun, Amazon SES, SMTP)

**Justificativa:**
- Abstração de múltiplos provedores de email (trocar provider sem alterar código)
- Tracking nativo de opens/clicks via webhooks
- Suporte a templates e variáveis
- Retry automático em falhas temporárias
- Biblioteca madura e bem mantida

**Provedores Recomendados (ordem de preferência):**
1. **SendGrid** — Melhor deliverability, tracking robusto, tier gratuito 100 emails/dia
2. **Mailgun** — Boa alternativa, API simples, tier gratuito 5.000 emails/mês
3. **Amazon SES** — Mais barato em escala ($$0.10/1000 emails), requer AWS

---

### SMS Service
**Escolha:** Twilio SMS API via twilio-python SDK

**Justificativa:**
- Líder de mercado em SMS APIs (cobertura global, deliverability)
- Webhooks nativos para tracking de status (enviado, entregue, falhou)
- Números de teste gratuitos para desenvolvimento
- SDKs oficiais bem documentados
- Preço competitivo (~$0.0075/SMS nos EUA)

**Alternativas Consideradas:**
- Vonage (ex-Nexmo): Boa alternativa, pricing similar
- Amazon SNS: Mais barato, mas menos features (sem conversação, apenas one-way)

---

### WhatsApp Integration
**Escolha:** WhatsApp Business API oficial via Twilio WhatsApp ou Meta Cloud API

**Justificativa:**
- API oficial garantindo compliance e deliverability
- Suporte a templates aprovados (obrigatório para mensagens proativas)
- Webhooks para status de entrega e mensagens recebidas
- Suporte a mídia (imagem, vídeo, documento)

**Provedores:**
1. **Twilio WhatsApp API** — Mais fácil de configurar, mesma conta Twilio do SMS
2. **Meta Cloud API** — Gratuito até 1.000 conversas/mês, requer aprovação Meta Business

**Alternativas Consideradas:**
- WhatsApp Web scraping (WaWeb.js): Viola ToS do WhatsApp, risco de ban
- WhatsApp Business App: Não escalável, sem API programática

---

### Storage (Media Files)
**Escolha:** Amazon S3 ou DigitalOcean Spaces via django-storages

**Justificativa:**
- Armazenamento escalável para anexos de email, mídia WhatsApp, exports CSV
- CDN integrado (CloudFront para S3, Spaces CDN para DO)
- Lifecycle policies (deletar arquivos antigos automaticamente)
- django-storages abstrai backend (trocar provider facilmente)

**Pricing:**
- **S3:** $0.023/GB/mês + $0.09/GB transfer out
- **Spaces:** $5/mês (250GB storage + 1TB transfer) — melhor custo-benefício para pequenas/médias escalas

---

### Monitoring & Observability
**Escolha:** Sentry (errors) + Prometheus + Grafana (metrics) + Loki (logs)

**Justificativa:**
- **Sentry:** Tracking de exceptions em tempo real, breadcrumbs, releases
- **Prometheus:** Métricas de performance (latência, throughput, queue size)
- **Grafana:** Dashboards customizados para métricas Prometheus
- **Loki:** Logs centralizados com query (alternativa mais leve ao ELK)

**Alternativas Consideradas:**
- DataDog: Mais completo, mas $$$$ (caro para projetos iniciais)
- ELK Stack: Pesado, requer infraestrutura dedicada
- New Relic: Bom APM, mas pricing por hosts pode crescer rápido

---

### Testing
**Escolha:** pytest + pytest-django + factory_boy + coverage.py

**Justificativa:**
- pytest é mais poderoso e flexível que unittest nativo Django
- factory_boy para fixtures realistas (evitar hardcoding de dados de teste)
- coverage.py para garantir RNF-021 (>= 80% coverage)

---

### CI/CD
**Escolha:** GitHub Actions

**Justificativa:**
- Gratuito para repositórios públicos, 2.000 minutos/mês para privados
- Integração nativa com GitHub (pull requests, issues)
- Workflows YAML configuráveis (lint, test, build, deploy)
- Secrets management nativo

**Pipeline Sugerido:**
```yaml
on: [push, pull_request]
jobs:
  test:
    - run: ruff check .
    - run: mypy .
    - run: pytest --cov=. --cov-fail-under=80
  deploy:
    - if: branch == main
    - run: deploy to staging/production
```

---

### Deployment
**Escolha:** Railway.app ou Render.com (desenvolvimento/pequena escala) → Kubernetes (produção em escala)

**Justificativa:**
- **Railway/Render:** PaaS simples, zero-config, deploy via Git push (ideal para MVP)
  - Railway: $5/mês por serviço, PostgreSQL incluído
  - Render: Free tier para testes, $7/mês por serviço
- **Kubernetes (AWS EKS/GCP GKE):** Para produção em escala (>100 usuários concorrentes)
  - Auto-scaling de pods Django e workers Celery
  - Zero-downtime deployments
  - Cost optimization via spot instances

---

### Frontend (Sugestão para Fases Futuras)
**Escolha:** Next.js 15 + React 19 + TypeScript + Tailwind CSS + shadcn/ui

**Justificativa:**
- Stack consistente com preferências AIOS (nextjs-react preset)
- Server-side rendering (SEO, performance)
- API Routes (proxy para backend Django se necessário)
- shadcn/ui (componentes premium prontos para CRM/dashboards)

**Alternativas:**
- Vue.js + Nuxt: Boa alternativa, menor ecossistema de componentes enterprise
- SvelteKit: Performance superior, mas menor adoção corporativa

---

## Stack Resumida (Quick Reference)

| Componente | Tecnologia | Versão | Justificativa Chave |
|------------|------------|--------|---------------------|
| Backend | Django + DRF | 5.1.x + 3.15+ | ORM robusto, admin panel, async support |
| Database | PostgreSQL | 16+ | JSONB, full-text search, RLS |
| Cache | Redis | 7+ | Sessions, rate limiting, Celery broker |
| Task Queue | Celery | 5.4+ | Async tasks, scheduling, retry |
| WebSocket | Django Channels | 4+ | Real-time chat, notificações |
| Email | django-anymail | 12+ | Multi-provider abstraction |
| SMS | Twilio API | Latest | Líder de mercado, deliverability |
| WhatsApp | Twilio WhatsApp API | Latest | API oficial, templates |
| Storage | Amazon S3 / DO Spaces | Latest | Escalável, CDN integrado |
| Monitoring | Sentry + Prometheus | Latest | Errors + metrics |
| Testing | pytest + factory_boy | Latest | Fixtures realistas, coverage |
| CI/CD | GitHub Actions | Latest | Gratuito, integração nativa |
| Deploy MVP | Railway / Render | Latest | Zero-config, $5-7/mês |
| Deploy Produção | Kubernetes (EKS/GKE) | Latest | Auto-scaling, HA |
| Frontend (futuro) | Next.js + shadcn/ui | 15+ | SSR, componentes premium |

---

## Deployment Architecture (Production)

```
┌─────────────────────────────────────────────────────────┐
│                     Load Balancer (NGINX)               │
│                     (TLS termination)                   │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐  ┌───────▼──────┐
│  Django App  │  │  Django App  │  (Horizontal scaling)
│  (Gunicorn)  │  │  (Gunicorn)  │
└───────┬──────┘  └───────┬──────┘
        │                 │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │   PostgreSQL    │  (Primary + Read Replicas)
        │   (RDS/CloudSQL)│
        └─────────────────┘

        ┌─────────────────┐
        │     Redis       │  (ElastiCache/MemoryStore)
        │  (Cache+Broker) │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │  Celery Workers │  (Auto-scaling)
        │  (Tasks+Beats)  │
        └─────────────────┘

        ┌─────────────────┐
        │   Amazon S3     │  (Media storage)
        │  + CloudFront   │  (CDN)
        └─────────────────┘
```

---

## Mandatory Output Sections — @po

### Decision
**APROVADO** — Stack recomendada atende todos os requisitos funcionais (RF-001 a RF-055) e não-funcionais (RNF-001 a RNF-025) identificados.

A escolha de **Django + PostgreSQL + Redis + Celery** como core stack é consistente com os requisitos de:
- Performance (RNF-001 a RNF-004) via async views, Redis cache, Celery workers
- Scalability (RNF-005 a RNF-007) via horizontal scaling de workers e read replicas
- Security (RNF-008 a RNF-012) via HTTPS, bcrypt, JWT, rate limiting
- Compliance (RNF-013 a RNF-015) via audit logs e GDPR/LGPD features
- Reliability (RNF-016 a RNF-018) via retry mechanisms e backups automáticos

### Acceptance Criteria
Para que esta stack seja considerada **implementada com sucesso**:

1. ✅ Backend Django 5.1+ com DRF 3.15+ configurado e funcionando
2. ✅ PostgreSQL 16+ como database principal com migrations aplicadas
3. ✅ Redis 7+ configurado para cache, sessions e Celery broker
4. ✅ Celery workers funcionando com retry automático (max 3 tentativas)
5. ✅ django-anymail configurado com provider de email (SendGrid ou Mailgun)
6. ✅ Twilio SMS API integrada com tracking de status
7. ✅ WhatsApp API integrada (Twilio ou Meta Cloud)
8. ✅ Django Channels configurado para WebSocket (chat real-time)
9. ✅ Amazon S3 ou DO Spaces configurado para storage de arquivos
10. ✅ Sentry integrado para tracking de erros
11. ✅ Prometheus + Grafana configurados para métricas
12. ✅ pytest + coverage >= 80%
13. ✅ GitHub Actions CI/CD pipeline funcionando (lint + test + deploy)
14. ✅ Deploy em Railway/Render (MVP) ou Kubernetes (produção)
15. ✅ HTTPS/TLS 1.3 enforcement em produção

### Priority
**Must Have** — Esta stack é o alicerce técnico da plataforma. Sem ela, nenhum requisito funcional pode ser entregue.

Priorização interna:
1. **P0 (Deploy blocker):** Django + PostgreSQL + Redis + DRF (core stack)
2. **P1 (MVP blocker):** django-anymail + Twilio SMS + Celery (comunicação básica)
3. **P2 (MVP enhancer):** Django Channels + WhatsApp API (real-time + multi-canal)
4. **P3 (Produção blocker):** Monitoring (Sentry + Prometheus) + CI/CD (GitHub Actions)
5. **P4 (Scale enabler):** Kubernetes deployment + Auto-scaling

### User Impact
**Impacto Direto:**
- **Usuários Finais (Contatos):** Receberão comunicações via email/SMS/WhatsApp com alta deliverability (Twilio + SendGrid)
- **Usuários Internos (Agentes):** Terão interface web responsiva, real-time chat, dashboards rápidos (<1.5s load)
- **Administradores:** Poderão escalar horizontalmente conforme crescimento de base de contatos
- **Desenvolvedores:** Terão stack madura com ecossistema rico (Django), facilitando manutenção e evolução

**Impacto Técnico:**
- Performance: Cache Redis + async views = response times <200ms (RNF-001)
- Escalabilidade: Celery workers + Kubernetes = suporta 1M+ contatos (RNF-006)
- Confiabilidade: Retry automático + backups = uptime 99.5% (RNF-016)
- Compliance: Audit logs + GDPR features = conformidade legal (RNF-013, RNF-014)

---

— Pax, equilibrando prioridades 🎯
