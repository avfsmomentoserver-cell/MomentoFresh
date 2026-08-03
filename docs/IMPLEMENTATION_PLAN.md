# MomentoFresh Implementation Plan

## Overview

This document outlines the implementation plan for MomentoFresh, a clean and fresh implementation of the Momento Core platform with enhanced features for professional crash game analysis.

## Repository Structure

MomentoFresh/
├── backend/
│   ├── momento/
│   │   ├── __init__.py
│   │   ├── analysis.py          # Core analysis engine
│   │   ├── backtest/            # Backtesting framework
│   │   │   ├── __init__.py
│   │   │   ├── engine.py         # Backtest execution engine
│   │   │   ├── metrics.py        # Performance metrics
│   │   │   ├── signals.py        # Signal detection
│   │   │   └── models.py         # Data models
│   │   ├── config.py            # Configuration management
│   │   ├── db.py                # Database models and operations
│   │   ├── store.py             # Storage layer and data access
│   │   ├── feed.py              # Live feed engine
│   │   ├── watcher.py           # File watcher
│   │   ├── hub.py               # WebSocket event hub
│   │   ├── linguistics.py       # Enhanced semantic vocabulary
│   │   ├── forecast.py          # Forecast engine
│   │   └── features/            # Feature implementations
│   │       ├── __init__.py
│   │       ├── pressure/         # Pressure analysis plugin
│   │       │   ├── __init__.py
│   │       │   ├── calculator.py  # Pressure calculations
│   │       │   ├── models.py      # Data models
│   │       │   └── README.md      # Documentation
│   │       └── equal_baseline/   # Equal baseline conversion
│   │           ├── __init__.py
│   │           ├── converter.py  # Multiplier conversion
│   │           ├── trendlines.py # Trendline analysis
│   │           └── README.md      # Documentation
│   │
│   ├── scripts/
│   │   └── import_v1_data.py    # Legacy data import
│   │
│   ├── data/
│   │   └── inbox/               # File ingestion
│   │
│   ├── requirements.txt
│   └── run_api.py
│
├── web/
│   ├── src/
│   │   ├── components/
│   │   │   ├── charts/
│   │   │   │   ├── EqualBaselineChart.tsx
│   │   │   │   └── PressureGauge.tsx
│   │   │   ├── console/
│   │   │   │   ├── Panel.tsx
│   │   │   │   └── StatTile.tsx
│   │   │   ├── layout/
│   │   │   │   ├── AppLayout.tsx
│   │   │   │   ├── AppShell.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   └── Sidebar.tsx
│   │   │   └── ui/
│   │   │       ├── button.tsx
│   │   │       ├── input.tsx
│   │   │       ├── label.tsx
│   │   │       └── toast.tsx
│   │   ├── lib/
│   │   │   ├── api.ts           # API client
│   │   │   ├── config.ts        # Application config
│   │   │   ├── utils.ts         # Utility functions
│   │   │   └── ws.ts            # WebSocket transport
│   │   ├── state/
│   │   │   └── PlatformProvider.tsx
│   │   ├── pages/
│   │   │   ├── app/
│   │   │   ├── auth/
│   │   │   │   └── Login.tsx
│   │   │   └── dashboard/
│   │   │       ├── BacktestStudio.tsx
│   │   │       ├── CommandCenter.tsx
│   │   │       ├── Ingest.tsx
│   │   │       ├── PressureAnalysis.tsx
│   │   │       └── Settings.tsx
│   │   ├── types/
│   │   └── main.tsx
│   │
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── docs/
│   ├── IMPLEMENTATION_PLAN.md
│   ├── BACKTEST_GUIDE.md
│   ├── PRESSURE_PLUGIN.md
│   └── EQUAL_BASELINE.md
│
├── .github/
    └── workflows/
        └── ci.yml

## Implementation Phases

### Phase 1: Core Infrastructure (COMPLETED)
- [x] Repository structure
- [x] Backend package structure
- [x] Configuration management
- [x] Database models (SQLAlchemy)
- [x] Storage layer
- [x] Analysis engine
- [x] Forecast engine

### Phase 2: Feature Implementation (COMPLETED)
- [x] Pressure Plugin
  - [x] Multi-ceiling tracking
  - [x] Gap energy verification
  - [x] Arch/egg pattern detection
  - [x] Imminence prediction
  - [x] Overflow gauge
- [x] Equal Baseline Chart
  - [x] Symmetric conversion
  - [x] Continuous trendlines
  - [x] Band classification
- [x] Enhanced Linguistics
  - [x] 8-layer vocabulary
  - [x] Band classifications
  - [x] State classifications

### Phase 3: Backtest Framework (COMPLETED)
- [x] Backtest engine
- [x] Test phase management
- [x] Signal detection (10 types)
- [x] Metric calculation (11 metrics)
- [x] Parallel execution

### Phase 4: API Layer (COMPLETED)
- [x] FastAPI application
- [x] Route modules
- [x] Authentication
- [x] WebSocket support

### Phase 5: Real-time Infrastructure (COMPLETED)
- [x] Live feed engine
- [x] File watcher
- [x] WebSocket hub

### Phase 6: Frontend (PENDING)
- [ ] React/TypeScript setup
- [ ] TailwindCSS configuration
- [ ] Component library
- [ ] Dashboard pages
- [ ] Chart components

### Phase 7: Documentation (IN PROGRESS)
- [x] README.md
- [x] EQUAL_BASELINE.md
- [ ] IMPLEMENTATION_PLAN.md
- [ ] BACKTEST_GUIDE.md
- [ ] PRESSURE_PLUGIN.md

## Core Principles

1. **Observation Before Prediction** - Understand the present before reasoning about the future
2. **Immutable Raw Events** - Raw data is never edited; corrections recorded separately
3. **Explainability Is Mandatory** - Every prediction carries explanation metadata
4. **Honest Accuracy** - Forecasts scored only against projections recorded *before* round landed
5. **Local vs Production Independence** - SQLite/local dev must always work

## Technology Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, SQLite (WAL mode)
- **Frontend**: Vite + React 18 + TypeScript, shadcn/ui, TailwindCSS
- **Real-time**: Custom WebSocket hub
- **Testing**: pytest, React Testing Library

## Next Steps

1. Complete frontend implementation
2. Add remaining documentation
3. Write unit tests
4. Performance optimization
5. Security review
6. Deployment configuration