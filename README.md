# Istiqra | استقراء

**EN** — A bilingual (Arabic RTL / English) data-analytics portfolio. Each project has a data story, an interactive dashboard, and full documentation: the nature of the data, the cleaning steps, and a "Number Book" with the definition, formula and pandas line behind every KPI.

**AR** — موقع أعمال ثنائي اللغة (عربي/إنجليزي) لمشاريع تحليل البيانات. لكل مشروع قصة بيانات، ولوحة تفاعلية، وتوثيق كامل: طبيعة البيانات، خطوات التنظيف، و«دفتر الأرقام» (تعريف كل رقم وصيغته وسطر pandas لإعادة حسابه).

**Live site / الموقع:** https://istiqra.netlify.app

## Projects / المشاريع

| Project | Data source | What it shows |
|---|---|---|
| Olist e-commerce (`olist.html`) | [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle) | Revenue, delivery, reviews, payments, 2017–2018 |
| Customer Personality (`customers.html`) | [Customer Personality Analysis](https://www.kaggle.com/datasets/imakash3011/customer-personality-analysis) (Kaggle) | K-Means segmentation, spend and campaign response |
| Amazon catalog (`amazon.html`) | [Amazon Sales Dataset](https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset) (Kaggle) | Prices, discounts, ratings of 1,351 listings (a catalog, not sales) |

## Tools / الأدوات

Python (pandas, numpy, scikit-learn), vanilla JavaScript with a custom SVG chart kit, Node.js + Express.

## Data & licenses / البيانات والتراخيص

Raw CSV files are **not** stored in this repo. Download them from the Kaggle links above and check each dataset's license there. `public/data/*.json` contains only the cleaned, derived data shown on the site.

ملفات CSV الأصلية غير موجودة هنا؛ حمّلها من روابط Kaggle وراجع رخصة كل مجموعة. الملفات في `public/data` هي النسخ المنظّفة المشتقة فقط.

## Run the site / تشغيل الموقع

```bash
npm install && npm start     # http://localhost:3000
```

The site is fully static: you can also host the `public/` folder anywhere (Netlify, Cloudflare Pages, GitHub Pages). No server is required.

## Reproduce the analysis / إعادة التحليل

Requires Python 3 with `pandas numpy scikit-learn`. Put the raw files in `data_raw/` (git-ignored).

```bash
pip install pandas numpy scikit-learn
# Customers
python analysis/build_customers.py data_raw/marketing_campaign.csv public/data/customers.json
# Amazon
python analysis/build_amazon.py data_raw/amazon.csv public/data/amazon.json
# Olist (analyze.py writes intermediate .pkl/K.json in the working folder)
python analysis/profile.py data_raw/olist public/data/olist_profile.json
python analysis/analyze.py data_raw/olist && python analysis/build_json.py
# Pages
python analysis/gen_pages.py
```

Note: `build_json.py` reads `olist_raw/olist_sellers_dataset.csv` relative to the working directory; run it from a folder that contains `olist_raw/` (a copy of the Olist files).

## Where to edit

- `public/data/portfolio.json` — projects shown on the home page (text AR/EN, links).
- `public/css/style.css` — colors and themes (light/dark).
- `public/js/core.js` — header/footer, theme, language. `charts.js` — chart kit. `proj.js` — shared project engine.
- `server.js` (optional) — serves `/api/*`; the front end falls back to `public/data/*.json` when no server is running.

## Olist definitions

Delivered orders only, Jan 2017–Aug 2018; revenue = item price excluding freight; late = delivered after the estimated date; review = mean per order.
