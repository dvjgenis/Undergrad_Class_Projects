1. Project Overview
You have been hired as an independent Algorithmic Accountability Auditor by a fictional
regulatory body called the U.S. Commission on Algorithmic Transparency (USCAT). Your job is
to investigate a real-world AI/ML application domain, audit a predictive model built on publicly
available data for bias and fairness violations, evaluate its explainability, map your findings to
existing and emerging regulations, and deliver a professional audit report with actionable
governance recommendations.
This is not a hypothetical exercise. You will write real code, produce real metrics, generate real
explanations of model behavior, and ground your policy analysis in actual legal and regulatory
texts. Your final deliverable is a comprehensive audit report that could credibly be submitted to a
regulatory oversight body.
2. Why This Project Matters
Across healthcare, criminal justice, hiring, finance, and education, algorithmic systems make
decisions that affect millions of lives. Yet most of these systems have never been independently
audited. The EU AI Act, GDPR Article 22, the proposed U.S. Algorithmic Accountability Act, and
state-level regulations like the Illinois AI Video Interview Act are creating a new professional
role: the algorithmic auditor. This project prepares you to fill that role.
This project brings together three pillars of the course: technical fairness evaluation, model
explainability, and regulatory/policy analysis. It is designed so that each student's findings will
be unique to the specific choices they make, the dataset they select, and the model they build.
3. Choose Your Investigation Domain
Select one of the following domains for your audit. Each domain comes with suggested publicly
available datasets. You may propose an alternative dataset with instructor approval (email by
April 3, 2026).
Domain Suggested Datasets Key Question Relevant Regulations
Criminal
Justice
COMPAS Recidivism
(ProPublica),
Sentencing Commission
data
Does a recidivism prediction
model treat racial groups
equitably across multiple
fairness metrics?
14th Amendment Equal
Protection, proposed
Algorithmic Accountability
Act, state-level AI criminal
justice laws
IS 467 - Final Capstone Project | Spring 2026
Page 3
Healthcare MIMIC-III (PhysioNet),
Diabetes 130-Hospital
dataset (UCI)
Do clinical prediction models
systematically under-predict
risk for certain demographic
groups?
HIPAA, ACA anti-
discrimination provisions,
FDA AI/ML guidance
Hiring &
Employment
Adult Income (UCI),
EEOC charge statistics,
IBM HR Analytics
(Kaggle)
Can a model predicting
income or attrition reproduce
systemic employment
disparities, and what
features drive this?
Title VII, EEOC Guidance
on AI, Illinois AI Video
Interview Act, NYC Local
Law 144
Consumer
Finance
HMDA data, German
Credit (UCI), Lending
Club (Kaggle)
Does a lending model
exhibit disparate impact
across protected classes,
and can denied applicants
receive meaningful
explanations?
Equal Credit Opportunity
Act, Fair Housing Act,
CFPB AI guidance, EU AI
Act
Education Student Performance
(UCI), OULAD (Open
University Learning
Analytics)
Do early-warning dropout
prediction models
disadvantage students from
specific socioeconomic or
demographic backgrounds?
FERPA, Title IX, emerging
K-12 AI guidelines,
UNESCO AI in Education
framework
4. The Investigation: What You Must Do
Your audit has four phases. Each phase builds on the previous one. You cannot skip phases or
complete them out of order. Your Phase 3 analysis will be shaped by what you discover in
Phases 1 and 2, so the work has to happen in sequence.
Phase 1: Build and Baseline Your Model
In this phase, you construct the system you will be auditing. Think of this as building the "black
box" before you open it.
1. Select your domain and dataset. Document your rationale for choosing this domain. Why
does it matter? Who is affected by algorithmic decisions in this space?
2. Perform exploratory data analysis (EDA). Examine the dataset for demographic
distributions, class imbalances, missing data patterns, and potential proxy variables.
Produce at least 3 meaningful visualizations with written interpretations.
3. Train a binary classification model. You may use logistic regression, random forest,
gradient boosting, or a neural network. Document your preprocessing steps, feature
selection rationale, and train/test split strategy.
IS 467 - Final Capstone Project | Spring 2026
Page 4
4. Report baseline performance metrics: accuracy, precision, recall, F1-score, and AUC-
ROC. Present these both overall and disaggregated by at least one protected attribute
(e.g., race, gender, age group).
Before moving to Phase 2: Write a one-paragraph prediction about where you think bias will
appear in your model and why. You will revisit this prediction later to compare it against your
actual findings. This step is about building honest self-awareness in your own audit process.
Phase 2: Fairness Audit and Explainability Analysis
This is the heart of your investigation. You are now the auditor examining the model you built.
Fairness Analysis
1. Compute and compare at least three fairness metrics across protected groups. Required
metrics: demographic parity (statistical parity), equalized odds (or equality of
opportunity), and predictive parity. You may add calibration or individual fairness metrics
for additional depth.
2. Show and explain how your chosen metrics conflict with each other on your specific
data. Which metric would you prioritize and why? Connect your choice to at least one
ethical framework covered in class (Utilitarianism, deontology, virtue ethics, or fair
ethics). You must show the mathematical tension using your own model's output, not
hypothetical numbers.
Explainability Analysis
1. Apply SHAP (or LIME) to generate global feature importance explanations. Identify the
top 5 features driving predictions and discuss whether any are proxies for protected
attributes.
2. The Recourse Test: For at least one unfavorable prediction, determine what would need
to change for the individual to receive a favorable outcome. Are those changes
actionable? Is this explanation something a non-technical person could understand and
act on? Assess this against GDPR Article 22's right to explanation.
Discovery Checkpoint: Revisit your Phase 1 prediction. Were you right about where bias
appeared? What surprised you? Write an honest 200-word reflection. This reflection is graded
for intellectual honesty, not for whether your prediction was correct.
Phase 3: Regulatory and Policy Mapping
IS 467 - Final Capstone Project | Spring 2026
Page 5
You now have concrete evidence of how your model behaves. In this phase, you map your
technical findings to the legal and regulatory landscape.
1. Identify and analyze at least three specific regulations, laws, or guidelines relevant to
your domain. At least one must be international (such as GDPR or the EU AI Act), and at
least one must be U.S. federal or state-level. For each regulation, cite the specific
articles or sections that apply to your findings.
2. Compliance Gap Analysis: Create a structured table mapping each of your Phase 2
findings to specific regulatory requirements. For each mapping, state whether your
model would be compliant, non-compliant, or in a gray area, and explain why. This table
is a required deliverable.
3. Regulatory Comparison: Pick one specific finding from your audit (for example, a
fairness violation or an explainability gap) and compare how the GDPR, a U.S.
regulation, and one other jurisdiction's framework would each treat it. Where do they
agree? Where do they diverge? What falls through the cracks?
Phase 4: Responsible AI Governance Framework
Based on everything you have found, propose a governance framework for the responsible
deployment of AI in your chosen domain. This is not generic advice. It must be grounded in your
specific findings.
1. Pre-Deployment Checklist: Design a concrete, actionable checklist (minimum 10 items)
that an organization in your domain should complete before deploying a predictive
model. Each item must reference a specific finding from your audit or a specific
regulatory requirement.
2. Stakeholder Communication Template: Draft a one-page plain-language disclosure
document (aimed at affected individuals) that explains what the model does, what data it
uses, how it was tested for fairness, and how to contest a decision. This must be
understandable by someone without any technical background.
5. Submission Requirements
Submit everything as a single PDF file through the canvas platform. Your submission should
contain the following sections in order:
Section What to Include Length / Notes
Audit Report All four phases, written in order, with
clear section headings
4,000 to 6,000 words (excluding
code, tables, and appendices)
IS 467 - Final Capstone Project | Spring 2026
Page 6
Code Appendix All Python code included as an
appendix at the end of the PDF. Code
must be fully commented and
reproducible. Also submit your .ipynb
or .py file separately.
Include a requirements.txt or list
of libraries used
Compliance Gap Table Embedded in Phase 3 of the report Minimum 10 rows
Stakeholder Disclosure
Document
Included as a separate section within
the PDF (Phase 4)
1 page maximum
Submission format: One single PDF file containing your entire audit report, compliance gap
table, stakeholder disclosure document, and code appendix. Additionally, submit your Jupyter
Notebook (.ipynb) or Python script (.py) as a separate file.
6. Grading Rubric (50 Points Total)
Criterion Points What Distinguishes Excellent Work
Phase 1: Model and
EDA
10 Thoughtful dataset selection rationale; visualizations reveal non-
obvious patterns; disaggregated metrics show genuine
investigation, not just running default code
Phase 2: Fairness
Audit
12 Shows metric conflicts on own data with specific numbers; ethical
framework connection is substantive, not superficial; trade-offs are
honestly reported
Phase 2:
Explainability
8 Proxy variable analysis goes beyond the obvious; recourse test
shows genuine thought about the affected individual's perspective
Phase 3: Regulatory
Mapping
10 Cites specific articles and sections (not just regulation names);
compliance gap table is precise and well-reasoned; regulatory
comparison reveals genuine insight
Phase 4:
Governance
Framework
5 Pre-deployment checklist is specific and actionable (not generic AI
ethics platitudes); stakeholder document is genuinely readable by
a non-expert
Discovery
Reflections
2 Intellectually honest; shows that findings challenged or confirmed
assumptions with specific evidence
Code Quality 3 Code is reproducible, well-commented, and produces the exact
numbers cited in the report
7. AI Tool Policy
IS 467 - Final Capstone Project | Spring 2026
Page 7
This project is designed so that each student's investigation produces unique numerical results,
unique fairness findings, and unique regulatory mappings based on the specific modeling
choices they make. Generic text will be identifiable because it will not match your code outputs.
LLM Use for Coding
You are allowed to use large language models to help with the coding portions of this project.
This includes debugging, writing helper functions, understanding library documentation, and
generating boilerplate code. If you use an LLM for coding, disclose which tool you used and
how.
Analysis and Report Writing
For all written analysis, interpretation, and the audit report itself, follow the University of Illinois
academic integrity policy and the course AI use policy as stated in the syllabus. The analysis
must reflect your own reasoning and your own interpretation of what the data shows. Your
writing must be your own.
Not Permitted
• Generating any section of the audit report text
• Having an AI produce your fairness analysis, SHAP explanations, or compliance table
• Submitting AI-generated policy memos or stakeholder documents
• Using AI to fabricate or approximate numerical results instead of running code
Verification
Your code must be runnable and reproduce the exact numbers cited in your report. Random
spot-checks of code and report consistency may be performed. You may be asked to explain
any specific metric, code choice, or regulatory interpretation.
8. Suggested Tools and Resources
Technical
• Python with scikit-learn, pandas, matplotlib/seaborn for modeling and EDA
• SHAP (shap library) or LIME (lime library) for model explainability
• Jupyter Notebook for code documentation and reproducibility
IS 467 - Final Capstone Project | Spring 2026
Page 8
Regulatory Research
• EUR-Lex for GDPR and EU AI Act full text (https://eur-lex.europa.eu)
• Congress.gov for U.S. federal bills and proposed legislation
• State legislature websites for state-level AI laws
• NIST AI Risk Management Framework (https://www.nist.gov/artificial-intelligence)
• Course recommended textbooks, especially Kearns & Roth and Coeckelbergh
Datasets
• UCI Machine Learning Repository (https://archive.ics.uci.edu)
• ProPublica COMPAS data (https://github.com/propublica/compas-analysis)
• PhysioNet for MIMIC-III (requires credentialing; start early if choosing healthcare)
• Kaggle for supplementary datasets
• HMDA data (https://ffiec.cfpb.gov/data-publication)
9. Getting Help
The TAs and I are here to support you throughout this project. Do not hesitate to reach out if
you are stuck, unsure about your approach, or need guidance on any phase.
• Office hours are available by appointment with Dr. Tibebu (htibebu@illinois.edu) and all
TAs.
• Optional lab sessions are available on a first-come, first-served basis at Room 5152, 614
E. Daniel St.
• There will be one dedicated help session before the submission deadline. The date and
time will be announced on Canvas.
• You can also email the instructor or your assigned TA at any point during the project.
10. Important Reminders
• Start early. If you are choosing the MIMIC-III dataset (healthcare), you need to complete
PhysioNet credentialing, which can take 1 to 2 weeks.
• The compliance gap table in Phase 3 is a required, separately graded component. Do
not treat it as optional.
• Your code must be reproducible. Include a requirements.txt or environment specification.
If the grader cannot run your notebook, points will be deducted.
IS 467 - Final Capstone Project | Spring 2026
Page 9
• Late policy: Per the course syllabus
Good luck with your investigation. I look forward to reading what you discover.
