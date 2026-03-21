# Django Communication Platform — Arquitetura Inicial

> **Projeto:** Django-based Communication Platform with Contact Management
> **Data:** 2026-03-21
> **Versão:** 1.0
> **Agentes AIOS:** @architect (Aria), @analyst (Atlas), @po (Pax)

---

## 📋 Documentos Gerados

Este diretório contém a arquitetura inicial completa do projeto, decomposta em 3 documentos especializados:

### 1. [Diagrama de Classes UML](./class-diagram.mmd)
**Responsável:** @architect (Aria — Visionary)

Diagrama completo em formato Mermaid cobrindo:
- **20+ modelos Django** organizados em 7 domínios
- **Contact Management:** Contact, Company, ContactGroup, Tag, CustomField, Note
- **Communication:** Abstract base + 4 implementações (Email, SMS, WhatsApp, Chat)
- **Channel & Campaign:** Channel, Campaign, Template
- **CRM Pipeline:** Pipeline, PipelineStage, Deal, Interaction
- **Automation:** Automation, Webhook
- **User & Team:** User (extends Django User), Team
- **Audit:** AuditLog

**Visualizar:**
- GitHub/GitLab: Preview automático de arquivos `.mmd`
- VS Code: Extensão "Markdown Preview Mermaid Support"
- Online: [mermaid.live](https://mermaid.live/) (copiar/colar conteúdo)

---

### 2. [Requisitos Funcionais](./requisitos-funcionais.md)
**Responsável:** @analyst (Atlas — Decoder)

**55 requisitos funcionais** organizados em 9 módulos:

| Módulo | RFs | Prioridade Must Have |
|--------|-----|---------------------|
| Contact Management | RF-001 a RF-009 | 7/9 (78%) |
| Communication | RF-010 a RF-018 | 7/9 (78%) |
| Campaigns | RF-019 a RF-024 | 4/6 (67%) |
| Pipelines (CRM) | RF-025 a RF-030 | 4/6 (67%) |
| Automation | RF-031 a RF-035 | 3/5 (60%) |
| Reporting & Analytics | RF-036 a RF-040 | 3/5 (60%) |
| User Management | RF-041 a RF-045 | 3/5 (60%) |
| API | RF-046 a RF-050 | 3/5 (60%) |
| Integrations | RF-051 a RF-055 | 3/5 (60%) |

**Resumo:**
- **Must Have:** 37 (67%)
- **Should Have:** 16 (29%)
- **Could Have:** 2 (4%)

**GAPs Identificados:**
- Integração com calendários (Google Calendar, Outlook)
- Gestão de SLA (Service Level Agreement)
- Multi-idioma (i18n)
- VOIP/Chamadas

---

### 3. [Requisitos Não-Funcionais + Tech Stack](./requisitos-nao-funcionais.md)
**Responsável:** @po (Pax — Balancer)

**25 requisitos não-funcionais** distribuídos em 8 categorias:

| Categoria | Quantidade | Highlights |
|-----------|------------|------------|
| Performance | 4 | Response time <200ms (p95), 1.000 emails/min |
| Scalability | 3 | 1M contatos, 100 usuários concorrentes |
| Security | 5 | HTTPS/TLS 1.3, JWT, rate limiting, encryption at-rest |
| Compliance | 3 | GDPR, LGPD, audit logs 95% coverage |
| Reliability | 3 | Uptime 99.5%, retry automático, backups diários |
| Usability | 2 | Responsivo mobile-first, WCAG 2.1 AA |
| Maintainability | 2 | Test coverage >= 80%, PEP 8 |
| Observability | 3 | Prometheus metrics, structured logging, Sentry |

**Tech Stack Recomendada:**

| Componente | Tecnologia | Versão | Custo Estimado (MVP) |
|------------|------------|--------|---------------------|
| Backend | Django + DRF | 5.1.x + 3.15+ | — |
| Database | PostgreSQL | 16+ | Incluído em PaaS |
| Cache | Redis | 7+ | Incluído em PaaS |
| Task Queue | Celery | 5.4+ | — |
| WebSocket | Django Channels | 4+ | — |
| Email | django-anymail + SendGrid | 12+ | Grátis (100/dia) |
| SMS | Twilio | Latest | $0.0075/SMS |
| WhatsApp | Twilio WhatsApp API | Latest | Variável |
| Storage | DigitalOcean Spaces | Latest | $5/mês |
| Monitoring | Sentry + Prometheus | Latest | Grátis (dev tier) |
| Deploy MVP | Railway / Render | Latest | $5-7/mês por serviço |

**Custo Total Estimado MVP:** ~$20-30/mês (Railway/Render backend + PostgreSQL + Redis + DO Spaces)

---

## 🎯 Próximos Passos Sugeridos

### Fase 1: Validação (1-2 dias)
1. **Review da arquitetura** com stakeholders técnicos
2. **Validação de requisitos** com Product Owner / CEO
3. **Aprovação de tech stack** (especialmente provedores de email/SMS/WhatsApp)

### Fase 2: Setup Inicial (3-5 dias)
1. **Criar repositório Git** e estrutura de projeto Django
2. **Configurar ambiente local** (Django + PostgreSQL + Redis via Docker Compose)
3. **Setup CI/CD** (GitHub Actions para lint + test)
4. **Configurar provedores externos** (SendGrid, Twilio trial accounts)

### Fase 3: MVP Core (2-3 semanas)
1. **Implementar modelos Django** conforme class diagram
2. **Criar API REST** para Contact Management (RF-001 a RF-009)
3. **Implementar comunicação email** (RF-010, RF-011, RF-012)
4. **Implementar comunicação SMS** (RF-013)
5. **Setup Celery** para envio assíncrono
6. **Testes automatizados** (coverage >= 80%)

### Fase 4: Features Avançadas (3-4 semanas)
1. **Campanhas** (RF-019 a RF-024)
2. **Pipelines CRM** (RF-025 a RF-030)
3. **Automações** (RF-031 a RF-035)
4. **WhatsApp integration** (RF-014, RF-015)
5. **Dashboard e relatórios** (RF-036 a RF-040)

### Fase 5: Produção (1-2 semanas)
1. **Monitoring setup** (Sentry + Prometheus + Grafana)
2. **Deploy em staging** (Railway/Render)
3. **Testes de carga** (validar RNF-001 a RNF-007)
4. **GDPR/LGPD compliance audit** (RNF-013, RNF-014)
5. **Deploy em produção**

---

## 📊 Complexidade Estimada

| Aspecto | Complexidade | Justificativa |
|---------|--------------|---------------|
| Backend | **Média-Alta** | 20+ modelos, múltiplas integrações externas |
| Database | **Média** | Relações complexas, mas padrão Django ORM |
| Comunicação | **Alta** | 4 canais (Email, SMS, WhatsApp, Chat), tracking, webhooks |
| Automação | **Alta** | Triggers, condições, actions, retry logic |
| Escalabilidade | **Média** | Celery + Redis resolvem maioria dos casos |
| Compliance | **Alta** | GDPR/LGPD requerem features específicas (anonimização, export, delete) |

**Complexidade Geral:** **7.5/10** (Projeto de médio-grande porte)

**Tempo Estimado (1 dev full-time):** 10-12 semanas para MVP completo

**Tempo Estimado (equipe 3 devs):** 6-8 semanas para MVP completo

---

## 🔗 Referências Técnicas

### Django Ecosystem
- [Django 5.1 Documentation](https://docs.djangoproject.com/en/5.1/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryq.dev/en/stable/)
- [Django Channels Documentation](https://channels.readthedocs.io/)

### Communication APIs
- [Twilio SMS API](https://www.twilio.com/docs/sms)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [SendGrid Email API](https://docs.sendgrid.com/)
- [django-anymail Documentation](https://anymail.dev/)

### Infrastructure
- [PostgreSQL 16 Documentation](https://www.postgresql.org/docs/16/)
- [Redis Documentation](https://redis.io/docs/)
- [Railway Deployment Guide](https://docs.railway.app/)
- [Render Django Deployment](https://render.com/docs/deploy-django)

### Compliance
- [GDPR Compliance Checklist](https://gdpr.eu/checklist/)
- [LGPD Brazil Overview](https://iapp.org/resources/article/brazilian-data-protection-law-lgpd-english-translation/)

---

## 📝 Notas de Arquitetura

### Decisões Arquiteturais Chave

**DA-001: Django como Backend Framework**
- **Rationale:** ORM robusto, admin panel, async support (Django 5.1), ecossistema maduro
- **Alternatives:** FastAPI (melhor performance bruta, menor ecossistema), Flask (muito manual)
- **Impact:** Acelera desenvolvimento inicial, facilita manutenção long-term

**DA-002: PostgreSQL como Primary Database**
- **Rationale:** JSONB nativo, full-text search, RLS, triggers, replicação
- **Alternatives:** MySQL (menor suporte JSONB), MongoDB (relações complexas são anti-pattern)
- **Impact:** Flexibilidade para custom fields, performance em busca, compliance (RLS)

**DA-003: Celery para Tarefas Assíncronas**
- **Rationale:** Padrão Django, retry, scheduling, horizontal scaling
- **Alternatives:** Django-Q (menos maduro), Dramatiq (menor integração nativa)
- **Impact:** Envio de campanhas não bloqueia requests, retry automático, escalável

**DA-004: Multi-Provider Abstraction (django-anymail)**
- **Rationale:** Não ficar locked-in a um provider de email, trocar facilmente
- **Alternatives:** Integração direta SendGrid/Mailgun (lock-in, refactor caro)
- **Impact:** Flexibilidade para trocar provider por custo/deliverability, zero refactor

**DA-005: Twilio como SMS/WhatsApp Provider**
- **Rationale:** Líder de mercado, deliverability, SDKs oficiais, WhatsApp API oficial
- **Alternatives:** Vonage (similar), Amazon SNS (menos features), scrapers (viola ToS)
- **Impact:** Compliance WhatsApp oficial, tracking robusto, suporte global

---

## 🏗️ Arquitetura de Deploy (Produção)

```
Internet
   │
   ▼
Load Balancer (NGINX/Traefik)
   │
   ├─► Django App 1 (Gunicorn) ──┐
   ├─► Django App 2 (Gunicorn) ──┤
   └─► Django App N (Gunicorn) ──┤
                                  │
                                  ▼
                         PostgreSQL Primary
                                  │
                         ┌────────┴────────┐
                         │                 │
                    Read Replica 1    Read Replica 2
                    (Reports)         (Analytics)

Redis Cluster
   │
   ├─► Cache (sessions, queries)
   ├─► Broker (Celery tasks)
   └─► Pub/Sub (Django Channels)

Celery Workers (Auto-scaling)
   ├─► Worker 1 (Email tasks)
   ├─► Worker 2 (SMS tasks)
   ├─► Worker 3 (WhatsApp tasks)
   └─► Worker N (Generic tasks)

Celery Beat (Scheduler)
   └─► Cron jobs (campanhas agendadas, backups)

Amazon S3 / DO Spaces
   └─► Media files (attachments, exports)
        └─► CDN (CloudFront/Spaces CDN)

Monitoring Stack
   ├─► Sentry (Error tracking)
   ├─► Prometheus (Metrics)
   ├─► Grafana (Dashboards)
   └─► Loki (Logs)
```

---

**Autoria:**
- **Diagrama UML:** @architect (Aria) — Visão holística de domínio
- **Requisitos Funcionais:** @analyst (Atlas) — Análise metódica de features
- **Requisitos Não-Funcionais + Stack:** @po (Pax) — Qualidade e viabilidade técnica

---

*Documentação gerada pelo Synkra AIOS Framework v4.31.0*
