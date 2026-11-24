import pandas as pd, numpy as np, json, sys
d=sys.argv[1]+"/"; out=sys.argv[2]
rd=lambda n: pd.read_csv(d+f"olist_{n}_dataset.csv")
o=rd("orders");it=rd("order_items");pay=rd("order_payments");rv=rd("order_reviews");cu=rd("customers");se=rd("sellers");pr=rd("products");ge=rd("geolocation")
for c in ["order_purchase_timestamp","order_delivered_customer_date","order_estimated_delivery_date"]: o[c]=pd.to_datetime(o[c])
o["month"]=o.order_purchase_timestamp.dt.to_period("M").astype(str)
P={}
tabs={"orders":o,"order_items":it,"order_payments":pay,"order_reviews":rv,"customers":cu,"sellers":se,"products":pr,"geolocation":ge}
P["tables"]={k:{"rows":int(len(v)),"cols":int(v.shape[1])} for k,v in tabs.items()}
st=o.order_status.value_counts()
P["status"]={k:int(v) for k,v in st.items()}
n0=len(o); dl=o[o.order_status=="delivered"]; n1=len(dl)
win=dl[(dl.month>="2017-01")&(dl.month<="2018-08")]; n2=len(win)
it_ids=set(it.order_id); n3=int(win.order_id.isin(it_ids).sum())
P["funnel"]=[n0,n1,n2,n3]
P["out_of_window_delivered"]=int(n1-n2)
P["first_order"]=str(o.order_purchase_timestamp.min().date());P["last_order"]=str(o.order_purchase_timestamp.max().date())
P["dq"]={
 "dupe_orders":int(o.order_id.duplicated().sum()),
 "delivered_no_date":int(((o.order_status=="delivered")&o.order_delivered_customer_date.isna()).sum()),
 "orders_no_items":int((~o.order_id.isin(it_ids)).sum()),
 "reviews_multi_order":int((rv.groupby("order_id").size()>1).sum()),
 "products_no_category":int(pr.product_category_name.isna().sum()),
 "categories":int(pr.product_category_name.nunique()),
 "cust_ids":int(cu.customer_id.nunique()),"cust_unique":int(cu.customer_unique_id.nunique()),
 "pay_multi_order":int((pay.groupby("order_id").size()>1).sum()),
 "review_no_text_pct":float(rv.review_comment_message.isna().mean()),
 "geo_dupe_pct":float(ge.duplicated(["geolocation_zip_code_prefix","geolocation_lat","geolocation_lng"]).mean()),
}
P["dq"]["delivered_before_purchase"]=int((o.order_delivered_customer_date<o.order_purchase_timestamp).sum())
json.dump(P,open(out,"w"),separators=(",",":"));print(json.dumps(P,indent=1))
