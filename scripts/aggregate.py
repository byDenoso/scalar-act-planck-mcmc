"""Agrega as cadeias de ckpt/chains/<modelo>_c*/chain.1.txt: Rhat dividido, ESS aproximado, medias; escreve summary/<modelo>.json e summary/SUMMARY.md."""
import sys, os, glob, json, numpy as np
root = sys.argv[1] if len(sys.argv) > 1 else "ckpt"; os.makedirs(f"{root}/summary", exist_ok=True)
def load(p):
    with open(p) as f: hdr = f.readline().lstrip("# ").split()
    a = np.loadtxt(p, comments="#"); return hdr, a
def rhat(chs):
    n = min(len(c) for c in chs); x = np.array([c[:n] for c in chs]); m, nn = x.shape[0], x.shape[1]
    if nn < 20: return float("nan")
    W = x.var(axis=1, ddof=1).mean(); B = nn * x.mean(axis=1).var(ddof=1); return float(np.sqrt(((nn - 1) / nn * W + B / nn) / W))
def ess(x):
    x = x - x.mean(); n = len(x); f = np.fft.rfft(x, 2 * n); ac = np.fft.irfft(f * np.conj(f))[:n]; ac /= ac[0]
    s = 1.0
    for k in range(1, n):
        if ac[k] < 0.05: break
        s += 2 * ac[k]
    return n / s
out = []
for mdir in sorted(set(os.path.basename(d).rsplit("_c", 1)[0] for d in glob.glob(f"{root}/chains/*_c*"))):
    chains = []
    for d in sorted(glob.glob(f"{root}/chains/{mdir}_c*")):
        fs = sorted(glob.glob(d + "/chain*.txt"))
        if not fs: continue
        hdr, a = load(fs[0]); a = np.repeat(a, np.maximum(a[:, 0], 1).astype(int), axis=0); a = a[int(0.3 * len(a)):]  # expande pesos, burn 30%
        if len(a) > 5: chains.append((hdr, a))
    if len(chains) < 2: out.append(f"| {mdir} | {len(chains)} | — | — | — |"); continue
    hdr = chains[0][0]; w = hdr.index("weight") if "weight" in hdr else 0; res = {"n_chains": len(chains), "samples": [int(len(a)) for _, a in chains], "params": {}}
    best = min(a[:, hdr.index("minuslogpost")].min() for _, a in chains) if "minuslogpost" in hdr else float("nan")
    for p in hdr:
        if p in ("weight", "minuslogpost", "minuslogprior", "chi2") or p.startswith("chi2__") or p.startswith("minuslogprior__"): continue
        j = hdr.index(p); col = [a[:, j] for _, a in chains]
        if np.std(np.concatenate(col)) < 1e-12: continue
        res["params"][p] = {"mean": float(np.mean(np.concatenate(col))), "sd": float(np.std(np.concatenate(col))), "rhat": rhat(col), "ess": float(sum(ess(c) for c in col))}
    res["best_minuslogpost"] = float(best); json.dump(res, open(f"{root}/summary/{mdir}.json", "w"), indent=1)
    key = [p for p in ("H0", "fde_zc", "Alens", "w", "wa") if p in res["params"]]
    COSMO = ("H0", "ombh2", "omch2", "logA", "ns", "tau", "fde_zc", "Alens", "w", "wa")
    mr = max((res["params"][k]["rhat"] for k in COSMO if k in res["params"] and np.isfinite(res["params"][k]["rhat"])), default=float("nan"))
    ma = max((v["rhat"] for v in res["params"].values() if np.isfinite(v["rhat"])), default=float("nan"))
    res["max_Rm1_cosmo"] = float(mr - 1); res["max_Rm1_all"] = float(ma - 1); json.dump(res, open(f"{root}/summary/{mdir}.json", "w"), indent=1)
    out.append(f"| {mdir} | {len(chains)} | {sum(res['samples'])} | {mr - 1:.3f} (todos: {ma - 1:.2f}) | " + "; ".join(f"{k}={res['params'][k]['mean']:.4g}±{res['params'][k]['sd']:.2g}" for k in key) + " |")
open(f"{root}/summary/SUMMARY.md", "w").write("| modelo | cadeias | amostras (pós-burn) | max R−1 cosmologia (todos os parâmetros) | parâmetros-chave |\n|---|---|---|---|---|\n" + "\n".join(out) + "\n")
print(open(f"{root}/summary/SUMMARY.md").read())
