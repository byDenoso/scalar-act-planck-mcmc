"""make_lite_yaml.py <modelo> <cadeia> <pacotes> <spt_dir> <saida_dir_chain>: YAML nativo P-ACT lite (Planck cortado + ACT DR6 lite + low-l + lensings + SPT-3G lite), parametrizacao cosmomc_theta (misturam melhor)."""
import sys, os, yaml
model, chain, pk, spt, chdir = sys.argv[1:6]
os.makedirs("run", exist_ok=True)
EXTRA = dict(kmax=10, k_per_logint=130, nonlinear=True, lens_potential_accuracy=8, lens_margin=2050, lAccuracyBoost=1.2, min_l_logl_sampling=6000, DoLateRadTruncation=False)
PARAMS = {
 "ombh2": {"prior": {"min": 0.017, "max": 0.027}, "ref": {"dist": "norm", "loc": 2.239e-2, "scale": 2.1e-4}, "proposal": 6.5e-5},
 "omch2": {"prior": {"min": 0.09, "max": 0.15}, "ref": {"dist": "norm", "loc": 0.12, "scale": 2.6e-3}, "proposal": 0.0011},
 "cosmomc_theta": {"prior": {"min": 103.0e-4, "max": 105.0e-4}, "ref": {"dist": "norm", "loc": 104.170e-4, "scale": 6.7e-6}, "proposal": 1.0e-5},
 "logA": {"prior": {"min": 2.6, "max": 3.5}, "ref": {"dist": "norm", "loc": 3.064, "scale": 0.024}, "proposal": 0.0036, "drop": True},
 "As": {"value": "lambda logA: 1e-10*np.exp(logA)", "derived": True},
 "ns": {"prior": {"min": 0.9, "max": 1.1}, "ref": {"dist": "norm", "loc": 0.9729, "scale": 0.006}, "proposal": 0.0033},
 "tau": {"prior": {"min": 0.0, "max": 0.1}, "ref": {"dist": "norm", "loc": 0.0544, "scale": 0.0073}, "proposal": 0.0073},
 "Tcal": {"prior": {"min": 0.8, "max": 1.2}, "ref": 1.0, "proposal": 0.01},
 "Ecal": {"prior": {"min": 0.8, "max": 1.2}, "ref": 1.0, "proposal": 0.01},
 "H0": {"latex": "H_0", "derived": True}, "sigma8": {"latex": "\\sigma_8", "derived": True}, "rdrag": {"derived": True},
}
if model.endswith("_Alens"): PARAMS["Alens"] = {"prior": {"min": 0.5, "max": 1.5}, "ref": {"dist": "norm", "loc": 1.0, "scale": 0.03}, "proposal": 0.03}
if model == "w0waCDM":
    EXTRA["dark_energy_model"] = "ppf"
    PARAMS["w"] = {"prior": {"min": -3, "max": 1}, "ref": {"dist": "norm", "loc": -1.0, "scale": 0.05}, "proposal": 0.05}
    PARAMS["wa"] = {"prior": {"min": -3, "max": 2}, "ref": {"dist": "norm", "loc": 0.0, "scale": 0.1}, "proposal": 0.1}
if model.startswith("PEER1P"):
    EXTRA.update(dark_energy_model="EarlyQuintessence", n=3.0, use_zc=True, zc=10 ** 3.56, theta_i=2.89155, m=8e-53, f=0.25)
    PARAMS["fde_zc"] = {"prior": {"min": 0.0005, "max": 0.18}, "ref": {"dist": "norm", "loc": 0.03, "scale": 0.005}, "proposal": 0.005}
LIK = {
 "planck_2018_lowl.TT": None, "planck_2018_lowl.EE_sroll2": None, "planck_2018_lensing.native": None,
 "act_dr6_cmbonly.PlanckActCut": {"dataset_params": {"use_cl": "tt te ee", "lmin_cuts": "0 0 0", "lmax_cuts": "1000 600 600"}, "params": {"A_planck": {"value": "lambda A_act: A_act", "latex": "A_{\\rm Planck}"}}},
 "act_dr6_cmbonly.ACTDR6CMBonly": {"stop_at_error": True},
 "act_dr6_lenslike.ACTDR6LensLike": {"variant": "act_baseline", "lmax": 4000},
 "spt3g_lite": {"class": "candl.interface.CandlCobayaLikelihood", "data_set_file": os.path.join(spt, "spt_candl_data/SPT3G_D1_TnE_v0/lite/SPT3G_D1_TnE_lite.yaml"), "clear_internal_priors": True, "feedback": False},
}
assert os.path.exists(LIK["spt3g_lite"]["data_set_file"]), "SPT yaml nao encontrado"
info = {"theory": {"camb": {"stop_at_error": False, "extra_args": EXTRA}}, "likelihood": LIK, "params": PARAMS,
        "prior": {"cal_dip_prior": "lambda A_act: stats.norm.logpdf(A_act, loc = 1.0, scale = 0.003)"},
        "sampler": {"mcmc": {"Rminus1_stop": 0.01, "Rminus1_cl_stop": 0.05, "max_samples": 400000, "max_tries": 100000, "learn_proposal": True}},
        "output": os.path.join(chdir, "chain"), "resume": True, "packages_path": pk}
os.makedirs(chdir, exist_ok=True)
out = f"run/{model}_c{chain}.yaml"; yaml.safe_dump(info, open(out, "w"), sort_keys=False); print("ok", out)
