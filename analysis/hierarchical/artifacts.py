"""Export reproducible compact posterior data and transparent diagnostics."""
from pathlib import Path
import json,hashlib
import numpy as np
import arviz as az
from .model import summarize_posterior
from .predictive import predictive_checks

def export_posterior(data,idata,out,predictive_replicates=400):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    result=summarize_posterior(idata)
    for name,value in result.items():
        if name!="diagnostics":value.to_csv(out/(name+".csv"),index=name=="diagnostic_table",encoding="utf-8-sig")
    (out/"diagnostics.json").write_text(json.dumps(result["diagnostics"],indent=2),encoding="utf-8")
    fields=["group_location","group_within_variance","group_location_change","group_variance_change","group_log_variance_ratio"]
    samples={name:idata.posterior[name].values for name in fields}
    samples["groups"]=idata.posterior.group.values.astype(str);samples["stages"]=idata.posterior.stage.values.astype(str)
    np.savez_compressed(out/"group_posterior.npz",**samples)
    table,meta=predictive_checks(data,idata,replicates=predictive_replicates)
    table.to_csv(out/"predictive_checks.csv",index=False,encoding="utf-8-sig")
    (out/"predictive_metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    full=out/"posterior.nc"
    snapshot=out.parent.parent/"source_hashes.json"
    source_hashes=json.loads(snapshot.read_text(encoding="utf-8")) if snapshot.exists() else {}
    source_digest=hashlib.sha256(json.dumps(source_hashes,sort_keys=True).encode()).hexdigest()
    data_digest=hashlib.sha256()
    for key in sorted(data):
        array=np.asarray(data[key])
        data_digest.update(key.encode());data_digest.update(str(array.dtype).encode())
        data_digest.update(str(array.shape).encode());data_digest.update(array.tobytes())
    manifest=dict(source_snapshot_sha256=source_digest if source_hashes else None,
        endpoint_arrays_sha256=data_digest.hexdigest(),model=json.loads(idata.attrs["model_metadata"]),sampling=json.loads(idata.attrs["sampling_settings"]),
        group_draw_array_order="chain, draw, group[, stage]",full_trace_local_only=True,
        full_trace_bytes=full.stat().st_size if full.exists() else None,
        full_trace_sha256=hashlib.sha256(full.read_bytes()).hexdigest() if full.exists() else None,
        diagnostic_status="adequate" if result["diagnostics"]["sampling_adequate"] else "review_required")
    (out/"posterior_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    return result

def finalize_all(root):
    root=Path(root);all_diagnostics={}
    hashes=json.loads((root/"source_hashes.json").read_text(encoding="utf-8"))
    if not all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==v for p,v in hashes.items()):
        raise ValueError("Current sources differ from the audited sampling inputs")
    for name in ("both_strength","strength_strength","both_angle","angle_angle"):
        out=root/"bayes"/name
        with np.load(root/(name+"_inputs.npz"),allow_pickle=False) as f:data=dict(f)
        idata=az.from_netcdf(out/"posterior.nc")
        all_diagnostics[name]=export_posterior(data,idata,out)["diagnostics"]
        print(name,all_diagnostics[name],flush=True)
    (root/"bayesian_diagnostics.json").write_text(json.dumps(all_diagnostics,indent=2),encoding="utf-8")
    return all_diagnostics

if __name__=="__main__":
    from common.paths import OUTPUT_ROOT
    finalize_all(OUTPUT_ROOT/"group_inference")
