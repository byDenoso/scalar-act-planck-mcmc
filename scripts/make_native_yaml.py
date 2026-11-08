"""Gera configs Cobaya NATIVAS (CAMB real em cada amostra) para os modelos CMB-only. Rodar em maquina maior (>=16 GB, MPI).
uso: python make_native_yaml.py <dir_saida> [--plik-only]  (--plik-only: so Planck plik-lite, para teste rapido)"""
import sys, os, json, yaml
out = sys.argv[1]; plik_only = "--plik-only" in sys.argv; os.makedirs(out, exist_ok=True)
D = os.environ.get("NEXO_DIR", ".")
SPT = os.path.join(D, "dl_spt/repo/spt_candl_data/SPT3G_D1_TnE_v0/lite/SPT3G_D1_TnE_lite.yaml")
EXTRA = dict(lmax=9000, lens_potential_accuracy=1, lens_margin=2050)
LIK = {"planck_2018_highl_plik.TTTEEE_lite_native": None, "planck_2018_lowl.TT": None, "planck_2018_lowl.EE_sroll2": None, "planck_2018_lensing.native": None}
if not plik_only:
    LIK.update({"act_dr6_mflike.ACTDR6MFLike": None, "act_dr6_lenslike.ACTDR6LensLike": {"variant": "act_baseline", "lmax": 4000},
                "spt3g_lite": {"class": "candl.interface.CandlCobayaLikelihood", "data_set_file": SPT, "clear_internal_priors": True, "feedback": False}})
BASE = {"H0": {"prior": {"min": 40, "max": 100}, "ref": {"dist": "norm", "loc": 67.7, "scale": 0.5}, "proposal": 0.4},
        "ombh2": {"prior": {"min": 0.005, "max": 0.1}, "ref": {"dist": "norm", "loc": 0.0225, "scale": 0.0001}, "proposal": 0.0001},
        "omch2": {"prior": {"min": 0.001, "max": 0.99}, "ref": {"dist": "norm", "loc": 0.119, "scale": 0.001}, "proposal": 0.001},
        "logA": {"prior": {"min": 1.61, "max": 3.91}, "ref": {"dist": "norm", "loc": 3.07, "scale": 0.01}, "proposal": 0.01, "drop": True},
        "As": {"value": "lambda logA: 1e-10*np.exp(logA)"},
        "ns": {"prior": {"min": 0.8, "max": 1.2}, "ref": {"dist": "norm", "loc": 0.968, "scale": 0.004}, "proposal": 0.004},
        "tau": {"prior": {"min": 0.01, "max": 0.15}, "ref": {"dist": "norm", "loc": 0.06, "scale": 0.006}, "proposal": 0.006}}
if not plik_only:
    BASE.update({"Tcal": {"prior": {"min": 0.8, "max": 1.2}, "ref": 1.0, "proposal": 0.01}, "Ecal": {"prior": {"min": 0.8, "max": 1.2}, "ref": 1.0, "proposal": 0.01}})
ALENS = {"Alens": {"prior": {"min": 0.5, "max": 1.5}, "ref": {"dist": "norm", "loc": 1.0, "scale": 0.03}, "proposal": 0.03}}
W0WA = {"w": {"prior": {"min": -3, "max": 1}, "ref": -1.0, "proposal": 0.05}, "wa": {"prior": {"min": -3, "max": 2}, "ref": 0.0, "proposal": 0.1}}
PEER = {"fde_zc": {"prior": {"min": 0.0005, "max": 0.18}, "ref": {"dist": "norm", "loc": 0.03, "scale": 0.005}, "proposal": 0.005},
        }
PEER_EA = dict(n=3.0, use_zc=True, zc=10 ** 3.56, theta_i=2.89155, m=8e-53, f=0.25)
MODELS = {"LCDM": {}, "LCDM_Alens": ALENS, "w0waCDM": W0WA, "PEER1P": PEER, "PEER1P_Alens": {**PEER, **ALENS}}
for name, extra in MODELS.items():
    ea = dict(EXTRA)
    if "w" in extra: ea.update(dark_energy_model="ppf")
    if "fde_zc" in extra: ea.update(dark_energy_model="EarlyQuintessence", **PEER_EA)
    theory = {"camb": {"extra_args": ea}}
    if not plik_only: theory["mflike.BandpowerForeground"] = {"experiments": ["dr6_pa4_f220", "dr6_pa5_f090", "dr6_pa5_f150", "dr6_pa6_f090", "dr6_pa6_f150"], "bandint_freqs": [220, 90, 150, 90, 150], "beam_profile": {"beam_from_file": None}}
    info = {"theory": theory, "likelihood": LIK, "params": {**BASE, **extra}, "sampler": {"mcmc": {"Rminus1_stop": 0.01, "Rminus1_cl_stop": 0.05, "max_samples": 200000, "max_tries": 100000, "learn_proposal": True, "burn_in": 0}},
            "output": os.path.join(out, "chains", name + ("_plik" if plik_only else "")), "resume": True, "packages_path": os.environ.get("COBAYA_PACKAGES_PATH", "packages")}
    yaml.safe_dump(info, open(os.path.join(out, name + ("_plik" if plik_only else "") + ".yaml"), "w"), sort_keys=False)
print("ok", list(MODELS))
