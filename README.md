# MCMC nativo CMB-only (Planck + ACT DR6 + SPT-3G lite)

Cinco modelos, quatro cadeias independentes cada (CAMB 1.6.6 real em cada amostra, Cobaya 3.6.2):
`LCDM`, `LCDM_Alens`, `w0waCDM`, `PEER1P` (EarlyQuintessence n=3, log10 zc=3.56, θi=2.89155, `fde_zc` livre), `PEER1P_Alens`.

* `.github/workflows/mcmc.yml`: roda a cada 6 h (e sob demanda). Cada execução retoma dos checkpoints no branch `mcmc-checkpoints`, roda até ~5h40 e comita os arquivos de cadeia de volta.
* `scripts/make_native_yaml.py`, `gen_yaml.py`: geram os YAMLs (a mesma config foi validada só com Planck contra o pipeline linearizado; veja o paper/pacote de origem). `scripts/aggregate.py`: R−1 dividido, ESS aproximado e médias por modelo → `summary/` no branch de checkpoints e no resumo do job.
* Critério de parada: R−1 < 0.01 e R−1(cl) < 0.05 por cadeia; a convergência entre cadeias é avaliada pelo agregador (cadeias são independentes, não MPI).
* O PEER1P+w0wa não tem config nativa (o CAMB 1.6.6 não combina `EarlyQuintessence` com w0wa).
* Limitações: foregrounds do ACT amostrados; SPT-3G na versão lite; precisão CAMB do pipeline (lens_potential_accuracy=1).
