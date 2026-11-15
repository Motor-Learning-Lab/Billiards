"""Design-matched prior/posterior predictive checks in original measurement units."""
import json
import numpy as np
import pandas as pd
import pymc as pm
from .model import build_model,validate_data,GROUP_NAMES


def predictive_checks(data, idata, replicates=400, seed=20261115, group_names=GROUP_NAMES):
    """Return check table plus provenance; bounds must be known for every trial.

    Optional input keys lower_bound/upper_bound are physical-unit protocol limits,
    not limits invented only for observations that happened to be censored. With
    actual censoring but without these limits, observed-distribution checks are
    limited to descriptive latent-versus-selected-exact comparisons; no censor
    rate or coverage claim is made for that case.
    """
    _,c,pid,stage,group,_=validate_data(data,group_names)
    y=np.asarray(data['y'],float)
    has_bounds='lower_bound' in data and 'upper_bound' in data
    latent_only = bool(np.any(c!=0) and not has_bounds)
    lower=np.asarray(data.get('lower_bound',np.full(len(y),-np.inf)),float)
    upper=np.asarray(data.get('upper_bound',np.full(len(y),np.inf)),float)
    if lower.shape!=y.shape or upper.shape!=y.shape or np.isnan(lower).any() or np.isnan(upper).any() or np.any(lower>=upper):
        raise ValueError('Predictive bounds must match y, be ordered, and not NaN.')
    if np.any(y<lower-1e-8) or np.any(y>upper+1e-8):
        raise ValueError('Observed responses fall outside specified protocol bounds.')
    if has_bounds and (np.any((c<0)&~np.isclose(y,lower)) or np.any((c>0)&~np.isclose(y,upper))):
        raise ValueError('Censor codes disagree with protocol boundary values.')
    metadata=json.loads(idata.attrs.get('model_metadata','{}'))
    nu=float(metadata.get('nu',5))
    model=build_model(data,group_names=group_names,nu=nu)
    with model:
        prior=pm.sample_prior_predictive(samples=replicates,random_seed=seed,
            var_names=['participant_location','participant_within_variance'])
    rng=np.random.default_rng(seed+1)
    obs_group=group[pid]
    result=[]
    for kind,ds in [('prior',prior.prior),('posterior',idata.posterior)]:
        loc=ds.participant_location.stack(sample=('chain','draw')).transpose('sample','participant','stage').values
        var=ds.participant_within_variance.stack(sample=('chain','draw')).transpose('sample','participant','stage').values
        select=rng.choice(len(loc),size=replicates,replace=len(loc)<replicates)
        mu=loc[select][:,pid,stage]
        sigma=np.sqrt(var[select][:,pid,stage]*(nu-2)/nu)
        latent=mu+sigma*rng.standard_t(nu,size=mu.shape)
        simulated=np.clip(latent,lower,upper)
        censored=(latent<=lower)|(latent>=upper)
        for gi,name in enumerate(group_names):
            for si,stage_name in enumerate(('baseline','test')):
                mask=(obs_group==gi)&(stage==si)
                if latent_only:
                    mask = mask & (c == 0)
                if mask.sum()<2:
                    continue
                observed=y[mask];rep=simulated[:,mask]
                checks={'mean':(observed.mean(),rep.mean(axis=1)),
                    'sd':(observed.std(ddof=1),rep.std(axis=1,ddof=1)),
                    'q05':(np.quantile(observed,.05),np.quantile(rep,.05,axis=1)),
                    'q95':(np.quantile(observed,.95),np.quantile(rep,.95,axis=1)),
                    'censor_rate':(np.mean(c[mask]!=0),censored[:,mask].mean(axis=1))}
                if not has_bounds:
                    checks.pop('censor_rate')
                for metric,(actual,samples) in checks.items():
                    lo,hi=np.quantile(samples,[.025,.975])
                    result.append(dict(predictive=kind,group=name,stage=stage_name,metric=metric,
                        n_observations=int(mask.sum()),observed=float(actual),predictive_median=float(np.median(samples)),
                        predictive_low=float(lo),predictive_high=float(hi),
                        comparison='latent_vs_selected_exact_descriptive_only' if latent_only else 'design_matched',
                        inside_95_predictive_interval=None if latent_only else bool(lo<=actual<=hi),
                        predictive_fraction_ge_observed=None if latent_only else float(np.mean(samples>=actual))))
    return pd.DataFrame(result),dict(available=True,replicates=replicates,seed=seed,
        protocol_bounds_supplied=has_bounds,censor_rate_check_available=has_bounds,
        latent_only=latent_only,selection_limitation='Without protocol bounds, exact-only rows are selected by observed outcomes; latent tail comparisons are descriptive and not calibrated predictive checks.' if latent_only else '',interpretation='Design-matched distribution diagnostics, not credible intervals for effects or calibrated goodness-of-fit p-values.')
