"""Participant-paired estimator sensitivity; bootstrap intervals are not posteriors."""
from itertools import combinations
import numpy as np
import pandas as pd
from scipy.stats import trim_mean, ttest_ind
from common.publication_data import GROUPS

ESTIMATORS={"mean":lambda x,axis=0: np.mean(x,axis=axis),
            "median":lambda x,axis=0: np.median(x,axis=axis),
            "trimmed_mean_20pct":lambda x,axis=0: trim_mean(x,.2,axis=axis)}

def holm(pvalues):
    p=np.asarray(pvalues,float);result=np.full(len(p),np.nan);finite=np.flatnonzero(np.isfinite(p))
    order=finite[np.argsort(p[finite])]
    if len(order): result[order]=np.minimum(1,np.maximum.accumulate(p[order]*(len(order)-np.arange(len(order)))))
    return result

def compare_estimators(stages,resamples=9999,seed=20261114):
    keys=["participant","group","task","channel"]
    if stages.duplicated(keys+["stage"]).any(): raise ValueError("Duplicate stage records")
    pre=stages[stages.stage.eq("baseline")].set_index(keys)
    post=stages[stages.stage.eq("test")].set_index(keys)
    pairs=pre[["location","variance","mae"]].join(post[["location","variance","mae"]],lsuffix="_pre",rsuffix="_post",how="inner").reset_index()
    rng=np.random.default_rng(seed);points=[];contrasts=[]
    for (task,ch),subset in pairs.groupby(["task","channel"],sort=True):
        for metric in ("location","variance","mae"):
            draws={};original={}
            for group in GROUPS:
                g=subset[subset.group.eq(group)];a=g[[metric+"_pre",metric+"_post"]].to_numpy(float)
                a=a[np.isfinite(a).all(axis=1)]
                if len(a)<3: raise ValueError("Insufficient paired participant estimates")
                boot=a[rng.integers(len(a),size=(resamples,len(a)))]
                original[group]=a
                for name,func in ESTIMATORS.items():
                    point=func(a,axis=0);bd=func(boot,axis=1);delta=bd[:,1]-bd[:,0]
                    draws[group,name]=delta
                    lo,hi=np.quantile(bd,[.025,.975],axis=0)
                    dl,dh=np.quantile(delta,[.025,.975])
                    points.append(dict(task=task,channel=ch,metric=metric,group=group,estimator=name,n=len(a),
                        baseline=point[0],post=point[1],baseline_low=lo[0],baseline_high=hi[0],post_low=lo[1],post_high=hi[1],
                        change=point[1]-point[0],change_low=dl,change_high=dh,
                        estimator_of_paired_changes=float(func(a[:,1]-a[:,0],axis=0))))
            for ga,gb in combinations(GROUPS,2):
                a,b=original[ga],original[gb];da=a[:,1]-a[:,0];db=b[:,1]-b[:,0]
                for name,func in ESTIMATORS.items():
                    delta=draws[ga,name]-draws[gb,name];low,high=np.quantile(delta,[.025,.975])
                    effect=(func(a,axis=0)[1]-func(a,axis=0)[0])-(func(b,axis=0)[1]-func(b,axis=0)[0])
                    p=float(ttest_ind(da,db,equal_var=False).pvalue) if name=="mean" else np.nan
                    pooled=np.sqrt(((len(da)-1)*da.var(ddof=1)+(len(db)-1)*db.var(ddof=1))/(len(da)+len(db)-2))
                    hedges=(1-3/(4*(len(da)+len(db))-9))*(da.mean()-db.mean())/pooled if name=="mean" and pooled>0 else np.nan
                    contrasts.append(dict(task=task,channel=ch,metric=metric,group_a=ga,group_b=gb,estimator=name,
                        difference_in_changes=effect,low=low,high=high,welch_p=p,hedges_g=hedges,
                        interval="pointwise participant-paired percentile bootstrap",n_a=len(a),n_b=len(b)))
    c=pd.DataFrame(contrasts);c["welch_p_holm_all_mean_contrasts"]=holm(c.welch_p)
    return pd.DataFrame(points),c,pairs
