# Istiqra | استقراء

Run: `npm install && npm start` → http://localhost:3000

## Where to edit
- `public/data/portfolio.json` — projects shown on the home page (text AR/EN, links). Add a project = add an object.
- `public/data/olist.json` — Olist data cubes. `meta.powerbi`: paste your published Power BI embed URL (https://app.powerbi.com/...) to show it under the dashboard.
- `public/css/style.css` — colors/themes (tokens at top, `:root` light, `[data-theme=dark]`).
- `public/js/core.js` — header/footer, theme, language. `charts.js` — chart kit. `olist.js` — story + dashboard.
- `server.js` — serves `/api/portfolio`, `/api/olist`; the front end tries `/api/*` first, then falls back to `public/data/*.json`. Connect a database by replacing `readJson`.

## Olist definitions
Delivered orders only, Jan 2017–Aug 2018; revenue = item price excl. freight; late = delivered after estimated date; review = mean per order.

- `public/data/olist_profile.json` — profile of the raw files (row counts, order funnel, quality checks) shown in the “Nature of the data” section. Regenerate with a script like `work/profile.py` when a new dataset arrives.
- `public/js/olist-docs.js` — data nature, quality table, workflow, and the Number Book (definition + formula + pandas line for every KPI). Edit the `NB` array to add or change a metric.

## Adding a new dataset (the pattern used for Customers and Amazon)
1. Put the cleaning + feature code in `analysis/build_<id>.py`; it writes `public/data/<id>.json` (`cols`, `rows`, `profile`, `ref`).
2. Generate the page with `analysis/gen_pages.py` (copy a block, change the texts and dashboard markup) or copy `customers.html`.
3. Copy `public/js/customers.js` to `public/js/<id>.js` and change: data model, `chapters()`, dashboard panels, `docs()` (facts, quality table, steps, code, number book) and insights.
4. `public/js/proj.js` is the shared engine (docs sections, story, KPI cards, insights). `/api/projects/<id>` serves any `data/<id>.json` automatically.
5. Add a card for it in `public/data/portfolio.json`.

Projects: `olist.html` (e-commerce orders), `customers.html` (customer segmentation and campaign response), `amazon.html` (Amazon India product catalog).
