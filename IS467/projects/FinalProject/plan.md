# IS 467 Final Capstone — Working Plan

This document summarizes requirements drawn from course materials indexed in the NotebookLM notebook **IS 467** (Algorithmic Accountability capstone). Confirm exact due dates on **Canvas** if sources disagree.

## Project title and framing

**The Algorithmic Accountability Investigation: Auditing AI Systems for Bias, Transparency, and Regulatory Compliance**

- **Weight:** 50% of final grade (individual).
- **Role:** You act as an auditor for the fictional **U.S. Commission on Algorithmic Transparency (USCAT)**.

## Deadlines (verify on Canvas)

| Source | What | When |
|--------|------|------|
| Syllabus | Final submission | Wednesday, May 6, 2026, 11:59 PM CT |
| Capstone assignment PDF | Project due | Monday, May 4, 2026, 11:59 PM CT |
| Capstone slide deck | Slides due | Monday, April 27, 2026, 11:59 PM CT |

Alternative datasets may require instructor approval by dates stated in those documents (e.g. before slide and final deadlines).

## Deliverables

Submit via **Canvas**:

1. **One PDF** containing, in order:
   - **Audit report** — all **four phases** with clear section headings.
   - **Word count:** 4,000–6,000 words (excluding code, tables, and appendices).
   - **Compliance gap table** — embedded in **Phase 3** (minimum **10 rows**).
   - **Stakeholder disclosure** — part of **Phase 4** (maximum **1 page**).
   - **Code appendix** — at the very end; fully commented, reproducible; include **`requirements.txt`** or an explicit list of libraries.

2. **Separate code file** — Jupyter Notebook (`.ipynb`) or Python script (`.py`).

## Dataset choice: Adult Census Income (UCI)

This project uses the **Adult / Census Income** dataset under the **Hiring & Employment** domain (UCI Machine Learning Repository). The prediction task is binary: income **>50K** vs **<=50K** per person record.

Processed copy for analysis: `data/adult_census_income.csv` (includes `dataset_split`: `train` | `test` for the canonical UCI split).

## Phase 1 — Build and baseline your model

- Rationale for domain and dataset.
- **EDA:** demographics, class imbalance, missing data, proxy variables; **at least 3 meaningful visualizations** with interpretation.
- **Model:** binary classifier (e.g. logistic regression, random forest, gradient boosting, or neural network); document preprocessing, feature selection, **train/test split**.
- **Metrics:** overall and **disaggregated** (by at least one protected attribute): accuracy, precision, recall, F1, AUC-ROC.
- **Before Phase 2:** one paragraph predicting **where bias may appear** and why.

## Phase 2 — Fairness audit and explainability

- **Fairness:** compute **at least 3** fairness metrics across protected groups; must include **demographic parity**, **equalized odds** (equality of opportunity), and **predictive parity**. Show how metrics **conflict** on your data; **prioritize one** and justify using an **ethical framework** (e.g. utilitarianism, deontology, virtue ethics, or fair ethics).
- **Explainability:** **SHAP** or **LIME** — global feature importance; **top 5** driving features and **proxy** discussion.
- **Recourse test:** at least one unfavorable prediction — actionable changes for a favorable outcome; relate to **GDPR Article 22**.
- **Discovery checkpoint:** ~**200 words** comparing your Phase 1 bias prediction to actual findings.

## Phase 3 — Regulatory and policy mapping

- **At least three** specific regulations/laws relevant to the domain, including **one international** (e.g. GDPR / EU AI Act) and **one U.S. federal or state**; cite **specific articles/sections**.
- **Compliance gap analysis:** table mapping Phase 2 findings to requirements (compliant / non-compliant / gray area).
- **Regulatory comparison:** one audit finding compared across **GDPR**, a **U.S.** rule, and a **third jurisdiction**.

## Phase 4 — Responsible AI governance

- **Pre-deployment checklist:** **at least 10** concrete items tied to your audit or regulations.
- **Stakeholder communication:** **1-page** plain-language disclosure (model, data, fairness testing, how to contest).

## Grading rubric (50 points)

| Component | Points |
|-----------|--------|
| Phase 1: model and EDA | 10 |
| Phase 2: fairness audit | 12 |
| Phase 2: explainability | 8 |
| Phase 3: regulatory mapping | 10 |
| Phase 4: governance framework | 5 |
| Discovery reflections | 2 |
| Code quality (reproducible; numbers match report) | 3 |

## Suggested tools

- **Python:** `pandas`, `scikit-learn`, `matplotlib` / `seaborn`; **`shap`** or **`lime`** for explainability; Jupyter for documentation.
- **Regulatory research:** EUR-Lex, Congress.gov, state legislatures, **NIST AI RMF**, etc.

- Graders must be able to run your notebook and reproduce numbers; missing `requirements` or failed runs can cost points.

## Local artifacts

| Path | Purpose |
|------|---------|
| `data/adult_census_income.csv` | Single analysis table with headers + `dataset_split` |
| `scripts/build_adult_csv.py` | Regenerates CSV from `adult/adult.data` and `adult/adult.test` |
| `capstone_analysis.ipynb` | Scaffold for code, EDA, modeling, and later phases |


---

Dear Students,

I would like to clarify a few common questions regarding the final project submission.

Please note that there is no presentation required for this final assignment.

For your exploratory data analysis, the most important insights should be presented and discussed in your written report. Additional or supporting visualizations may remain in your Jupyter Notebook or be in an appendix if desired.

Your final submission should be a single ZIP file that includes:

    -  A PDF of your final report
    -  Your Jupyter Notebook (.ipynb) file
    -  Optional requirements.txt file

Including code in an appendix within your report. However, you must still submit the full notebook file separately, included in the zip file. 

I was also asked whether students are allowed to revise their submissions after submitting. Those of you who have already submitted and need to make changes are allowed to submit a revised version at any time before the deadline.

A requirements.txt file is not mandatory, as long as your notebook clearly includes and runs with the necessary libraries and packages.

For more information, please refer to Section 5, Submission Requirements, in the final project description PDF.

If you have further questions, feel free to reach out.

 

Good luck! 