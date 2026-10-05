QUESTIONS = [
    {
        "stage": "technical",
        "track": "ml",
        "topic": "statistics",
        "difficulty": 1,
        "prompt": "Explain the formal difference between correlation and causation in data analysis. Please structure your response by: 1) Defining both concepts, 2) Identifying how confounding variables interfere, and 3) Providing a concrete practical example demonstrating how a causal design or experiment establishes true causality.",
        "reference": "Correlation measures association between variables, while causation means changing one variable produces a change in the other. Confounding variables can create correlation without causation. A randomized experiment or a sound causal design helps establish causality.",
        "rubric": {"distinction": 0.4, "confounding": 0.3, "experiment": 0.3}
    },
    {
        "stage": "technical",
        "track": "ml",
        "topic": "model evaluation",
        "difficulty": 2,
        "prompt": "You have trained a binary classification model for fraud detection that achieves 99% accuracy on the test set. However, business stakeholders report that major fraud cases are still being missed. How would you evaluate this model's performance beyond accuracy, and what specific steps would you take to optimize it for production?",
        "reference": "Accuracy is misleading with imbalanced classes. Examine the confusion matrix, precision, recall, F1 and PR-AUC. Choose a threshold based on the business cost of false negatives and false positives; use class weights, resampling, or more representative data.",
        "rubric": {"imbalance": 0.2, "metrics": 0.3, "threshold": 0.25, "mitigation": 0.25}
    },
    {
        "stage": "technical",
        "track": "ml",
        "topic": "overfitting",
        "difficulty": 2,
        "prompt": "How do you systematically diagnose model overfitting during model development? Detail the diagnostic indicators you monitor and outline the remedial actions you would implement across data engineering, model selection, and hyperparameter tuning.",
        "reference": "Overfitting appears when training performance is substantially better than validation or test performance. Use a held-out validation set or cross-validation. Reduce model complexity, regularize, add data or augmentation, tune with validation only, and use early stopping where appropriate.",
        "rubric": {"diagnosis": 0.3, "validation": 0.2, "regularization": 0.25, "data_or_complexity": 0.25}
    },
    {
        "stage": "technical",
        "track": "ml",
        "topic": "feature engineering",
        "difficulty": 3,
        "prompt": "When engineering features for a customer churn prediction pipeline, data leakage can corrupt validation results. Explain how you would establish a strict prediction-time cutoff, construct historical feature aggregations, and design a temporal validation strategy to guarantee zero data leakage.",
        "reference": "Start from a prediction time and include only information available before it. Use domain hypotheses, clean missing values, encode categories, aggregate historical windows, and validate with a time-aware split. Leakage is future information or target-derived data and produces unrealistically high validation results.",
        "rubric": {"prediction_time": 0.25, "features": 0.2, "leakage": 0.3, "time_split": 0.25}
    },
    {
        "stage": "technical",
        "track": "analytics",
        "topic": "sql",
        "difficulty": 1,
        "prompt": "In relational data modeling, compare INNER JOIN and LEFT JOIN operations. In your answer, explain row inclusion/exclusion logic, handling of unmatched NULL keys, and how key grain misalignments can cause accidental row multiplication.",
        "reference": "An INNER JOIN returns rows that match in both tables. A LEFT JOIN retains all rows from the left table and gives nulls for unmatched right rows. Join keys and duplicate grain should be checked to avoid row multiplication.",
        "rubric": {"inner": 0.35, "left": 0.35, "nulls": 0.15, "grain": 0.15}
    },
    {
        "stage": "technical",
        "track": "analytics",
        "topic": "experimentation",
        "difficulty": 2,
        "prompt": "As a Data Scientist evaluating an A/B test, what criteria and data quality checks do you perform before declaring a result statistically and practically actionable? Walk through hypothesis pre-registration, sample ratio mismatch (SRM), statistical significance, and guardrail metrics.",
        "reference": "Predefine the hypothesis, primary metric, sample size and duration. Check randomization, sample ratio mismatch and data quality. Interpret effect size with confidence intervals and statistical significance, while considering practical significance and guardrail metrics.",
        "rubric": {"design": 0.25, "quality": 0.2, "uncertainty": 0.3, "practicality": 0.25}
    },
    {
        "stage": "technical",
        "track": "analytics",
        "topic": "metrics",
        "difficulty": 3,
        "prompt": "A critical executive dashboard shows that the user checkout conversion rate dropped by 10% overnight. Walk through your step-by-step diagnostic workflow, detailing data validation, funnel segmentation, statistical confidence checks, and hypothesis testing.",
        "reference": "First validate the metric definition, pipeline and tracking changes. Segment by platform, channel, geography and funnel step; compare cohorts and traffic mix. Identify whether the change is statistically credible, form hypotheses, and connect findings to a product or operational change.",
        "rubric": {"validation": 0.25, "segmentation": 0.3, "statistics": 0.15, "hypotheses": 0.3}
    },
    {
        "stage": "case",
        "track": "ml",
        "topic": "recommendation systems",
        "difficulty": 2,
        "prompt": "A major media streaming platform wants to overhaul content recommendations for newly registered users who have zero watch history. Propose an end-to-end technical strategy addressing the cold-start problem, specifying offline evaluation strategies, online A/B testing setup, and guardrail metrics.",
        "reference": "Use a cold-start strategy combining onboarding preferences, content metadata, popularity or editorial priors, and collaborative signals once available. Offline evaluate ranking with held-out interactions, then A/B test engagement and retention with diversity and satisfaction guardrails.",
        "rubric": {"cold_start": 0.3, "approach": 0.25, "evaluation": 0.25, "guardrails": 0.2}
    },
    {
        "stage": "case",
        "track": "ml",
        "topic": "model deployment",
        "difficulty": 3,
        "prompt": "A machine learning demand-forecasting model achieved high accuracy during offline cross-validation, but post-launch performance degraded significantly. How would you investigate training-serving skew, feature drift, telemetry monitoring, and fallback operational runbooks?",
        "reference": "Compare online inputs and feature definitions with training data, check data quality and training-serving skew, monitor drift and error by segment, and compare against a baseline. Establish alerting, rollback, retraining cadence, and use business feedback to diagnose changing demand.",
        "rubric": {"skew": 0.3, "monitoring": 0.25, "baseline": 0.15, "operations": 0.3}
    },
    {
        "stage": "case",
        "track": "analytics",
        "topic": "product analytics",
        "difficulty": 2,
        "prompt": "An e-commerce platform observes that user account sign-ups are growing rapidly month-over-month, but paid subscription conversions remain flat. How would you structure a product funnel investigation, segment user cohorts, prioritize product interventions, and design experiments to validate solutions?",
        "reference": "Define the conversion funnel and cohort windows, validate tracking, segment acquisition channels and user cohorts, find the largest drop-off, and quantify changes. Form hypotheses, prioritize interventions by impact and effort, and test them with experiments while monitoring retention and revenue.",
        "rubric": {"funnel": 0.25, "validation": 0.15, "segmentation": 0.2, "prioritization": 0.2, "experiments": 0.2}
    },
    {
        "stage": "case",
        "track": "analytics",
        "topic": "forecasting",
        "difficulty": 3,
        "prompt": "A national retail chain requires weekly inventory forecasts across 500 stores. Formulate an end-to-end analytical framework covering problem definition, data aggregation (promotions, holidays, seasonality), model validation (temporal splits & error metrics like MAE/WAPE), and automated monitoring.",
        "reference": "Define forecast horizon and decision cost, assemble sales with promotions, holidays, stockouts and hierarchy, use time-based validation and a baseline, measure errors such as MAE or WAPE by segment, and operationalize forecasts with monitoring and retraining.",
        "rubric": {"framing": 0.2, "data": 0.25, "validation": 0.2, "forecast_metrics": 0.15, "operations": 0.2}
    },
    {
        "stage": "behavioral",
        "track": "all",
        "topic": "communication",
        "difficulty": 1,
        "prompt": "Describe a specific scenario where you had to present a highly complex data science analysis or machine learning model to executive non-technical stakeholders. Structure your response using the STAR method (Situation, Task, Action, Result), highlighting how you adapted your communication and what key takeaway resulted.",
        "reference": "A strong STAR response provides a specific Situation and Task, explains Actions tailored to the audience, reports a measurable Result, and reflects on what was learned.",
        "rubric": {"situation": 0.2, "task": 0.15, "action": 0.3, "result": 0.25, "reflection": 0.1}
    },
    {
        "stage": "behavioral",
        "track": "all",
        "topic": "ownership",
        "difficulty": 2,
        "prompt": "Give an example of a project where you received critical or conflicting feedback from peer reviewers or stakeholders regarding your analytical methodology or assumptions. Using the STAR framework, detail the context, how you handled the feedback constructively, the actions taken, and the ultimate outcome.",
        "reference": "A strong STAR response names the context, describes ownership and concrete corrective action, reports an outcome, and shows reflection or a durable process improvement.",
        "rubric": {"situation": 0.15, "task": 0.15, "action": 0.35, "result": 0.2, "reflection": 0.15}
    },
]
