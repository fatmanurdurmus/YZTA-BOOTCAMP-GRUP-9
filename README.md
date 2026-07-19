<p align="center">
  <img src="docs/assets/banner.png" alt="CarbonPilot AI" width="600"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-1F7A54?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-backend-1F7A54?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React%20%2B%20Vite-frontend-1F7A54?style=flat-square&logo=react&logoColor=white" alt="React"/>
  <img src="https://img.shields.io/badge/LangGraph-agent%20orchestration-1F7A54?style=flat-square" alt="LangGraph"/>
  <img src="https://img.shields.io/badge/tests-passing-1F7A54?style=flat-square" alt="Tests"/>
</p>

<h1 align="center">CarbonPilot AI</h1>
<p align="center"><i>CBAM/SKDM uyumluluğu için yapay zeka destekli karbon muhasebesi platformu</i></p>

<p align="center">
  <a href="#-türkçe">🇹🇷 Türkçe</a> •
  <a href="#-english">🇬🇧 English</a>
</p>

---

# 🇹🇷 Türkçe

## 📋 İçindekiler

- [Takım](#takım-ismi)
- [Ürün Bilgileri](#ürün-ile-ilgili-bilgiler)
- [Teknoloji Yığını](#tech-stack)
- [Repo Yapısı](#repository-structure)
- [Kurulum](#kurulum)
- [Sprint 1](#sprint-1-19-haziran--5-temmuz)
- [Sprint 2](#sprint-2-6-temmuz--19-temmuz)

---

## Takım İsmi
Grup 9 – CarbonPilot AI

### 👔 Proje Ekibi & Roller

| İsim | Rol | Bağlantılar |
| :--- | :--- | :---: |
| **Fatma Nur Durmuş** | Scrum Master | [🌐 LinkedIn](https://www.linkedin.com/in/fatmanurdurmus/) \| [🐙 GitHub](https://github.com/fatmanurdurmus) |
| **Senem Selim** | Product Owner | [🌐 LinkedIn](https://www.linkedin.com/in/senemselim/) \| [🐙 GitHub](https://github.com/senemselim) |
| **Yaren Yurdakul** | Developer | [🌐 LinkedIn](https://www.linkedin.com/in/yaren-yurdakul-452096295/) \| [🐙 GitHub](https://github.com/yarenyurdakul) |
| **Onur Ergüden** | Developer | [🌐 LinkedIn](https://www.linkedin.com/in/onurerguden/?locale=tr) \| [🐙 GitHub](https://github.com/onurerguden) |
| **Tahsin Yazıcı** | Developer | [🌐 LinkedIn](https://www.linkedin.com/in/yazctahsin/) \| [🐙 GitHub](https://github.com/yazctahsin) |

## Ürün İle İlgili Bilgiler

### Ürün İsmi
CarbonPilot AI

### Ürün Açıklaması
CarbonPilot AI, demir-çelik başta olmak üzere ağır sanayi ihracatçılarının Avrupa Birliği Sınırda Karbon Düzenleme Mekanizması (SKDM/CBAM) yükümlülüklerini yönetebilmesi için geliştirilen, yapay zeka destekli bir karbon muhasebesi ve karar destek platformudur. Sistem; ERP logları, faturalar ve sevkiyat belgelerinden faaliyet verisini ayrıştırır, Kapsam 1/2/3 emisyonlarını deterministik Python koduyla hesaplar, ilgili mevzuat referanslarını (Law-RAG) getirir, sonuçları bir Critic Agent ile denetler ve denetlenebilir raporlar üretir.

### Ürün Özellikleri
- 🔒 Pydantic ile tip-güvenli veri şemaları (strict JSON)
- 📊 Deterministik Scope 1, Scope 2 ve CBAM-odaklı Scope 3 hesaplama motoru
- 🤖 LangGraph tabanlı agent orkestrasyonu (loop limit, timeout ve fallback guardrail'leri ile)
- 📚 Law-RAG mevzuat referans katmanı (Gemini embedding + pgvector semantik arama)
- 🧠 Epizodik bellek: agent geçmiş çalıştırmaları tesis bazında hatırlar
- 🗄️ PostgreSQL + LangGraph PostgresSaver ile kalıcı durum ve checkpointing
- 🌱 Yeşil dönüşüm optimizasyon motoru ve simülasyon sürgüleri
- ✅ Critic Agent ile halüsinasyon/tutarlılık denetimi
- 📱 React + Tailwind ile mobil öncelikli karbon risk paneli


### İş Model Kanvası

<p align="center">
  <img src="docs/assets/BM-9.png" alt="İş Model Kanvası" width="100%">
</p>


### Hedef Kitle
- Demir-çelik ve ağır sanayi ihracatçıları
- Çevre mühendisleri ve sürdürülebilirlik direktörleri
- Kurumsal denetçiler ve gümrük/uyum ekipleri

### Product Backlog URL
[Jira – CarbonPilot Board](https://onurerguden.atlassian.net/jira/software/projects/CP/boards/1/backlog?atlOrigin=eyJpIjoiMjY4MzRlZGUyN2ViNDNmMDhiZTJlMDI1ODFiYWNiMDMiLCJwIjoiaiJ9)

---

## Tech Stack

| Katman | Teknoloji |
|---|---|
| Backend | Python, FastAPI, Pydantic v2, SQLAlchemy/Alembic-ready |
| Agent Orchestration | LangGraph StateGraph (guarded loops, checkpoint-ready) |
| Database | PostgreSQL + pgvector |
| Frontend | React, Vite, TypeScript, Tailwind CSS, Recharts |
| Tests | pytest (backend), Vitest/Playwright-ready (frontend) |
| Observability | LangSmith-first configuration |

## Repository Structure

```text
apps/
  backend/        FastAPI, schemas, deterministic calculation engine, agent graph
  frontend/       React + Vite dashboard
docs/             Product, architecture, roadmap, Jira workflow, methodology
infra/            Docker Compose and database bootstrap assets
packages/         Shared schema notes for future generated contracts
ProjectManagement Bootcamp sprint artifacts
```

## Kurulum

### 1. Repoyu klonla
```bash
git clone https://github.com/fatmanurdurmus/YZTA-BOOTCAMP-GRUP-9.git
cd YZTA-BOOTCAMP-GRUP-9
```

### 2. Backend'i çalıştır
```bash
cd apps/backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m pytest                 # testlerin geçtiğini doğrula
uvicorn carbonpilot.main:app --reload
```
API varsayılan olarak `http://localhost:8000` adresinde çalışır.

### 3. Frontend'i çalıştır
```bash
cd apps/frontend
npm install
npm run dev
```
Dashboard varsayılan olarak `http://localhost:5173` adresinde açılır.

## Safety Rules

- Do not push, force push, merge PRs, deploy, delete remote resources, or mark Jira issues Done without explicit approval.
- Emission calculations are deterministic Python code, never free-form LLM reasoning.
- LLM outputs must be schema-validated before entering the database, calculation engine, or reporting pipeline.

---

# Sprint 1 (19 Haziran – 5 Temmuz)

**Sprint Hedefi:** Monorepo, backend/frontend iskeletleri, tip-güvenli şemalar, Scope 1/2/CBAM-odaklı Scope 3 hesaplama motoru, Law-RAG stub'ı, LangGraph iskeleti, guardrail'ler ve pytest test yapısının kurulması.

- **Backlog düzeni ve Story seçimleri:** Sprint 1 kapsamı, projenin en yüksek riskli ve test edilmesi gereken çekirdek modüllerini (veri şeması, hesaplama motoru, agent orkestrasyonu) içerecek şekilde front-loading mantığıyla seçilmiştir (CP-14 – CP-22). Ayrıca ekibin iş modeli/pazar analizi çalışmaları (CP-23 – CP-28) aynı sprint içinde tamamlanmıştır.

- **Daily Scrum:** Daily Scrum toplantıları Slack ve WhatsApp üzerinden yürütülmüştür. Notlar: [Sprint 1 Daily Scrum Notları](https://github.com/fatmanurdurmus/YZTA-BOOTCAMP-GRUP-9/blob/main/ProjectManagement/Sprint1Documents/DailyScrumMeetingNotesSprint1.docx?raw=true)

- **Sprint board update:**

  <p align="center">
    <img src="ProjectManagement/Sprint1Documents/backlog1.png" width="90%" alt="Sprint 1 board 1"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint1Documents/backlog2.png" width="90%" alt="Sprint 1 board 2"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint1Documents/backlog3.png" width="90%" alt="Sprint 1 board 3"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint1Documents/backlog4.png" width="90%" alt="Sprint 1 board 4"/>
  </p>

- **Ürün Durumu:**

  <p align="center">
    <img src="ProjectManagement/Sprint1Documents/backend.png" width="90%" alt="Backend test/çalışma çıktısı"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint1Documents/dashboard.png" width="90%" alt="CarbonPilot dashboard"/>
  </p>

- **Sprint Review:** Sprint 1 kapsamındaki 15 backlog kalemi (CP-14 – CP-28) tamamlanmıştır. Hesaplama motoru ve agent orkestrasyon iskeleti pytest ile doğrulanmıştır (9 test, tamamı geçiyor). Loop limit, timeout ve fallback guardrail'leri (CP-20) ve ek edge-case testleri (CP-21) sprint sonunda tamamlanarak eklenmiştir. Sprint Review katılımcıları: Tahsin, Onur, Fatma Nur, Senem, Yaren.

- **Sprint Retrospective:**
  - Jira board güncellemesinin kod ilerlemesinin gerisinde kaldığı fark edildi; bundan sonra her PR sonrası ilgili ticket anında güncellenecek.
  - Görev atamaları netleştirildi.
  - Test kapsamı (zero/invalid/edge-case) sprint ortasında değil, ticket açılırken tanımlanmalı.

---

# Sprint 2 (6 Temmuz – 19 Temmuz)

**Sprint Hedefi:** PostgreSQL kalıcılığı, SQLAlchemy/Alembic migration altyapısı, LangGraph PostgresSaver checkpointing, semantik (Gemini + pgvector) ve epizodik bellek katmanları, yeşil dönüşüm optimizasyon motoru ve simülasyon sürgü backend'inin kurulması; Sprint 1'in bozulmadığının regresyon testleriyle kanıtlanması.

- **Backlog düzeni ve Story seçimleri:** Sprint 2 kapsamı (CP-29 – CP-39), bootcamp planlama dokümanındaki "Durum Yönetimi, Çok Katmanlı Bellek ve Simülasyon Motoru" hedefiyle birebir örtüşecek şekilde seçildi: veritabanı şeması ve ORM (CP-29, CP-31), hesaplama motorunun gerçek kalıcılığa bağlanması (CP-32), agent checkpointing ve state recovery (CP-33, CP-34), semantik ve epizodik bellek (CP-35, CP-36), optimizasyon ve simülasyon (CP-37, CP-38), ve son olarak Sprint 1'i doğrulayan regresyon test paketi (CP-39).

- **Daily Scrum:** Daily Scrum toplantıları Slack ve WhatsApp üzerinden yürütülmüştür. Notlar: [Sprint 2 Daily Scrum Notları](https://github.com/fatmanurdurmus/YZTA-BOOTCAMP-GRUP-9/blob/main/ProjectManagement/Sprint2Documents/DailyScrumMeetingNotesSprint2.docx?raw=true)

- **Sprint board update:**

  <p align="center">
    <img src="ProjectManagement/Sprint2Documents/board1.png" width="90%" alt="Sprint 2 board 1"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint2Documents/board2.png" width="90%" alt="Sprint 2 board 2"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint2Documents/summary.png" width="90%" alt="Sprint 2 özet"/>
  </p>

- **Ürün Durumu:**

  <p align="center">
    <img src="ProjectManagement/Sprint2Documents/backend1.png" width="90%" alt="Backend test çıktısı"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint2Documents/backend2.png" width="90%" alt="API endpoint listesi (Swagger)"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint2Documents/backend3.png" width="90%" alt="API şemaları (Swagger)"/>
  </p>

- **Sprint Review:** Sprint 2 kapsamındaki 11 backlog kalemi (CP-29 – CP-39) tamamlandı. PostgreSQL şeması, SQLAlchemy modelleri ve Alembic migration'ları kuruldu; LangGraph self-correction döngüsüne gerçek PostgresSaver checkpointing eklendi ve state recovery testiyle doğrulandı; Law-RAG semantik bellek katmanı gerçek Gemini embedding'leriyle çalışır hale getirildi; epizodik bellek katmanı agent'ın geçmiş çalıştırmaları hatırlamasını sağladı; yeşil dönüşüm optimizasyon motoru ve simülasyon sürgü backend'i tamamlandı; 3 yeni regresyon testiyle Sprint 1'in bozulmadığı kanıtlandı (toplam 51 test, tamamı geçiyor). Sprint Review katılımcıları: Fatma Nur, Onur, Yaren, Senem, Tahsin.

- **Sprint Retrospective:**
  - LangGraph'ın conditional-edge fonksiyonlarında state mutasyonunun kalıcı olmadığı (sadece node'larda kalıcı olduğu) sancılı ama değerli bir öğrenme oldu.
  - Checkpointer serileştirme (msgpack → pickle fallback) ve embedding boyut uyumsuzlukları (1536 vs 768) gibi kütüphane detaylarına daha erken bakılması gerektiği görüldü.
  - DB gerektiren testlerin "sessizce geç" yerine "yüksek sesle hata ver" prensibiyle yazılması, gerçek altyapı sorunlarını erken yakalamamızı sağladı.

---

# Sprint 3

---

# 🇬🇧 English

## 📋 Table of Contents

- [Team](#team-name)
- [Product Info](#about-the-product)
- [Tech Stack](#tech-stack-1)
- [Repository Structure](#repository-structure-1)
- [Setup](#setup)
- [Sprint 1](#sprint-1-june-19--july-5)
- [Sprint 2](#sprint-2-july-6--july-19)

---

## Team Name
Group 9 – CarbonPilot AI

### 👔 Project Team & Roles

| Name | Role | Links |
| :--- | :--- | :---: |
| **Fatma Nur Durmuş** | Scrum Master | [🌐 LinkedIn](https://www.linkedin.com/in/fatmanurdurmus/) \| [🐙 GitHub](https://github.com/fatmanurdurmus) |
| **Senem Selim** | Product Owner | [🌐 LinkedIn](https://www.linkedin.com/in/senemselim/) \| [🐙 GitHub](https://github.com/senemselim) |
| **Yaren Yurdakul** | Developer | [🌐 LinkedIn](https://www.linkedin.com/in/yaren-yurdakul-452096295/) \| [🐙 GitHub](https://github.com/yarenyurdakul) |
| **Onur Ergüden** | Developer | [🌐 LinkedIn](https://www.linkedin.com/in/onurerguden/?locale=tr) \| [🐙 GitHub](https://github.com/onurerguden) |
| **Tahsin Yazıcı** | Developer | [🌐 LinkedIn](https://www.linkedin.com/in/yazctahsin/) \| [🐙 GitHub](https://github.com/yazctahsin) |

## About the Product

### Product Name
CarbonPilot AI

### Product Description
CarbonPilot AI is an AI-assisted carbon accounting and decision-support platform built for heavy industry exporters — primarily iron and steel producers — to manage their obligations under the EU Carbon Border Adjustment Mechanism (CBAM). The system ingests activity data from ERP logs, invoices, and shipment documents; calculates Scope 1/2/3 emissions with deterministic Python code; retrieves relevant legal references (Law-RAG); audits the output with a Critic Agent; and produces audit-ready reports.

### Product Features
- 🔒 Type-safe data schemas with Pydantic (strict JSON)
- 📊 Deterministic Scope 1, Scope 2, and CBAM-focused Scope 3 calculation engine
- 🤖 LangGraph-based agent orchestration (with loop limit, timeout, and fallback guardrails)
- 📚 Law-RAG legal reference layer (Gemini embeddings + pgvector semantic search)
- 🧠 Episodic memory: the agent recalls past runs per facility
- 🗄️ PostgreSQL + LangGraph PostgresSaver for durable state and checkpointing
- 🌱 Green-transition optimization engine and simulation sliders
- ✅ Critic Agent for hallucination/consistency auditing
- 📱 Mobile-first carbon risk dashboard built with React + Tailwind

### Target Audience
- Iron, steel, and heavy industry exporters
- Environmental engineers and sustainability directors
- Corporate auditors and customs/compliance teams

### Product Backlog URL
[Jira – CarbonPilot Board](https://onurerguden.atlassian.net/jira/software/projects/CP/boards/1/backlog?atlOrigin=eyJpIjoiMjY4MzRlZGUyN2ViNDNmMDhiZTJlMDI1ODFiYWNiMDMiLCJwIjoiaiJ9)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Pydantic v2, SQLAlchemy/Alembic-ready |
| Agent Orchestration | LangGraph StateGraph (guarded loops, checkpoint-ready) |
| Database | PostgreSQL + pgvector |
| Frontend | React, Vite, TypeScript, Tailwind CSS, Recharts |
| Tests | pytest (backend), Vitest/Playwright-ready (frontend) |
| Observability | LangSmith-first configuration |

## Repository Structure

```text
apps/
  backend/        FastAPI, schemas, deterministic calculation engine, agent graph
  frontend/       React + Vite dashboard
docs/             Product, architecture, roadmap, Jira workflow, methodology
infra/            Docker Compose and database bootstrap assets
packages/         Shared schema notes for future generated contracts
ProjectManagement Bootcamp sprint artifacts
```

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/fatmanurdurmus/YZTA-BOOTCAMP-GRUP-9.git
cd YZTA-BOOTCAMP-GRUP-9
```

### 2. Run the backend
```bash
cd apps/backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m pytest                 # verify all tests pass
uvicorn carbonpilot.main:app --reload
```
The API runs at `http://localhost:8000` by default.

### 3. Run the frontend
```bash
cd apps/frontend
npm install
npm run dev
```
The dashboard opens at `http://localhost:5173` by default.

## Safety Rules

- Do not push, force push, merge PRs, deploy, delete remote resources, or mark Jira issues Done without explicit approval.
- Emission calculations are deterministic Python code, never free-form LLM reasoning.
- LLM outputs must be schema-validated before entering the database, calculation engine, or reporting pipeline.

---

# Sprint 1 (June 19 – July 5)

**Sprint Goal:** Establish the monorepo, backend/frontend skeletons, strict schemas, Scope 1/2/CBAM-focused Scope 3 calculation engine, Law-RAG stub, LangGraph skeleton, guardrails, and pytest structure.

- **Backlog structure and story selection:** Sprint 1 scope was chosen using a front-loading approach, prioritizing the project's highest-risk, most test-critical core modules (data schemas, calculation engine, agent orchestration) — CP-14 through CP-22. The team's business model / market analysis work (CP-23 – CP-28) was also completed within the same sprint.

- **Daily Scrum:** Daily Scrum meetings were held via Slack and WhatsApp due to scheduling constraints. Notes: [Sprint 1 Daily Scrum Notes](https://github.com/fatmanurdurmus/YZTA-BOOTCAMP-GRUP-9/blob/main/ProjectManagement/Sprint1Documents/DailyScrumMeetingNotesSprint1.docx?raw=true)

- **Sprint board update:**

  <p align="center">
    <img src="ProjectManagement/Sprint1Documents/backlog1.png" width="90%" alt="Sprint 1 board 1"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint1Documents/backlog2.png" width="90%" alt="Sprint 1 board 2"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint1Documents/backlog3.png" width="90%" alt="Sprint 1 board 3"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint1Documents/backlog4.png" width="90%" alt="Sprint 1 board 4"/>
  </p>

- **Product Status:**

  <p align="center">
    <img src="ProjectManagement/Sprint1Documents/backend.png" width="90%" alt="Backend test/run output"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint1Documents/dashboard.png" width="90%" alt="CarbonPilot dashboard"/>
  </p>

- **Sprint Review:** All 15 backlog items in Sprint 1 (CP-14 – CP-28) were completed. The calculation engine and agent orchestration skeleton were verified with pytest (9 tests, all passing). Loop limit, timeout, and fallback guardrails (CP-20) and additional edge-case tests (CP-21) were completed at the end of the sprint. Sprint Review attendees: Tahsin, Onur, Fatma Nur, Senem, Yaren.

- **Sprint Retrospective:**
  - We noticed the Jira board had fallen behind actual code progress; from now on, each ticket will be updated immediately after the related PR.
  - Task assignments were clarified.
  - Test coverage (zero/invalid/edge-case) should be defined when a ticket is opened, not mid-sprint.

---

# Sprint 2 (July 6 – July 19)

**Sprint Goal:** Establish PostgreSQL persistence, the SQLAlchemy/Alembic migration pipeline, LangGraph PostgresSaver checkpointing, semantic (Gemini + pgvector) and episodic memory layers, the green-transition optimization engine, and the simulation slider backend; prove Sprint 1 remains intact via a dedicated regression suite.

- **Backlog structure and story selection:** Sprint 2 scope (CP-29 – CP-39) mapped directly onto the bootcamp's planned "State Management, Multi-Layer Memory, and Simulation Engine" milestone: database schema and ORM (CP-29, CP-31), wiring the calculation engine to real persistence (CP-32), agent checkpointing and state recovery (CP-33, CP-34), semantic and episodic memory (CP-35, CP-36), optimization and simulation (CP-37, CP-38), and finally a regression suite proving Sprint 1 still holds (CP-39).

- **Daily Scrum:** Daily Scrum meetings were held via Slack and WhatsApp. Notes: [Sprint 2 Daily Scrum Notes](https://github.com/fatmanurdurmus/YZTA-BOOTCAMP-GRUP-9/blob/main/ProjectManagement/Sprint2Documents/DailyScrumMeetingNotesSprint2.docx?raw=true)

- **Sprint board update:**

  <p align="center">
    <img src="ProjectManagement/Sprint2Documents/board1.png" width="90%" alt="Sprint 2 board 1"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint2Documents/board2.png" width="90%" alt="Sprint 2 board 2"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint2Documents/summary.png" width="90%" alt="Sprint 2 summary"/>
  </p>

- **Product Status:**

  <p align="center">
    <img src="ProjectManagement/Sprint2Documents/backend1.png" width="90%" alt="Backend test output"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint2Documents/backend2.png" width="90%" alt="API endpoint list (Swagger)"/>
  </p>
  <p align="center">
    <img src="ProjectManagement/Sprint2Documents/backend3.png" width="90%" alt="API schemas (Swagger)"/>
  </p>

- **Sprint Review:** All 11 backlog items in Sprint 2 (CP-29 – CP-39) were completed. The PostgreSQL schema, SQLAlchemy models, and Alembic migrations were built; real PostgresSaver checkpointing was added to the LangGraph self-correction loop and verified with a state-recovery test; the Law-RAG semantic memory layer was made to work with real Gemini embeddings; the episodic memory layer let the agent recall past runs; the green-transition optimization engine and simulation slider backend were completed; and 3 new regression tests confirmed Sprint 1 remained intact (51 tests total, all passing). Sprint Review attendees: Fatma Nur, Onur, Yaren, Senem, Tahsin.

- **Sprint Retrospective:**
  - Discovering that state mutations inside LangGraph conditional-edge functions don't persist (only node functions do) was a painful but valuable lesson.
  - Library-level details — checkpointer serialization (msgpack → pickle fallback) and embedding dimension mismatches (1536 vs 768) — should be checked earlier next time.
  - Writing DB-dependent tests to "fail loudly" instead of "silently pass" helped catch real infrastructure issues early.

---

# Sprint 3