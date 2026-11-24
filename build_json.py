import pandas as pd, numpy as np, json
dl = pd.read_pickle("dl.pkl"); items = pd.read_pickle("items.pkl"); pp = pd.read_pickle("pp.pkl")
K = json.load(open("K.json"))
months = sorted(dl.month.unique()); mi = {m:i for i,m in enumerate(months)}
states = list(dl.groupby("customer_state").rev.sum().sort_values(ascending=False).index); si = {s:i for i,s in enumerate(states)}
TOP = ["health_beauty","watches_gifts","bed_bath_table","sports_leisure","computers_accessories","furniture_decor","housewares","cool_stuff","auto","garden_tools","toys","baby","perfumery","telephony"]
cats = TOP + ["other"]; ci = {c:i for i,c in enumerate(cats)}
ptypes = ["credit_card","boleto","voucher","debit_card"]; pi = {p:i for i,p in enumerate(ptypes)}
r = lambda x, n=1: round(float(x), n)

dl["mi"] = dl.month.map(mi); dl["si"] = dl.customer_state.map(si)
dl["dn"] = dl.days.notna().astype(int); dl["ds"] = dl.days.fillna(0)
dl["ln"] = (dl.late & dl.days.notna()).astype(int)
dl["rn"] = dl.review.notna().astype(int); dl["rs"] = dl.review.fillna(0)
A = dl.groupby(["mi","si"]).agg(o=("order_id","count"), rev=("rev","sum"), frt=("frt","sum"), it=("items","sum"),
        ds=("ds","sum"), dn=("dn","sum"), ln=("ln","sum"), rs=("rs","sum"), rn=("rn","sum")).reset_index()
base = {"cols":["m","s","orders","rev","freight","items","daysSum","daysN","lateN","revSum","revN"],
        "rows":[[int(a.mi),int(a.si),int(a.o),r(a.rev),r(a.frt),int(a.it),r(a.ds),int(a.dn),int(a.ln),r(a.rs),int(a.rn)] for a in A.itertuples()]}

items["c"] = items.cat.where(items.cat.isin(TOP), "other").map(ci)
items["mi"] = items.month.map(mi); items["si"] = items.customer_state.map(si)
B = items.groupby(["mi","si","c"]).agg(rev=("price","sum"), n=("price","count")).reset_index()
catc = {"cols":["m","s","c","rev","items"], "rows":[[int(a.mi),int(a.si),int(a.c),r(a.rev),int(a.n)] for a in B.itertuples()]}

pm = pp.merge(dl[["order_id","mi","si"]], on="order_id"); pm = pm[pm.payment_type.isin(ptypes)]
pm["t"] = pm.payment_type.map(pi)
C = pm.groupby(["mi","si","t"]).agg(v=("payment_value","sum"), n=("payment_value","count"), inst=("payment_installments","sum")).reset_index()
payc = {"cols":["m","s","t","value","payments","instSum"], "rows":[[int(a.mi),int(a.si),int(a.t),r(a.v),int(a.n),int(a.inst)] for a in C.itertuples()]}

b = dl.dropna(subset=["bucket"]).copy(); b["b"] = b.bucket.astype(int)
D = b.groupby(["mi","si","b"]).agg(o=("order_id","count"), rs=("rs","sum"), rn=("rn","sum")).reset_index()
delc = {"cols":["m","s","b","orders","revSum","revN"], "rows":[[int(a.mi),int(a.si),int(a.b),int(a.o),r(a.rs),int(a.rn)] for a in D.itertuples()]}

E = dl.groupby(["si","wd","hr"]).size().reset_index(name="n")
heat = {"cols":["s","wd","hr","orders"], "rows":[[int(a.si),int(a.wd),int(a.hr),int(a.n)] for a in E.itertuples()]}

nov = dl[dl.month=="2017-11"].groupby(dl.order_purchase_timestamp.dt.day).size()
dailyAll = dl.groupby(dl.order_purchase_timestamp.dt.date).size()
K["median_day_orders"] = float(dailyAll.median()); K["peak_day"] = "2017-11-24"; K["peak_day_orders"] = int(dailyAll.max())

# same-state vs cross-state freight
sel = items.merge(pd.read_csv("olist_raw/olist_sellers_dataset.csv")[["seller_id","seller_state"]], on="seller_id", how="left")
same = sel.seller_state == sel.customer_state
K["freight_same"] = r(sel[same].freight_value.mean(),2); K["freight_cross"] = r(sel[~same].freight_value.mean(),2)
K["freight_gap_pct"] = r(K["freight_cross"]/K["freight_same"]-1,3)

out = {"meta":{"months":months,"states":states,"cats":cats,"ptypes":ptypes,"window":["2017-01","2018-08"],
  "currency":"BRL","revenue_def":"sum of item price on delivered orders","source":"Olist Brazilian E-Commerce (Kaggle), 2016-2018"},
  "kpis":{k:(r(v,4) if isinstance(v,float) else v) for k,v in K.items()},
  "base":base,"cat":catc,"pay":payc,"del":delc,"heat":heat,
  "bfDaily":{"days":[int(x) for x in nov.index],"orders":[int(x) for x in nov.values]}}
s = json.dumps(out, ensure_ascii=False, separators=(",",":"))
open("out/olist.json","w").write(s); print(len(s)/1024, "KB")
# reconciliation
print("rev check", sum(x[3] for x in base["rows"]), K["revenue"], "| cat", sum(x[3] for x in catc["rows"]), "| orders", sum(x[2] for x in base["rows"]), K["orders"])
print("pay orders rows", sum(x[4] for x in payc["rows"]), " bucket orders", sum(x[3] for x in delc["rows"]), "heat", sum(x[3] for x in heat["rows"]))
print(json.dumps(out["kpis"], indent=0)[:900])
