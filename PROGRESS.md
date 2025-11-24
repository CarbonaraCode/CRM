# Progress Log

## 2025-11-24
- Added Django REST Framework layer for the sales domain (clients, contacts, opportunities, offers with items, sale orders, invoices, contracts).
- Offers now accept inline items and automatically recalculate total_amount on create/update; orders and invoices default total_amount from linked offer/order when omitted.
- Wired DRF router in `backend/sales/urls.py` exposing `/api/sales/` endpoints for all sales resources.
- Next steps: run `python manage.py makemigrations && python manage.py migrate`, create an admin/user, and add authentication/permission rules plus API tests.
- Installed Python 3.12 via winget, recreated virtualenv, installed backend requirements, generated initial migrations for `core` and `sales`, and applied them to SQLite.
- Verified backend configuration loads (`python manage.py check` + `django.setup()` smoke test) and frontend builds cleanly via `npm run build`.
- Reinstalled frontend dependencies inside WSL (Linux) to fix Rollup native module resolution, `npm run build` now succeeds.
- Wired frontend "Vendite" pages to backend sales API: added `src/services/api.js`, replaced mock data with live fetch for clients/contacts/opportunities/offers/orders/invoices/contracts, and added UI badges/currency formatting with loading/error banners.
- Hardened `manage.sh` with `set -euo pipefail` and a guard for the venv path.
- Seeded sample sales data (clients, contact, opportunity, offer with items, order, invoice, contract) via Django shell to make UI tables non-empty.
- Added auto-number generation helpers in sales serializers for opportunities (`OPP-YYYY-XXX`), offers (`OFF-YYYY-XXX`), and invoices (`INV-YYYY-XXX`) with zero-padded sequences; made number fields nullable to allow backend auto-fill.
- Updated frontend "Nuovo" actions to rely on backend-generated numbers (no user prompt) for offers/invoices/opportunities; orders still prompt for minimal required fields.
- Enforced relational links in serializers (offer requires opportunity, order requires offer, invoice requires order) and auto-numbering for sale orders (`ORD-YYYY-XXX`). Linked existing seed order/invoice back to offer/order chain and relaxed model number fields to allow backend generation.
- Improved frontend “Nuovo” flows to choose related records from lists (clients/opportunities/offers/orders) instead of raw IDs, aligning required relationships; build still passes.
- Added backend API tests (`backend/sales/tests.py`) covering auto-numbering, required links (opportunity→offer→order→invoice), and totals propagation.
- Added frontend test setup with Vitest/Testing Library plus tests for DataTable filtering and App data loading/creation; configured vitest with jsdom and jest-dom.
- Updated models/serializers/UI fields: removed probability/expected_value, added inserted_date/close_date to opportunities; added issued/accepted dates, type to offers; added invoicing_date to orders; optional address on clients already present.
- Added backend edit/delete coverage (patch/delete clients, offers, opportunities) and frontend edit/delete actions with API helpers; DataTable now supports edit/delete buttons; tests remain green.
- Backend tests now explicitly clean up created objects in `tearDown` to avoid lingering data if run outside the isolated test DB.
