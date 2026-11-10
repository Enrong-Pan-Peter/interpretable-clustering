# Data plan — public cancer expression data

**Date.** 2026-08-05. From Ting's suggestion in the reframe meeting. **Nothing has been built yet;
this is the acquisition and design note only.**

---

## 1. Why this dataset class, and what it fixes

Every dataset we have used — the six synthetic shapes, Mice Protein Expression, UCI HAR — has labels
but **no published feature panel**. That has capped the whole project: we can score whether the
*clustering* is right, never whether the *selection* is right, on real data. It is the caveat at the
bottom of exp-019 and one of the four questions taken to Ting.

Breast cancer expression data closes it. **PAM50** (Parker et al., J Clin Oncol 2009) is a published
50-gene panel for the intrinsic molecular subtypes. That gives, for the first time, a real dataset
where "did the method name the right genes?" has an answer somebody else wrote down and we did not.

It also supplies the interpretability figure the paper needs. "This split separated patients on
ERBB2 and GRB7" is a sentence an oncologist can evaluate. Named genes are the point.

---

## 2. Which data to get

### First choice — METABRIC, via cBioPortal

Confirmed present: study id **`brca_metabric`**, "Breast Cancer (METABRIC, Nature 2012 &
Nat Commun 2016)", **2,509 samples** (cBioPortal API, checked 2026-08-05). Citations: Curtis et al.
Nature 2012, Pereira et al. Nat Commun 2016, Rueda et al. Nature 2019.

Why this one first: roughly twice the patients of TCGA-BRCA, and the clinical file carries both the
PAM50 calls and the Claudin-low call, which gives a second contrast for free.

**Where to get it — two routes, use whichever works:**

1. **Datasets page (reliable route).** <https://www.cbioportal.org/datasets> → find "Breast Cancer
   (METABRIC, Nature 2012 & Nat Commun 2016)" → click the download icon on that row. This gives a
   `.tar.gz` of the whole study.
2. **Study page.** <https://www.cbioportal.org/study/summary?id=brca_metabric> has the same download.

The direct link is usually `https://cbioportal-datahub.s3.amazonaws.com/brca_metabric.tar.gz`. I
could not verify that URL from here (the bucket refuses listing), so if it 403s, use route 1 rather
than guessing at variants.

**What you need out of the tarball** — filenames have changed across cBioPortal releases, so match
on the prefix rather than the exact name:

| what | file to look for |
|---|---|
| expression matrix | `data_mrna_illumina_microarray.txt`, or on older releases `data_expression_median.txt` — genes × samples, gene symbols in column 1 |
| subtype labels | `data_clinical_patient.txt` — the PAM50 + Claudin-low call is usually a column named `CLAUDIN_SUBTYPE` or similar |
| sample-level clinical | `data_clinical_sample.txt` |

Put the extracted folder under `data/uci/raw/` alongside the others, or make a sibling
`data/cancer/raw/` — either is fine, just tell me which so the loader points at the right place.

### Second choice / cross-check — TCGA-BRCA

~1,100 patients, RNA-seq, fully open with no application. Two routes:

- **UCSC Xena**, <https://xenabrowser.net/datapages/> → TCGA Breast Cancer (BRCA) cohort → the gene
  expression RNAseq dataset plus the phenotype dataset. Xena is a JavaScript app so I could not read
  its file listing from here; you will need to pick the files on the page.
- **cBioPortal**, study id `brca_tcga_pan_can_atlas_2018`, same download route as above.

Worth having eventually as a replication cohort — "the same two genes come up in an independent
cohort" is a strong interpretability claim. Not needed to start.

### The PAM50 gene list itself

Published in Parker et al. 2009. Also shipped in the R package `genefu`, and reproduced in many
GitHub repos. We need the 50 gene symbols as plain text; I can pull them once you decide the source
you want cited.

### Not worth it

The classic small cancer sets — Golub leukemia (72 samples), Alon colon (62), SRBCT (83) — have too
few rows. Our density and graph-cut terms need enough neighbours for the estimates to mean anything,
and 62 rows is below where we would trust them.

---

## 3. Design constraints, decided before any code

These come from our own pipeline and from mistakes we have already made twice.

**Feature count.** ~20,000 genes gives about 200 million pairs. We cannot enumerate. Two options:

- **(a) Preferred.** Take the 50 PAM50 genes as the planted panel and add K randomly chosen
  non-PAM50 genes as distractors. That reproduces our synthetic setup exactly — known answer, known
  junk — but on real data with a real published answer key. K can be swept the way p was.
- **(b) Fallback.** Pre-filter to the few hundred highest-variance genes and sample pairs. Weaker,
  because the answer key becomes fuzzy.

Start with (a).

**Row count.** Subsample to ~600 rows, stratified by subtype, same as mice and HAR. Our scores need
an n×n distance matrix per candidate.

**Which contrast, and this is the decision that determines whether the dataset tests anything.** Our
splitter is binary; PAM50 is five-way (Luminal A, Luminal B, HER2-enriched, Basal-like, Normal-like).

- **Basal vs Luminal** will very likely fail the one-column gate — ESR1 alone is expected to separate
  them. Same failure mode as HAR's moving-vs-still, where a single column reached ARI 1.00 and 205 of
  561 columns reached 0.5, making the dataset unable to distinguish a working selection method from a
  coin flip.
- **Luminal A vs Luminal B** is the one to aim for: clinically real, proliferation-driven, and no
  single gene is expected to solve it. This is the breast-cancer analogue of sitting-vs-standing.
- **HER2-enriched vs Luminal** is a middle case worth measuring.
- **Claudin-low vs Basal** is the free second contrast METABRIC gives us.

**Run the one-column gate first, before scoring anything.** Best single-column ARI, and how many
columns exceed 0.5. It has now caught an unusable dataset twice — jain and spiral on our own
generator, and HAR's moving-vs-still. Do not skip it because the data is prestigious.

**Expect the subtype labels to be themselves derived.** PAM50 calls are produced by a classifier, not
measured. So "our clustering disagrees with PAM50" is a weaker accusation than it sounds, and it is
exactly the case where the meaningful-disagreement evidence from the meeting note §4b applies.

---

## 4. What this buys the paper if it works

- The first **selection**-accuracy number against a published panel, rather than against clustering
  quality standing in for one.
- The interpretability figure: a tree whose splits are named genes.
- A replication claim, if the same genes surface in TCGA-BRCA independently.
- A concrete answer to "would this be useful to a biologist", which is the question the whole
  reframe rests on.

---

## 5. What I need from you

1. **Download `brca_metabric` from cBioPortal** (route 1 above) and extract it.
2. Tell me **where you put it** and **which mRNA file the release actually contains** — the filename
   varies and I would rather match it than guess.
3. Confirm which **PAM50 gene list source** you want cited.

Then I will write the loader and the one-column gate, in that order, and nothing else until the gate
result is in.
