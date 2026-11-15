"""Run one independent endpoint from an audited NPZ input file."""
import argparse
import json
from pathlib import Path
import numpy as np
from .model import sample_endpoint, summarize_posterior


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input",type=Path)
    parser.add_argument("output",type=Path)
    parser.add_argument("--draws",type=int,default=1500)
    parser.add_argument("--tune",type=int,default=2000)
    parser.add_argument("--chains",type=int,default=4)
    parser.add_argument("--cores",type=int,default=1)
    parser.add_argument("--seed",type=int,default=20261114)
    parser.add_argument("--target-accept",type=float,default=.995)
    parser.add_argument("--compile-mode",default="NUMBA")
    args=parser.parse_args()
    data=dict(np.load(args.input,allow_pickle=False))
    args.output.mkdir(parents=True,exist_ok=True)
    print("Starting endpoint",args.input,flush=True)
    idata=sample_endpoint(data,draws=args.draws,tune=args.tune,chains=args.chains,cores=args.cores,
                          seed=args.seed,target_accept=args.target_accept,compile_mode=args.compile_mode)
    idata.to_netcdf(args.output/"posterior.nc")
    result=summarize_posterior(idata)
    for key in ("group_stages","within_group_changes","between_group_contrasts","diagnostic_table"):
        result[key].to_csv(args.output/(key+".csv"),encoding="utf-8-sig",index=key=="diagnostic_table")
    (args.output/"diagnostics.json").write_text(json.dumps(result["diagnostics"],indent=2),encoding="utf-8")
    print(json.dumps(result["diagnostics"],indent=2),flush=True)


if __name__=="__main__": main()
