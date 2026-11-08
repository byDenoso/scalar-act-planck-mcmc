"""gen_yaml.py <modelo> <cadeia> <dir_pacotes> <dir_spt> -> escreve run/<modelo>_c<cadeia>.yaml (saida: chains/<modelo>_c<cadeia>/chain)."""
import sys, os, yaml, subprocess
model, chain, pk, spt = sys.argv[1:5]
os.makedirs("run", exist_ok=True)
tmp = "run/_gen"; os.environ["NEXO_DIR"] = "."
subprocess.run([sys.executable, "scripts/make_native_yaml.py", tmp], check=True, env={**os.environ, "COBAYA_PACKAGES_PATH": pk})
info = yaml.safe_load(open(f"{tmp}/{model}.yaml"))
info["likelihood"]["spt3g_lite"]["data_set_file"] = os.path.join(spt, "SPT3G_D1_TnE_v0/lite/SPT3G_D1_TnE_lite.yaml")
info["output"] = f"chains/{model}_c{chain}/chain"; info["packages_path"] = pk; info["resume"] = True
info["sampler"]["mcmc"].update(Rminus1_stop=0.01, Rminus1_cl_stop=0.05, max_samples=200000)
os.makedirs(os.path.dirname(info["output"]), exist_ok=True)
yaml.safe_dump(info, open(f"run/{model}_c{chain}.yaml", "w"), sort_keys=False)
print("ok", f"run/{model}_c{chain}.yaml")
