For your Final Capstone Project, you need to apply three core pillars from the course: technical fairness evaluation, model explainability, and regulatory/policy analysis. 

Here are the specific course concepts you must note and apply across the four phases of your project:

**1. Fairness Metrics and the "Impossibility Theorem"**
You must move beyond traditional accuracy (which can be misleading on imbalanced datasets) and apply specific fairness-aware metrics. 
*   **Demographic Parity:** Ensuring equal acceptance rates across different demographic groups.
*   **Equal Opportunity:** Ensuring that truly qualified individuals from all groups succeed at equal rates (focusing on True Positive Rate/Recall).
*   **Predictive Parity:** Ensuring the model's precision is equal across groups.
*   **The Impossibility Theorem:** You must mathematically demonstrate the tension between these metrics. As course concepts show, it is often mathematically impossible to satisfy Demographic Parity and Predictive Parity simultaneously, requiring you to make a trade-off.

**2. Ethical Frameworks for Decision-Making**
When your fairness metrics conflict, you must use an ethical framework to justify which metric you prioritize.
*   **Deontology (Rules-Based):** Strict adherence to moral rules, regardless of the outcome.
*   **Utilitarianism (Consequence-Based):** Maximizing the overall benefit for the greatest number of people.
*   **Justice Ethics:** Focusing on addressing historical oppression and advancing equity, which often aligns with prioritizing Equal Opportunity over mere accuracy.
*   **Virtue Ethics:** Basing decisions on the moral character and responsibility of the developers.

**3. Model Explainability (SHAP & LIME)**
You are required to open the "black box" of your model using explainability tools to understand the reasoning behind its predictions.
*   **Global vs. Local Explanations:** You must use tools like SHAP to understand global feature importance (which features matter most overall) and local explanations (why a specific prediction was made for a specific individual).
*   **Proxy Variables:** You must identify if the model is using seemingly neutral features (like marital status or zip code) as proxies for protected attributes like race or sex.
*   **Actionable Recourse:** You must evaluate a borderline, unfavorable prediction to see if the explanation provides the user with realistic, actionable steps to change their outcome. 

**4. Regulatory and Policy Mapping**
You must map your technical findings (like fairness gaps and explainability flaws) directly to legal frameworks. Key regulations to apply include:
*   **GDPR (Article 22 & 15):** The right to meaningful information about the logic involved in automated decision-making, and the right to human intervention/recourse.
*   **Title VII of the Civil Rights Act & EEOC Guidelines:** U.S. federal laws prohibiting employment discrimination and utilizing the "four-fifths rule" to measure adverse impact.
*   **EU AI Act & Local Laws:** Regulations classifying certain AI (like hiring or credit tools) as "high-risk" and mandating transparency, post-market monitoring, and independent bias audits (e.g., NYC Local Law 144).

**5. Bias Mitigation and AI Governance**
Finally, you must apply concepts of algorithmic governance to propose solutions.
*   **Mitigation Stages:** Understanding whether to fix the bias via **Pre-processing** (re-weighting training data), **In-processing** (changing the model's objective function), or **Post-processing** (manually correcting the final scores).
*   **NIST AI Risk Management Framework (RMF):** Using established guidelines (Govern, Map, Measure, Manage) to create a pre-deployment checklist.
*   **Stakeholder Transparency:** Translating complex algorithmic mechanics into plain-language disclosures that non-technical users can understand.