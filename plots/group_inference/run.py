"""Group estimators and hierarchical inference; read-only source CSVs."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from common.paths import PARTICIPANT_ROOT, OUTPUT_ROOT
from common.group_inference_data import load_inputs
from analysis.group_estimators.sensitivity import compare_estimators
from plots.group_inference.figures import draw_estimator_effects
from plots.group_inference.bivariate_figures import write_scatterplots

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=PARTICIPANT_ROOT)
    parser.add_argument("--out",type=Path,default=OUTPUT_ROOT/"group_inference")
    parser.add_argument("--bayesian",action="store_true",help="Run four-chain hierarchical MCMC; optional separate analysis")
    parser.add_argument("--endpoint",choices=["both_strength","strength_strength","both_angle","angle_angle"],action="append")
    parser.add_argument("--draws",type=int,default=1500);parser.add_argument("--tune",type=int,default=2000)
    parser.add_argument("--cores",type=int,default=1);parser.add_argument("--seed",type=int,default=20261114)
    parser.add_argument("--target-accept",type=float,default=.995)
    parser.add_argument("--resamples",type=int,default=9999)
    parser.add_argument("--compile-mode",choices=["NUMBA","default"],default="NUMBA")
    args=parser.parse_args();out=args.out.resolve();root=args.root.resolve()
    if out==root or out.is_relative_to(root): parser.error("Output must be outside participant source directories")
    out.mkdir(parents=True,exist_ok=True)
    datasets,stages,audit,hashes=load_inputs(root)
    for name,data in datasets.items():
        np.savez_compressed(out/(name+"_inputs.npz"),**data)
    points,contrasts,pairs=compare_estimators(stages,args.resamples,args.seed)
    for name,table in [("stage_estimates",stages),("selection_audit",audit),("estimator_group_points",points),("estimator_group_contrasts",contrasts),("participant_pairs",pairs)]:
        table.to_csv(out/(name+".csv"),index=False,encoding="utf-8-sig")
    write_scatterplots(points,pairs,out)
    draw_estimator_effects(contrasts,out)
    (out/"source_hashes.json").write_text(json.dumps(hashes,indent=2),encoding="utf-8")
    diagnostics={}
    if args.bayesian:
        from analysis.hierarchical.model import sample_endpoint
        from analysis.hierarchical.artifacts import export_posterior
        for name,data in datasets.items():
            if args.endpoint and name not in args.endpoint: continue
            dest=out/"bayes"/name;dest.mkdir(parents=True,exist_ok=True)
            idata=sample_endpoint(data,draws=args.draws,tune=args.tune,chains=4,cores=args.cores,seed=args.seed,
                                  target_accept=args.target_accept,compile_mode=None if args.compile_mode=="default" else args.compile_mode)
            idata.to_netcdf(dest/"posterior.nc")
            result=export_posterior(data,idata,dest)
            diagnostics[name]=result["diagnostics"]
            (dest/"diagnostics.json").write_text(json.dumps(result["diagnostics"],indent=2),encoding="utf-8")
            print(name,json.dumps(result["diagnostics"]))
    if args.bayesian and set(diagnostics) == set(datasets):
        from plots.group_inference.posterior_figures import draw_posteriors, draw_variance_scatter
        draw_posteriors(out)
        draw_variance_scatter(out)
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest for p,digest in hashes.items()),"Input changed during run"
    (out/"run_manifest.json").write_text(json.dumps(dict(input_hashes_unchanged=len(hashes),resamples=args.resamples,
        seed=args.seed,bayesian_requested=args.bayesian,diagnostics=diagnostics),indent=2),encoding="utf-8")
    print("Complete:",out)

if __name__=="__main__": main()
