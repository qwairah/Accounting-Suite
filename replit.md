# Workspace — قـويـره سوفت (QWAIRAH SOFT)

## Overview

Full-stack Arabic RTL accounting system. pnpm workspace monorepo using TypeScript.
Main artifact: `artifacts/qawera-soft` (React+Vite web app)
API server: `artifacts/api-server` (Express 5 + PostgreSQL + Drizzle ORM)

## Features Implemented
- Sales, Purchases, Treasury (Vouchers), Journal, Exchange modules
- Account Ledger (ترحيل): All transactions auto-post to `qawera_ledger_v1` localStorage
  - Sales: post to fund account (debit) when payment account selected
  - Purchases: post to fund account (credit) when payment account selected
  - Treasury: post Dr/Cr to both fund and customer/account
  - Journal: each line posted to its respective account
- Delete permissions per document type: `allowDeleteInvoices/Vouchers/Journals/Exchange` in SettingsContext
- Income statement: shows only صافي الربح OR صافي الخسارة (not both)
- Balance sheet: Assets = Liabilities + Equity enforced using journal-based account balances
- Account statements: full ledger history shown in account detail dialog
- Settings security section: edit + delete permission toggles

## Key Files
- `artifacts/qawera-soft/src/lib/ledger.ts` — account ledger utility (localStorage)
- `artifacts/qawera-soft/src/contexts/SettingsContext.tsx` — app settings including permissions
- `artifacts/qawera-soft/src/pages/` — all page components

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
