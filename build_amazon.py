import pandas as pd, numpy as np, json, sys, re
src, out = sys.argv[1], sys.argv[2]
a = pd.read_csv(src); n0 = len(a); ncols = a.shape[1]
num = lambda s: pd.to_numeric(s.astype(str).str.replace(r"[₹,%]", "", regex=True), errors="coerce")
a["price"] = num(a.discounted_price); a["list"] = num(a.actual_price); a["disc"] = num(a.discount_percentage); a["rating"] = num(a.rating); a["rc"] = num(a.rating_count)
a["nrev"] = a.review_id.str.split(",").str.len()
bad_rating = int(a.rating.isna().sum()); rc_na = int(a.rating_count.isna().sum())
calc = ((1 - a.price / a.list) * 100).round(); mismatch = int((abs(calc - a.disc) > 1).sum())
dupe_rows = int(a.product_id.duplicated().sum())
a["_rc"] = a.rc.fillna(-1); a = a.sort_values("_rc", ascending=False).drop_duplicates("product_id").sort_index()
u = a.copy(); n1 = len(u)
u["l1"] = u.category.str.split("|").str[0]; u["l2"] = u.category.str.split("|").str[1]
L1 = ["Electronics", "Computers&Accessories", "Home&Kitchen", "OfficeProducts"]
u["l1c"] = u.l1.map(lambda s: L1.index(s) if s in L1 else 4)
l2n = u.l2.value_counts(); top2 = [k for k, v in l2n.items() if v >= 10]; print(len(l2n), "L2;", len(top2), "with >=10")
u["l2c"] = u.l2.map(lambda s: top2.index(s) if s in top2 else len(top2))
cols = ["l1c", "l2c", "price", "list", "disc", "rating10", "rc", "nrev"]
u["rating10"] = (u.rating * 10).round().fillna(-1).astype(int); u["rc"] = u.rc.fillna(-1).astype(int)
rows = u[cols].astype(int).values.tolist(); names = [re.sub(r"\s+", " ", s)[:90] for s in u.product_name]
P = {"raw_rows": n0, "raw_cols": int(ncols), "unique_products": n1, "dupe_rows": dupe_rows, "bad_rating": bad_rating, "rating_count_na": rc_na, "disc_mismatch": mismatch,
     "total_reviews_listed": int(u.nrev.sum()), "l1_n": int(u.l1.nunique()), "l2_n": int(len(l2n)), "l1": L1 + ["Other"], "l2": top2 + ["Other"], "l1_counts": {k: int((u.l1c == i).sum()) for i, k in enumerate(L1 + ["Other"])},
     "list_gt_price": int((u.price > u.list).sum()), "disc_zero": int((u.disc == 0).sum())}
ref = {"n": n1, "avg_disc": round(float(u.disc.mean()), 3), "avg_rating": round(float(u.rating.mean()), 4), "med_price": float(u.price.median()), "rc_sum": int(u.rc[u.rc > 0].sum())}
json.dump({"cols": cols, "rows": rows, "names": names, "profile": P, "ref": ref}, open(out, "w"), ensure_ascii=False, separators=(",", ":"))
print(json.dumps(P, indent=1, ensure_ascii=False)); print(ref); print(top2)
