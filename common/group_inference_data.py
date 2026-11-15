"""Read-only baseline/post inputs for estimator and hierarchical sensitivity analysis."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from common.paths import PARTICIPANT_ROOT, assignments_path
from common.publication_data import GROUPS, discover
from analysis.robust.censoring import censor_codes, censor_values
from plots.baseline_transfer.robust_comparison import compute_stage_metrics

ENDPOINTS = (("both", "strength"), ("strength", "strength"), ("both", "angle"), ("angle", "angle"))

def eligible(df, channel):
    """Require scored finite values, valid=1 when present, and never include flag=1."""
    v = pd.to_numeric(df[channel+"_value"], errors="coerce")
    mask = np.isfinite(v) & df[channel+"_status"].astype(str).str.strip().str.lower().eq("scored")
    if channel+"_valid" in df:
        mask &= pd.to_numeric(df[channel+"_valid"], errors="coerce").eq(1)
    if channel+"_outlier" in df:
        mask &= ~pd.to_numeric(df[channel+"_outlier"], errors="coerce").eq(1)
    return mask.to_numpy()

def load_inputs(root=PARTICIPANT_ROOT):
    root=Path(root); ap=assignments_path(root)
    assignment=json.loads(ap.read_text(encoding="utf-8-sig"))["assignments"]
    ids=[f"{i:02d}" for i in range(1,31)]
    groups=[assignment[i].lower() for i in ids]
    if any(groups.count(g)!=10 for g in GROUPS): raise ValueError("Expected 10 participants per group")
    hashes={str(ap.resolve()):hashlib.sha256(ap.read_bytes()).hexdigest()}
    files={i:discover(root,i) for i in ids}
    records=[];audit=[];datasets={}
    for task,ch in ENDPOINTS:
        trials=[]
        for idx,pid in enumerate(ids):
            if ("training",groups[idx]) not in files[pid]: raise ValueError("Group/filename mismatch: "+pid)
            for stage_idx,stage in enumerate(("baseline","test")):
                path=files[pid][stage,task];hashes[str(path.resolve())]=hashlib.sha256(path.read_bytes()).hexdigest()
                df=pd.read_csv(path);mask=eligible(df,ch)
                if mask.sum()<5: raise ValueError(f"Insufficient eligible stage observations: {pid}/{task}/{ch}/{stage}")
                values=censor_values(df,ch);codes=censor_codes(df,ch)
                # Fit the same legacy stage estimator on explicitly selected rows.
                selected=df.loc[mask].reset_index(drop=True).copy()
                selected[ch+"_status"]=selected[ch+"_status"].astype(str).str.strip().str.lower()
                stats=compute_stage_metrics(selected)
                records.append(dict(participant=pid,group=groups[idx],task=task,channel=ch,stage=stage,
                    n=int(mask.sum()),location=stats[ch+"_mean"],variance=stats[ch+"_variance"],mae=stats[ch+"_abs_err"],
                    fit_success=stats[ch+"_fit_success"],fit_message=stats[ch+"_fit_message"]))
                audit.append(dict(participant=pid,group=groups[idx],task=task,channel=ch,stage=stage,
                    source=str(path.resolve()),rows=len(df),included=int(mask.sum()),censored=int(np.count_nonzero(codes[mask]))))
                for j in np.flatnonzero(mask):
                    trials.append((values[j],int(codes[j]),idx,stage_idx))
        a=np.asarray(trials,float)
        scale=float(np.sqrt(np.mean(a[a[:,3]==0,0]**2)))
        if not np.isfinite(scale) or scale<=0: raise ValueError("Baseline RMS scale must be positive")
        datasets[task+"_"+ch]=dict(y=a[:,0],censor=a[:,1].astype(int),participant_index=a[:,2].astype(int),
            stage_index=a[:,3].astype(int),group_index_per_participant=np.array([GROUPS.index(g) for g in groups]),
            scale=scale)
    return datasets,pd.DataFrame(records),pd.DataFrame(audit),hashes
