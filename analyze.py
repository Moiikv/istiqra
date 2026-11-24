import pandas as pd, numpy as np, json, sys
d = sys.argv[1] + "/"
rd = lambda n: pd.read_csv(d + f"olist_{n}_dataset.csv")
o = rd("orders"); it = rd("order_items"); pay = rd("order_payments"); rv = rd("order_reviews")
cu = rd("customers"); se = rd("sellers"); pr = rd("products")
tr = pd.read_csv(d + "product_category_name_translation.csv")
for c in ["order_purchase_timestamp","order_delivered_customer_date","order_estimated_delivery_date"]:
    o[c] = pd.to_datetime(o[c])
o["month"] = o.order_purchase_timestamp.dt.to_period("M").astype(str)

# ---- data quality
print("dupe order ids:", o.order_id.duplicated().sum())
print("orders w/o items:", (~o.order_id.isin(it.order_id)).sum(), " delivered w/o items:", ((o.order_status=="delivered") & ~o.order_id.isin(it.order_id)).sum())
print("delivered w/o delivery date:", ((o.order_status=="delivered") & o.order_delivered_customer_date.isna()).sum())
print("delivery before purchase:", (o.order_delivered_customer_date < o.order_purchase_timestamp).sum())
print("delivered orders per month:\n", o[o.order_status=="delivered"].groupby("month").size().to_string())

# ---- base: delivered orders in the full-month window
START, END = "2017-01", "2018-08"
dl = o[(o.order_status=="delivered") & (o.month>=START) & (o.month<=END)].merge(cu[["customer_id","customer_unique_id","customer_state"]], on="customer_id")
dl["days"] = (dl.order_delivered_customer_date - dl.order_purchase_timestamp).dt.total_seconds()/86400
dl["delay"] = (dl.order_delivered_customer_date - dl.order_estimated_delivery_date).dt.total_seconds()/86400
dl["late"] = dl.order_delivered_customer_date > dl.order_estimated_delivery_date
dl["wd"] = dl.order_purchase_timestamp.dt.dayofweek   # 0=Mon
dl["hr"] = dl.order_purchase_timestamp.dt.hour
rvo = rv.groupby("order_id").review_score.mean().rename("review")
dl = dl.merge(rvo, on="order_id", how="left")
iq = it[it.order_id.isin(dl.order_id)]
agg = iq.groupby("order_id").agg(rev=("price","sum"), frt=("freight_value","sum"), items=("order_item_id","count"))
dl = dl.merge(agg, on="order_id", how="left")
print("dl rows", len(dl), "missing rev", dl.rev.isna().sum(), "missing review", dl.review.isna().sum(), "missing days", dl.days.isna().sum())
dl = dl.dropna(subset=["rev"])

bins = [-1e9, 0, 3, 7, 1e9]
dl["bucket"] = pd.cut(dl.delay, bins=bins, labels=[0,1,2,3], right=True).astype("float")
print("bucket counts", dl.bucket.value_counts(dropna=False).sort_index().to_dict())
print(dl.groupby("bucket").review.agg(["mean","count"]))
print("on-time rate", 1-dl.late.mean(), "avg days", dl.days.mean(), "median", dl.days.median())

K = {}
K["orders"] = int(len(dl)); K["revenue"] = float(dl.rev.sum()); K["freight"] = float(dl.frt.sum())
K["aov"] = float(dl.rev.mean()); K["customers"] = int(dl.customer_unique_id.nunique())
c = dl.groupby("customer_unique_id").size()
K["repeat_rate"] = float((c>1).mean()); K["repeat_share_orders"] = float(c[c>1].sum()/c.sum())
K["review"] = float(dl.review.mean()); K["on_time"] = float(1-dl.late.mean()); K["avg_days"] = float(dl.days.mean())
K["items"] = int(dl["items"].sum())
K["freight_ratio"] = K["freight"]/K["revenue"]
print(K)

# ---- review dist
K["review_dist"] = [int((dl.review.round()==i).sum()) for i in range(1,6)]
print("review dist", K["review_dist"], "pct 1-2:", sum(K["review_dist"][:2])/sum(K["review_dist"]))

# ---- sellers & categories at item level
items = iq.merge(dl[["order_id","month","customer_state"]], on="order_id").merge(pr[["product_id","product_category_name"]], on="product_id", how="left").merge(tr, on="product_category_name", how="left")
items["cat"] = items.product_category_name_english.fillna("unknown")
cat = items.groupby("cat").agg(rev=("price","sum"), n=("price","count"), frt=("freight_value","sum")).sort_values("rev", ascending=False)
cat["share"] = cat.rev/cat.rev.sum()
print(cat.head(20).to_string())
print("n categories", len(cat))
sel = items.merge(se[["seller_id","seller_state"]], on="seller_id", how="left")
srev = sel.groupby("seller_id").price.sum().sort_values(ascending=False)
K["sellers"] = int(len(srev)); K["top10pct_sellers_share"] = float(srev.head(int(len(srev)*0.1)).sum()/srev.sum())
K["top1pct_sellers_share"] = float(srev.head(max(1,int(len(srev)*0.01))).sum()/srev.sum())
K["seller_sp_share_revenue"] = float(sel[sel.seller_state=="SP"].price.sum()/sel.price.sum())
K["same_state_share"] = float((sel.seller_state==sel.customer_state).mean())
print({k:K[k] for k in ["sellers","top10pct_sellers_share","top1pct_sellers_share","seller_sp_share_revenue","same_state_share"]})
ss = sel.assign(same=(sel.seller_state==sel.customer_state)).groupby("same").agg(frt=("freight_value","mean"), p=("price","mean"))
print(ss)

# ---- state table
st = dl.groupby("customer_state").agg(orders=("order_id","count"), rev=("rev","sum"), frt=("frt","sum"), days=("days","mean"), late=("late","mean"), review=("review","mean"))
st["frt_ratio"] = st.frt/st.rev; st["share"] = st.rev/st.rev.sum()
print(st.sort_values("rev", ascending=False).round(3).to_string())

# ---- peak day
day = dl.groupby(dl.order_purchase_timestamp.dt.date).size().sort_values(ascending=False)
print("peak days", day.head(3).to_dict(), "median day", day.median())
mo = dl.groupby("month").agg(orders=("order_id","count"), rev=("rev","sum"), review=("review","mean"), late=("late","mean"), days=("days","mean"))
print(mo.round(3).to_string())

# ---- payment
pp = pay[pay.order_id.isin(dl.order_id)]
print(pp.groupby("payment_type").agg(v=("payment_value","sum"), n=("order_id","nunique")).assign(sh=lambda x:x.v/x.v.sum()))
cc = pp[pp.payment_type=="credit_card"]
print("cc avg installments", cc.payment_installments.mean(), "share >1", (cc.payment_installments>1).mean())
print(cc.groupby(pd.cut(cc.payment_installments,[0,1,3,6,10,24])).payment_value.agg(["mean","count"]))

# ---- weekday/hour
print(dl.groupby("wd").size().to_dict(), dl.groupby("hr").size().to_dict())
dl.to_pickle("dl.pkl"); items.to_pickle("items.pkl"); pp.to_pickle("pp.pkl")
json.dump(K, open("K.json","w"))
