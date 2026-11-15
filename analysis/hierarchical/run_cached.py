"""Run the remaining audited endpoint cache files; source hashes are checked."""
from pathlib import Path
import json,hashlib
import numpy as np
from analysis.hierarchical.model import sample_endpoint,summarize_posterior

def main():
    root=Path(__file__).resolve().parents[2]/"results/group_inference"
    hashes=json.loads((root/"source_hashes.json").read_text())
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==v for p,v in hashes.items())
    for name in ("strength_strength","both_angle","angle_angle"):
        print("Starting",name,flush=True)
        data=dict(np.load(root/(name+"_inputs.npz")))
        out=root/"bayes"/name;out.mkdir(parents=True,exist_ok=True)
        idata=sample_endpoint(data,draws=1500,tune=2000,chains=4,cores=1,seed=20261114,compile_mode="NUMBA",target_accept=.995,progressbar=False)
        idata.to_netcdf(out/"posterior.nc")
        summary=summarize_posterior(idata)
        for key,value in summary.items():
            if key=="diagnostics": (out/"diagnostics.json").write_text(json.dumps(value,indent=2),encoding="utf-8")
            else: value.to_csv(out/(key+".csv"),index=key=="diagnostic_table",encoding="utf-8-sig")
        print(name,summary["diagnostics"],flush=True)
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==v for p,v in hashes.items())

if __name__=="__main__":main()
