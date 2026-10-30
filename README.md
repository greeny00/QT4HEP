# QT4HEP — Quantum Data Encoding for CMS Jets

Zeynep Sağlam · İstanbul Teknik Üniversitesi, Fizik Mühendisliği
Danışman: Altan Çakır

CERN QT4HEP posteri (24 Kasım 2026) ve yüksek lisans tezi için çalışma deposu.
Rekonstrükte CMS jetlerinde (pT, η, ϕ, m) Angle ve Amplitude encoding karşılaştırması,
L2 normalizasyonunun yol açtığı "state collapse" ve fizik güdümlü encoding stratejileri.

## Klasör yapısı

| Klasör | İçerik |
| --- | --- |
| `Data/` | Ham veri (Git'e girmez) |
| `src/` | Yeniden kullanılabilir Python kodu (veri okuma, encoding, metrikler) |
| `notebooks/` | Keşif ve figür notebook'ları |
| `figures/` | Poster ve tez figürleri |
| `notes/` | Araştırma günlüğü, sürüm kaydı |
| `docs/` | Özet, poster taslakları |
| `references.bib` | Kaynakça (BibTeX) |

## Kurulum

```bash
conda env create -f environment.yml
conda activate qt4hep
```

## Veri

CMS Open Data, record 12100 — DOI: 10.7483/OPENDATA.CMS.RY2V.T797

```bash
cd Data
cernopendata-client download-files --recid 12100 --filter-name JetNtuple_RunIISummer16_13TeV_MC_1.h5
mv 12100/JetNtuple_RunIISummer16_13TeV_MC_1.h5 . && rmdir 12100
```
