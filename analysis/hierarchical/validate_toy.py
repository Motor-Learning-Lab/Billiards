"""Reproducible simulation recovery check, separate from real endpoint inference."""
import json
from pathlib import Path
import numpy as np
from tests.hierarchical.test_model import toy_data
from .model import sample_endpoint,summarize_posterior


def main():
    data=toy_data(seed=72,per_group=8,trials=15)
    idata=sample_endpoint(data,draws=1000,tune=1000,chains=4,cores=1,
                          seed=731,compile_mode="NUMBA",progressbar=False)
    result=summarize_posterior(idata)
    truth={"both":(.4,.1),"strength":(0.,0.),"angle":(-.4,-.1)}
    table=result["group_stages"].copy()
    table["truth"]=[truth[r.group][0 if r.stage=="baseline" else 1] if r.metric=="location" else .2**2*5/3 for r in table.itertuples()]
    table["truth_inside_95cri"]=(table.truth>=table.cri_low)&(table.truth<=table.cri_high)
    out=Path("results/group_inference/bayes/toy_recovery")
    out.mkdir(parents=True,exist_ok=True)
    table.to_csv(out/"known_parameter_recovery.csv",index=False,encoding="utf-8-sig")
    result["diagnostic_table"].to_csv(out/"diagnostic_table.csv",encoding="utf-8-sig")
    (out/"diagnostics.json").write_text(json.dumps(result["diagnostics"],indent=2),encoding="utf-8")
    print(json.dumps(result["diagnostics"],indent=2),flush=True)
    print(table.to_string(index=False),flush=True)


if __name__=="__main__":main()
