"""Trial-level Student-t hierarchy with censored likelihood and paired changes.

Each endpoint is fitted separately. Group baseline/change parameters partially
pool through shared weak hyperpriors; participant random baseline/change terms
are independent, non-centered, and their SDs are shared across groups. This is a
new candidate scientific model, not a relabeling of old per-person MLE means.
"""
from itertools import combinations
import json
import numpy as np
import pandas as pd
import pymc as pm
import pytensor.tensor as pt
import arviz as az

GROUP_NAMES = ('both', 'strength', 'angle')


def validate_data(data, group_names=GROUP_NAMES):
    y = np.asarray(data['y'], dtype=float)
    c = np.asarray(data['censor'])
    pid = np.asarray(data['participant_index'])
    stage = np.asarray(data['stage_index'])
    group = np.asarray(data['group_index_per_participant'])
    scale = float(data['scale'])
    if y.ndim != 1 or not len(y) or not np.isfinite(y).all():
        raise ValueError('y must be nonempty finite physical-unit observations/bounds.')
    if any(a.shape != y.shape for a in (c, pid, stage)):
        raise ValueError('Observation arrays must have equal one-dimensional shape.')
    if not np.isin(c, [-1, 0, 1]).all() or not np.isin(stage, [0, 1]).all():
        raise ValueError('Censor codes -1/0/1; stages baseline=0, post-test=1 required.')
    if group.ndim != 1 or not len(group) or not np.isin(group, np.arange(len(group_names))).all():
        raise ValueError('Participant group indices are invalid.')
    if not np.isin(pid, np.arange(len(group))).all():
        raise ValueError('Participant indices must index group_index_per_participant.')
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError('Physical normalization scale must be finite and positive.')
    for i in range(len(group)):
        if set(stage[pid == i]) != {0, 1}:
            raise ValueError('Every participant must have baseline and post-test observations.')
    if set(group) != set(range(len(group_names))):
        raise ValueError('Each named group must be represented.')
    return y / scale, c.astype(int), pid.astype(int), stage.astype(int), group.astype(int), scale


def build_model(data, group_names=GROUP_NAMES, participant_names=None, nu=5):
    """Data y is physical-unit value or proven signed censor boundary; never uncapped.

    Population within-person variance integrates over lognormal random scales,
    but excludes variance of participant locations. No target centering occurs.
    """
    if nu <= 2:
        raise ValueError('nu must exceed 2 for finite variance.')
    y, censor, pid, stage, group, physical_scale = validate_data(data, group_names)
    if participant_names is None:
        participant_names = [str(i) for i in range(len(group))]
    if len(participant_names) != len(group):
        raise ValueError('Participant labels must match group array.')
    coords = dict(group=list(group_names), participant=list(participant_names),
                  stage=['baseline', 'test'], observation=np.arange(len(y)))
    with pm.Model(coords=coords) as model:
        # Non-centered group deviations; SDs expressed in normalized y/log-scale.
        def group_parameter(name, prior_mean, prior_sd, pooling_sd):
            # Integrate the redundant common component of independent group z.
            # Conditional covariance remains prior_sd**2 * J + tau**2 * I.
            # This is the same prior, with G-1 orthogonal zero-sum contrasts.
            from scipy.linalg import helmert
            count=len(group_names)
            basis=helmert(count,full=False).T
            tau = pm.HalfNormal(name+'_group_sd', pooling_sd)
            overall = pm.Normal(name+'_overall', prior_mean,
                                pt.sqrt(prior_sd**2+tau**2/count))
            z = pm.Normal(name+'_group_z', 0, 1, shape=count-1)
            return pm.Deterministic(name, overall + tau*pt.dot(basis,z), dims='group')
        mu0 = group_parameter('mu_baseline', 0., 1.5, .75)
        dmu = group_parameter('mu_change', 0., .75, .5)
        ls0 = group_parameter('logscale_baseline', np.log(.5), .75, .5)
        dls = group_parameter('logscale_change', 0., .5, .35)
        def person_effect(name, prior_sd):
            sd = pm.HalfNormal(name+'_sd', prior_sd)
            z = pm.Normal(name+'_z', 0, 1, dims='participant')
            return sd*z, sd
        u0, _ = person_effect('person_mu_baseline', .75)
        ud, _ = person_effect('person_mu_change', .5)
        v0, v0sd = person_effect('person_logscale_baseline', .5)
        vd, vdsd = person_effect('person_logscale_change', .35)
        p_mu = pm.Deterministic('participant_location', physical_scale*pt.stack(
            [mu0[group]+u0, mu0[group]+u0+dmu[group]+ud], axis=1), dims=('participant','stage'))
        p_ls = pt.stack([ls0[group]+v0, ls0[group]+v0+dls[group]+vd], axis=1)
        pm.Deterministic('participant_within_variance', physical_scale**2*nu/(nu-2)*pt.exp(2*p_ls),
                         dims=('participant','stage'))
        gloc = pm.Deterministic('group_location', physical_scale*pt.stack([mu0,mu0+dmu],axis=1),
                               dims=('group','stage'))
        group_ls = pt.stack([ls0,ls0+dls],axis=1)
        random_ls_var = pt.stack([v0sd**2,v0sd**2+vdsd**2])
        gvar = pm.Deterministic('group_within_variance', physical_scale**2*nu/(nu-2)*
                               pt.exp(2*group_ls+2*random_ls_var), dims=('group','stage'))
        pm.Deterministic('group_location_change', gloc[:,1]-gloc[:,0], dims='group')
        pm.Deterministic('group_variance_change', gvar[:,1]-gvar[:,0], dims='group')
        pm.Deterministic('group_log_variance_ratio', pt.log(gvar[:,1])-pt.log(gvar[:,0]), dims='group')
        # pm.Censored contributes CDF at left boundaries, survival probability at
        # right boundaries, density at exact observations. It never deletes caps.
        lower = np.where(censor == -1, y, -np.inf)
        upper = np.where(censor == 1, y, np.inf)
        # Equivalent trial-wise expression avoids two-index advanced tensor
        # indexing in PyTensor's compiled NUTS graph on Windows.
        trial_mu = mu0[group[pid]] + u0[pid] + stage*(dmu[group[pid]] + ud[pid])
        trial_ls = ls0[group[pid]] + v0[pid] + stage*(dls[group[pid]] + vd[pid])
        dist = pm.StudentT.dist(nu=nu, mu=trial_mu, sigma=pt.exp(trial_ls))
        pm.Censored('observed', dist, lower=lower, upper=upper, observed=y, dims='observation')
    model.hierarchical_metadata = dict(nu=float(nu),physical_scale=physical_scale,
        n_observations=len(y),n_censored=int(np.count_nonzero(censor)),
        n_participants=len(group),group_names=list(group_names),
        parameterization="orthogonal_group_contrasts_integrated_common_mode")
    return model


def sample_endpoint(data, draws=1500, tune=2000, chains=4, cores=1, seed=20261114,
                    target_accept=.995, group_names=GROUP_NAMES, participant_names=None,
                    nu=5, progressbar=True, compile_mode=None, max_treedepth=12):
    """MCMC only: no variational/point estimate is presented as posterior sampling.

    compile_mode can be 'NUMBA' when installed PyTensor supports the graph; errors
    propagate rather than silently changing inference. Short runs are smoke checks.
    """
    model = build_model(data,group_names,participant_names,nu)
    kwargs = {} if compile_mode is None else {'compile_kwargs':{'mode':compile_mode}}
    with model:
        idata = pm.sample(draws=draws,tune=tune,chains=chains,cores=min(cores,chains),
                          random_seed=seed,target_accept=target_accept,
                          nuts={'max_treedepth':max_treedepth}, progressbar=progressbar,
                          idata_kwargs={'log_likelihood':True}, **kwargs)
    idata.attrs['model_metadata'] = json.dumps(model.hierarchical_metadata)
    idata.attrs['sampling_settings'] = json.dumps(dict(draws=draws,tune=tune,chains=chains,
        cores=min(cores,chains),seed=seed,target_accept=target_accept,compile_mode=compile_mode,
        max_treedepth=max_treedepth))
    return idata


def _summary(values):
    values=np.asarray(values).ravel()
    if not np.isfinite(values).all():
        raise ValueError('Posterior contains nonfinite derived quantities.')
    low,high=np.quantile(values,[.025,.975])
    return dict(mean=float(np.mean(values)),median=float(np.median(values)),
                cri_low=float(low),cri_high=float(high),prob_less_zero=float(np.mean(values<0)))


def summarize_posterior(idata, group_names=None):
    """Equal-tailed 95% posterior intervals; contrasts are group A minus group B.

    Signed location delta below zero is not necessarily improvement toward zero.
    Variance changes/ratios concern expected within-person variance, not SEM.
    """
    post=idata.posterior
    names=list(post.coords['group'].values) if group_names is None else list(group_names)
    stages=[];changes=[];contrasts=[]
    for group in names:
        for stage in ('baseline','test'):
            for metric,var in [('location','group_location'),('within_variance','group_within_variance')]:
                stages.append(dict(group=group,stage=stage,metric=metric,
                                   **_summary(post[var].sel(group=group,stage=stage).values)))
        for metric,var in [('location_change','group_location_change'),
                           ('variance_change','group_variance_change'),
                           ('log_variance_ratio','group_log_variance_ratio')]:
            changes.append(dict(group=group,metric=metric,**_summary(post[var].sel(group=group).values)))
    for a,b in combinations(names,2):
        for metric,var in [('location_change','group_location_change'),
                           ('variance_change','group_variance_change'),
                           ('log_variance_ratio','group_log_variance_ratio')]:
            difference=post[var].sel(group=a)-post[var].sel(group=b)
            contrasts.append(dict(group_a=a,group_b=b,metric=metric,**_summary(difference.values)))
    # Include hyperparameters and participant latent terms, not only smooth summaries.
    ds=az.summary(idata,kind='diagnostics',round_to='none')
    finite_rhat=ds.r_hat[np.isfinite(ds.r_hat)]
    settings=json.loads(idata.attrs.get('sampling_settings','{}'))
    depth_limit=int(settings.get('max_treedepth',12))
    stats=idata.sample_stats
    depth_hits=int(stats.reached_max_treedepth.sum()) if 'reached_max_treedepth' in stats else int((stats.tree_depth>=depth_limit).sum())
    diagnostics=dict(chains=int(post.sizes['chain']),draws_per_chain=int(post.sizes['draw']),
        max_rhat=float(finite_rhat.max()) if len(finite_rhat) else None,
        min_ess_bulk=float(ds.ess_bulk.min()),min_ess_tail=float(ds.ess_tail.min()),
        divergences=int(idata.sample_stats.diverging.sum()),
        max_tree_depth=int(idata.sample_stats.tree_depth.max()),
        max_treedepth_hits=depth_hits,configured_max_treedepth=depth_limit,
        diagnostic_variables=len(ds),
        nonfinite_diagnostic_rows=int((~np.isfinite(ds[['r_hat','ess_bulk','ess_tail']]).all(axis=1)).sum()),
        min_bfmi=float(np.min(az.bfmi(idata))))
    diagnostics['sampling_adequate'] = bool(diagnostics['chains']>=4 and
        diagnostics['max_rhat'] is not None and diagnostics['max_rhat']<=1.01 and
        diagnostics['min_ess_bulk']>=400 and diagnostics['min_ess_tail']>=400 and
        diagnostics['divergences']==0 and diagnostics['nonfinite_diagnostic_rows']==0 and
        diagnostics['min_bfmi']>=.3 and diagnostics['max_treedepth_hits']==0)
    return dict(group_stages=pd.DataFrame(stages),within_group_changes=pd.DataFrame(changes),
                between_group_contrasts=pd.DataFrame(contrasts),diagnostics=diagnostics,
                diagnostic_table=ds)
