import pandas as pd, numpy as np, json, sys
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
src, out = sys.argv[1], sys.argv[2]
m = pd.read_csv(src, sep=None, engine="python"); n0 = len(m)
miss = m.Income.isna(); outl = m.Income > 200000; old = m.Year_Birth < 1930
c = m[~(miss | outl | old)].copy()
c["age"] = 2014 - c.Year_Birth
mnt = ["MntWines","MntFruits","MntMeatProducts","MntFishProducts","MntSweetProducts","MntGoldProds"]
c["spend"] = c[mnt].sum(axis=1); c["kids"] = c.Kidhome + c.Teenhome
EDU = ["Basic","2n Cycle","Graduation","Master","PhD"]; c["edu"] = c.Education.map(EDU.index)
c["mar"] = c.Marital_Status.map(lambda s: 0 if s in ("Married","Together") else 2 if s in ("Absurd","YOLO") else 1)
c["enr"] = pd.to_datetime(c.Dt_Customer, format="%d-%m-%Y"); c["tenure"] = (pd.Timestamp("2014-06-30") - c.enr).dt.days
X = c[["Income","spend","NumWebPurchases","NumCatalogPurchases","NumStorePurchases","NumWebVisitsMonth","NumDealsPurchases","kids"]].copy()
X["Income"] = np.log(X.Income); X["spend"] = np.log1p(X.spend); Z = StandardScaler().fit_transform(X)
km = KMeans(4, n_init=20, random_state=7).fit(Z); sil = float(silhouette_score(Z, km.labels_))
# stable naming: order clusters by mean spend desc -> 0 top spenders ... then label by profile
c["raw"] = km.labels_; order = c.groupby("raw").spend.mean().sort_values(ascending=False).index.tolist()
# order by spend: [high-value, mid regular, deal seekers(542), low]
c["seg"] = c.raw.map({r: i for i, r in enumerate(order)})
cols = ["age","edu","mar","Income","Kidhome","Teenhome","tenure","Recency"] + mnt + ["NumDealsPurchases","NumWebPurchases","NumCatalogPurchases","NumStorePurchases","NumWebVisitsMonth","AcceptedCmp1","AcceptedCmp2","AcceptedCmp3","AcceptedCmp4","AcceptedCmp5","Response","Complain","seg"]
rows = c[cols].astype(int).values.tolist()
seg_prof = c.groupby("seg").agg(n=("ID","count"), inc=("Income","mean"), spend=("spend","mean"), kids=("kids","mean"), deals=("NumDealsPurchases","mean"), vis=("NumWebVisitsMonth","mean"), resp=("Response","mean")).round(2).to_dict("index")
P = {"raw_rows": n0, "raw_cols": int(m.shape[1]), "clean_rows": len(c), "miss_income": int(miss.sum()), "income_outlier": int(outl.sum()), "birth_before_1930": int(old.sum()),
     "removed_total": int((miss | outl | old).sum()), "marital_unclear": int((c.mar == 2).sum()), "const_cols": 2, "dupes": int(m.duplicated().sum()),
     "enroll_min": str(c.enr.min().date()), "enroll_max": str(c.enr.max().date()), "complain": int(c.Complain.sum()), "silhouette": round(sil, 3), "seg_prof": seg_prof,
     "education": {k: int(v) for k, v in m.Education.value_counts().items()}, "marital": {k: int(v) for k, v in m.Marital_Status.value_counts().items()}}
ref = {"n": len(c), "spend": int(c.spend.sum()), "resp": round(float(c.Response.mean()), 4), "avg_spend": round(float(c.spend.mean()), 2), "avg_income": round(float(c.Income.mean()), 1)}
json.dump({"cols": cols, "rows": rows, "profile": P, "ref": ref}, open(out, "w"), separators=(",", ":"))
print(json.dumps(P, indent=1)); print(ref, len(json.dumps(rows)) // 1024, "KB")
