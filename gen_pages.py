import re, sys, html
root = "/home/claude/istiqra/public/"
s = open(root + "olist.html", encoding="utf8").read()
def cut(a, b, text=s): i = text.index(a); j = text.index(b, i); return i, j
def A(ar, en, tag=""): return f'ar="{html.escape(ar)}" en="{html.escape(en)}"'
dash_start = s.index("<!-- ================= Dashboard"); dash_end = s.index("<!-- ================= Number book")
base = s
# drop #data section (Olist schema) 
i, j = cut("<!-- ================= The data", "<!-- ================= Nature of the data", base); base = base[:i] + base[j:]
# nature section: rename eyebrow/heading is generic already. Remove old olist-docs reference & set scripts
base = base.replace('<script src="js/olist.js"></script>\n<script src="js/olist-docs.js"></script>', '<script src="js/proj.js"></script>\n<script src="js/@ID@.js"></script>')
# remove olist-only method/limits copy header text stays generic
def page(pid, title_ar, title_en, h1_ar, h1_en, lead_ar, lead_en, chips, dash, intro_cta_ar="افتح الداشبورد ↓", live_ar="مشروع تحليل بيانات · داشبورد تفاعلي", live_en="Data analysis project · interactive dashboard"):
    p = base
    p = re.sub(r"<title>.*?</title>", f"<title>{title_ar} · استقراء</title>", p)
    p = re.sub(r'data-title-ar="[^"]*" data-title-en="[^"]*"', f'data-title-ar="{title_ar} · استقراء" data-title-en="{title_en} · Istiqra"', p)
    i, j = cut('<div class="live">', '<div class="chips', p)
    intro = f'<div class="live"><i></i><span {A(live_ar, live_en)}></span></div>\n      <h1 class="h1s" data-split data-now {A(h1_ar, h1_en)}></h1>\n      <p class="lead rv" data-d="300" {A(lead_ar, lead_en)}></p>\n      '
    p = p[:i] + intro + p[j:]
    p = re.sub(r'<div class="chips rv" data-d="450">.*?</div>', '<div class="chips rv" data-d="450">' + "".join(f"<span>{c}</span>" for c in chips) + "</div>", p, count=1, flags=re.S)
    i = p.index("<!-- ================= Dashboard"); j = p.index("<!-- ================= Number book")
    p = p[:i] + dash + "\n" + p[j:]
    p = p.replace("@ID@", pid)
    return p
def panel(ar, en, body, extra="", how=None):
    h = f'<details class="how"><summary ar="كيف يُحسب هذا الرسم؟" en="How is this chart built?"></summary><p {A(*how)}></p></details>' if how else ""
    return f'<div class="panel"><div class="ph2"><h4 {A(ar, en)}></h4>{extra}</div>{body}{h}</div>'

# ---------- customers ----------
cd = f'''<!-- ================= Dashboard ================= -->
<section id="dashboard" class="dash-sec"><div class="w">
  <div class="hd rv"><div><div class="eb" ar="الداشبورد" en="THE DASHBOARD"></div><h2 ar="اسأل العملاء بنفسك." en="Ask the customers yourself."></h2></div><p ar="كل رسم يتحدّث مع الفلاتر. اختر شريحة أو دخلًا أو حالة عائلية وشاهد كل شيء يتغيّر." en="Every chart follows the filters. Pick a segment, an income band or a family status and watch everything change."></p></div>
  <div class="ds rv" id="ds">
    <div class="dh"><div><h3 ar="لوحة العملاء" en="Customer board"></h3><small id="dsScope"></small></div>
      <div class="fbar" id="fbar"><label class="sel" id="fSeg"></label><label class="sel" id="fInc"></label><label class="sel" id="fMar"></label><label class="sel" id="fKids"></label><label class="sel" id="fEdu"></label><button class="rst" id="fReset" type="button" ar="إعادة ضبط" en="Reset"></button></div></div>
    <div class="kp6" id="kpis"></div>
    <div class="row r1">
      {panel("الشرائح الأربع", "The four segments", '<div class="segs" id="cSegs"></div>', how=("قسّمنا العملاء بخوارزمية K-Means على ثمانية مؤشرات: الدخل، الإنفاق، قنوات الشراء، زيارات الموقع، الصفقات، وعدد الأطفال. الاسم نضعه نحن بعد قراءة خصائص كل شريحة. اضغط على شريحة لتصفية اللوحة.", "We grouped customers with K-Means on eight signals: income, spend, purchase channels, web visits, deals and number of children. We name each segment after reading its profile. Click a segment to filter the board."))}
      {panel("الإنفاق حسب نوع المنتج", "Spend by product type", '<div id="cCats"></div>', how=("نجمع إنفاق العملاء المختارين خلال آخر سنتين في كل فئة، ونعرض حصة كل فئة من الإجمالي.", "We sum the selected customers' spend over the last two years per category and show each category's share of the total."))}
    </div>
    <div class="row r2">
      {panel("الإنفاق والاستجابة حسب الدخل", "Spend and response by income", '<div id="cInc" class="chart"></div>', '<div class="tabs sm" id="iTabs"></div>', how=("نقسّم العملاء المختارين إلى أربع فئات دخل متساوية العدد (حدود الفئات تُحسب على كل العملاء). ثم نحسب متوسط الإنفاق أو نسبة قبول الحملة الأخيرة.", "We split customers into four equal-sized income bands (cut-offs computed on all customers), then show average spend or the last-campaign acceptance rate."))}
      {panel("من يستجيب للحملة؟", "Who responds to the campaign?", '<div id="cResp" class="chart"></div>', '<div class="tabs sm" id="rTabs"></div>', how=("نسبة قبول الحملة الأخيرة (Response) حسب عدد الحملات السابقة المقبولة، أو حسب عدد الأيام منذ آخر شراء.", "Acceptance rate of the last campaign (Response) by number of earlier campaigns accepted, or by days since last purchase."))}
    </div>
    <div class="row r3">
      {panel("قنوات الشراء", "Purchase channels", '<div id="cChan"></div><div class="inst" id="cVis"></div>', how=("عدد عمليات الشراء في كل قناة (متجر، موقع، كتالوج). عمليات الصفقات (Deals) تُحسب ضمن القنوات ولا تُعدّ قناة مستقلة.", "Number of purchases per channel (store, web, catalog). Deal purchases happen inside these channels and are not a channel of their own."))}
      {panel("قبول كل حملة", "Acceptance by campaign", '<div id="cCmp" class="chart"></div>', how=("نسبة العملاء الذين قبلوا كل حملة من الحملات الخمس السابقة والحملة الأخيرة. لا تتوفر تواريخ الحملات ولا نوع العرض.", "Share of customers who accepted each of the five earlier campaigns and the last one. Campaign dates and offer types are not in the data."))}
    </div>
    <div class="row r4">{panel("ملف العميل: العمر والتعليم والعائلة", "Customer profile: age, education, family", '<div class="prof" id="cProf"></div>', how=("متوسط إنفاق العملاء في كل مجموعة، مع عدد العملاء بين قوسين. المجموعات الصغيرة (أقل من 30 عميلًا) تُعرض بشفافية أقل.", "Average spend of customers in each group, with the customer count in brackets. Small groups (under 30 customers) are shown faded."))}</div>
    <details class="tv"><summary ar="عرض البيانات كجدول" en="View data as a table"></summary><div class="tw" id="tableView"></div></details>
    <div class="src" ar="المصدر: Customer Personality Analysis (Kaggle) · 2,212 عميلًا بعد التنظيف · الإنفاق خلال آخر سنتين · الاستجابة = قبول الحملة الأخيرة · العملة غير مذكورة في الملف" en="Source: Customer Personality Analysis (Kaggle) · 2,212 customers after cleaning · spend over the last two years · response = accepted the last campaign · currency is not stated in the file"></div>
  </div>
</div></section>
'''
c = page("customers", "العملاء", "Customers", "من يشتري، وماذا يشتري، ومن يستجيب للحملة؟", "Who buys, what they buy, and who responds?",
  "تحليل ملف عملاء شركة تجزئة: 2,212 عميلًا بعد التنظيف. من هم أفضل العملاء، وكيف نقسّمهم إلى شرائح، ومن يقبل الحملات التسويقية ومن يتجاهلها؟",
  "Analysis of a retailer's customer file: 2,212 customers after cleaning. Who the best customers are, how to split them into segments, and who accepts or ignores marketing campaigns.",
  ["Python · pandas", "scikit-learn · K-Means", "Segmentation", "Campaign analysis", "SVG dashboard"], cd)
open(root + "customers.html", "w", encoding="utf8").write(c)

# ---------- amazon ----------
ad = f'''<!-- ================= Dashboard ================= -->
<section id="dashboard" class="dash-sec"><div class="w">
  <div class="hd rv"><div><div class="eb" ar="الداشبورد" en="THE DASHBOARD"></div><h2 ar="اسأل الكتالوج بنفسك." en="Ask the catalog yourself."></h2></div><p ar="اختر فئة أو شريحة سعر أو مستوى خصم، وشاهد كيف تتغيّر التقييمات والشعبية." en="Pick a category, price tier or discount level and watch ratings and popularity change."></p></div>
  <div class="ds rv" id="ds">
    <div class="dh"><div><h3 ar="لوحة كتالوج أمازون الهند" en="Amazon India catalog board"></h3><small id="dsScope"></small></div>
      <div class="fbar" id="fbar"><label class="sel" id="fCat"></label><label class="sel" id="fPrice"></label><label class="sel" id="fDisc"></label><label class="sel" id="fRate"></label><button class="rst" id="fReset" type="button" ar="إعادة ضبط" en="Reset"></button></div></div>
    <div class="kp6" id="kpis"></div>
    <div class="row r1">
      {panel("هل الخصم الأكبر يعني تقييمًا أعلى؟", "Does a bigger discount mean a higher rating?", '<div id="cDR" class="chart"></div><small class="un" id="drNote"></small>', how=("نقسّم المنتجات حسب نسبة الخصم، ثم نحسب متوسط التقييم لكل شريحة. المحور يبدأ من 3.5 ليظهر الفرق الصغير، وهذا واضح في التسمية. الارتباط ضعيف ولا يثبت سببًا.", "Products are grouped by discount level and we average the rating of each group. The axis starts at 3.5 so the small gap is visible, and it is labelled. The relationship is weak and proves no cause."))}
      {panel("الفئات", "Categories", '<div id="cCats"></div>', '<div class="tabs sm" id="cTabs"></div>', how=("الفئة الفرعية الثانية من مسار التصنيف في أمازون. نعرض أكبر الفئات فقط، والباقي في «أخرى».", "The second level of Amazon's category path. Only the biggest categories are listed; the rest are grouped as “Other”."))}
    </div>
    <div class="row r2">
      {panel("الشعبية حسب السعر", "Popularity by price tier", '<div id="cPP" class="chart"></div>', how=("الشعبية = عدد التقييمات (rating_count) وليس المبيعات. نعرض الوسيط لأن عدد قليل من المنتجات يملك مئات الآلاف من التقييمات ويشوّه المتوسط.", "Popularity = rating count, not sales. We show the median because a few products with hundreds of thousands of ratings would distort the mean."))}
      {panel("الشعبية حسب الخصم", "Popularity by discount level", '<div id="cPD" class="chart"></div>', how=("وسيط عدد التقييمات لكل شريحة خصم. المنتجات بلا تقييمات مُحتسبة مُستبعدة من هذا الرسم.", "Median rating count per discount level. Products with no rating count are left out of this chart."))}
    </div>
    <div class="row r3">
      {panel("توزيع التقييمات", "Rating distribution", '<div id="cRD" class="chart"></div>', how=("عدد المنتجات في كل مستوى تقييم بخطوة 0.2. تتركّز التقييمات بين 3.8 و4.5 تقريبًا.", "Number of products per rating level in 0.2 steps. Ratings cluster between roughly 3.8 and 4.5."))}
      {panel("توزيع الأسعار", "Price distribution", '<div id="cPR" class="chart"></div>', how=("عدد المنتجات في كل شريحة سعرية بعد الخصم، بالروبية الهندية.", "Number of products per price tier after discount, in Indian rupees."))}
    </div>
    <div class="row r4">{panel("أكثر المنتجات تقييمًا (عددًا)", "Most-rated products", '<div class="tw tall" id="cTop"></div>', how=("نرتّب المنتجات المختارة حسب عدد التقييمات. هذا مؤشر شعبية وليس مبيعات، والنسخ المختلفة من المنتج نفسه تتكرر بالعدد نفسه.", "Selected products ranked by rating count. A popularity signal, not sales; variants of one product repeat the same count."))}</div>
    <details class="tv"><summary ar="عرض البيانات كجدول" en="View data as a table"></summary><div class="tw" id="tableView"></div></details>
    <div class="src" ar="المصدر: Amazon Sales Dataset (Kaggle) · كتالوج منتجات أمازون الهند · لقطة بلا تواريخ · الأسعار بالروبية الهندية" en="Source: Amazon Sales Dataset (Kaggle) · Amazon India product catalog · a snapshot with no dates · prices in Indian rupees"></div>
  </div>
</div></section>
'''
a = page("amazon", "كتالوج أمازون", "Amazon catalog", "هل الخصم الكبير يعني منتجًا أفضل؟", "Does a big discount mean a better product?",
  "تحليل كتالوج أمازون الهند: 1,351 منتجًا بعد إزالة التكرار، أسعارها وخصوماتها وتقييماتها. الملف اسمه «مبيعات» لكنه كتالوج: بلا طلبات ولا تواريخ، لذلك نقيس الشعبية بعدد التقييمات وليس بالمبيعات.",
  "Analysis of the Amazon India catalog: 1,351 products after removing duplicates, with prices, discounts and ratings. The file is named “sales” but it is a catalog: no orders, no dates, so popularity is measured by rating count, not sales.",
  ["Python · pandas", "Pricing analysis", "Ratings", "Data caveats", "SVG dashboard"], ad)
open(root + "amazon.html", "w", encoding="utf8").write(a)
print("ok")
