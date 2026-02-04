---
layout: post
title: "White Box vs. Black Box Models: The Trade-off Between Explainability and Performance"
excerpt: "In biomedical and clinical research, interpretability matters: black box vs white box models, why Random Forest and similar methods are often preferred over deep learning, and how this applies to lab work with physiological signals."
categories:
  - "Machine Learning & Statistical Modeling"
order: 1
tags:
  - Interpretability
  - Random Forest
  - Research
  - Black Box
  - White Box
  - Clinical ML
---

In many research settings—especially biomedical and clinical—**interpretable** machine learning models (e.g. **Random Forest**, decision trees, logistic regression) are often preferred over **neural networks**. This post explains the **black box vs white box** distinction, why interpretability matters in research, and how this choice shows up in lab work such as physiological signal analysis.

---

## 1. Black box vs white box

### Black box

A **black box** model is one whose internal logic is hard or impossible to explain in human terms. You see inputs and outputs, but you cannot easily say *why* the model made a given prediction.

- **Examples:** Deep neural networks (many layers, thousands or millions of parameters), complex ensembles when used without interpretability tools.
- **Why it is “black”:** The decision is a result of many non-linear transformations; there is no simple rule like “if X > 5 then Y”. Explaining *which* input features drove the prediction requires extra methods (SHAP, attention, etc.), and even then the story is often approximate.

### White box (interpretable)

A **white box** model is one whose behaviour can be understood and explained: which variables matter, in what direction, and sometimes in the form of explicit rules.

- **Examples:** Linear/logistic regression (coefficients show effect of each feature), decision trees (if–then rules), Random Forest (feature importances, tree structure), gradient boosting with feature importance.
- **Why it is “white”:** You can inspect coefficients, splits, or feature importances and report them in a paper or to a clinician: “age and blood pressure were the strongest predictors.”

In research, especially when results must be communicated to clinicians or regulators, **white box** (or at least “grey box”) models are often chosen so that the *why* is as important as the *how well*.

---

## 2. Why interpretability matters in research

In biomedical and clinical research, the goal is often not only to predict well but to **understand** and **publish**:

- **Clinicians** need to trust and interpret the model: which variables drive the prediction? Does it align with medical knowledge?
- **Regulators and ethics** may require some form of explainability, especially when the model supports decisions that affect patients.
- **Scientific papers** need to report which factors matter; “the model works well” is not enough—you need to say *what* the model learned (e.g. feature importances, key variables).
- **Small or costly data:** In many clinical settings, sample sizes are limited. Interpretable models (Random Forest, logistic regression) often generalise reasonably with less data and are less prone to overfitting than large neural networks when data is scarce.

So in research, **interpretability** (white box or grey box) is often a requirement, not a nice-to-have. That favours models like Random Forest, XGBoost (with feature importance), or logistic regression over deep neural networks when the problem allows it.

---

## 3. When neural networks are used anyway

Neural networks are used in research when:

- The **input** is high-dimensional and unstructured (images, raw signals, text) and hand-crafted features are hard or insufficient; deep learning can learn representations.
- **Performance** is the main criterion and interpretability is secondary (e.g. some screening or auxiliary tools).
- There is **enough data** and compute, and the team adds **post-hoc interpretability** (SHAP, attention, saliency maps) to satisfy reviewers.

So it is not “research = no neural networks”; it is “research often prefers interpretable models when the problem and data allow it.” For **tabular** or **engineered-feature** settings (e.g. physiological features from wearables), Random Forest and similar models are a natural fit and easier to justify in a paper.

---

## 4. How this applies to my lab work

In my **research fellowship** at the **LEICI Institute** (UNLP) in collaboration with the **Italian Hospital of Buenos Aires (HIBA)**, we work with **physiological signals** from wearable sensors and continuous glucose monitors (CGM) to detect and classify physiological states in individuals with Type 1 Diabetes. The pipeline includes signal processing, feature extraction, and **machine learning** for classification.

We use **Random Forest** (and related interpretable methods) in this project because:

- **Interpretability:** Clinicians and collaborators need to understand *which* physiological features (e.g. heart rate variability, glucose trends, activity) drive the predictions. Feature importances and tree-based logic support that.
- **Data size:** Clinical cohorts are often limited; Random Forest tends to generalise well with moderate sample sizes and is less data-hungry than deep networks.
- **Publishability:** In medical and engineering journals, reporting “top predictors” and “feature importance” is standard; a white-box or grey-box model makes that straightforward.

So the choice of **Random Forest** instead of a neural network here is deliberate: we prioritise **interpretability and explainability** for a clinical research context. For more on the project (architecture, signal processing, ML pipeline), see [Physiological Signal Analysis Research](/projects/research-lab.html).

I have also used **Random Forest, XGBoost, and logistic regression** in other projects, for example [Heart Disease Prediction](/projects/heart-disease.html), where the goal is again to identify risk factors and build interpretable predictive models from tabular clinical and lifestyle variables.

---

## 5. Summary table

| Aspect | Black box (e.g. deep neural nets) | White box / interpretable (e.g. Random Forest, logistic regression) |
|--------|-----------------------------------|----------------------------------------------------------------------|
| **Interpretability** | Hard to explain *why* a prediction was made. | Coefficients, feature importances, or rules can be reported. |
| **Typical use in research** | When inputs are unstructured (images, raw signals) or when performance is paramount and explainability is added post hoc. | When the problem is tabular or feature-based and clinicians/reviewers need to understand which variables matter. |
| **Data** | Often needs large datasets. | Can work well with moderate sample sizes. |
| **Research / clinical** | Used when necessary; explainability via SHAP, attention, etc. | Often preferred in biomedical/clinical papers and collaborations. |

---

This post summarised **black box vs white box** models and why research—especially in biomedical and clinical settings—often favours **interpretable ML** (e.g. Random Forest) over neural networks when the problem allows it. In my [lab project](/projects/research-lab.html) (LEICI–HIBA, physiological signals), we use Random Forest for exactly these reasons: interpretability, moderate data, and the need to report which physiological features drive the predictions.
