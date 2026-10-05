CONCEPT_HINTS = {
    "distinction": ["association", "correlation", "cause", "causation"], "confounding": ["confound", "third variable"], "experiment": ["random", "experiment", "causal"],
    "imbalance": ["imbalanc", "rare", "skew"], "metrics": ["precision", "recall", "f1", "pr-auc", "confusion"], "threshold": ["threshold", "cost", "false negative", "false positive"], "mitigation": ["weight", "resampl", "oversampl", "data"],
    "diagnosis": ["train", "validation", "gap", "test"], "validation": ["validation", "cross-validation", "holdout", "time"], "regularization": ["regular", "penalty", "dropout"], "data_or_complexity": ["simpl", "complex", "data", "augment", "early stop"],
    "prediction_time": ["prediction time", "available", "before"], "features": ["missing", "categor", "aggregate", "feature"], "leakage": ["leak", "future", "target"], "time_split": ["time", "temporal", "split"],
    "inner": ["inner", "match", "both"], "left": ["left", "all", "left table"], "nulls": ["null", "unmatched"], "grain": ["duplicate", "grain", "multip"],
    "design": ["hypothesis", "metric", "sample", "duration", "predefine"], "quality": ["random", "sample ratio", "tracking", "quality"], "uncertainty": ["confidence", "significance", "interval", "p-value"], "practicality": ["practical", "effect size", "guardrail", "business"],
    "cold_start": ["cold", "new user", "onboarding"], "approach": ["metadata", "content", "popular", "collaborative"], "evaluation": ["offline", "a/b", "test", "ranking"], "guardrails": ["diversity", "satisfaction", "retention", "guardrail"],
    "skew": ["skew", "online", "training", "feature"], "monitoring": ["monitor", "drift", "segment"], "baseline": ["baseline", "compare"], "operations": ["alert", "rollback", "retrain"],
    "funnel": ["funnel", "conversion", "drop"], "segmentation": ["segment", "channel", "cohort"], "prioritization": ["impact", "effort", "priorit"], "experiments": ["experiment", "test", "a/b"],
    "framing": ["horizon", "cost", "decision"], "data": ["promotion", "holiday", "stockout", "sales"], "forecast_metrics": ["mae", "wape", "error", "metric"],
    "situation": ["situation", "when", "at "], "task": ["task", "goal", "needed"], "action": ["i ", "i did", "i used", "i created"], "result": ["result", "%", "improved", "reduced", "increased"], "reflection": ["learn", "would", "next time", "realized"],
    "statistics": ["statistical", "significan", "credible", "confidence"], "hypotheses": ["hypothes"],
}

STAGE_ORDER = ["warmup", "technical", "case", "behavioral"]
STAGE_REQUIRED = {"warmup": 1, "technical": 3, "case": 2, "behavioral": 2}

FRAMEWORK_HINTS = {
    "warmup": "Framework Hint: Introduce your background, primary technical skills, and current data focus in 2-3 concise sentences.",
    "technical": "Framework Hint: 1. Define core technical principles -> 2. Explain practical trade-offs & edge cases -> 3. Detail metrics, algorithm parameters, or SQL logic.",
    "case": "Framework Hint: 1. Frame business objectives & metrics -> 2. Segment conversion funnel & user cohorts -> 3. Propose A/B testing & guardrails.",
    "behavioral": "Framework Hint (STAR Method): Situation (Context) -> Task (Goal) -> Action (Your specific role & execution) -> Result (Quantifiable impact & reflection)."
}

EXPERT_BENCHMARK = [
    (1, "Correlation is association; causation means an intervention changes an outcome. Confounding can create correlation, so randomized experiments help establish causality.", 94),
    (1, "Correlation and causation are the same because both variables change together.", 8),
    (1, "We can use correlation to see if two things move together. If they do, one might cause the other, but we'd need an experiment to be sure.", 65),
    (2, "Use accuracy because it is the highest metric. I would collect more data.", 22),
    (2, "Fraud is imbalanced, so accuracy can mislead. Check precision, recall, F1 and PR-AUC, then choose a cost-aware threshold and use class weights or resampling.", 96),
    (2, "Since fraud is rare, I would use oversampling to make the dataset balanced and then train a model using F1 score.", 70),
    (3, "Overfitting happens when the model learns the training data too well. I would use L1 or L2 regularization to prevent it, or add dropout layers.", 85),
    (3, "I don't really know, maybe the model is just bad.", 10),
    (4, "Data leakage is when the model uses information from the future that wouldn't be available at prediction time. I'd split the data properly and ensure no future features are included.", 90),
    (4, "Leakage is bad data. I would drop null values.", 15),
    (5, "INNER JOIN keeps matching rows only. LEFT JOIN keeps every left record and nulls for unmatched right rows; verify key grain to avoid duplicates.", 92),
    (5, "Inner join is for inside tables and left join is for the left table.", 25),
    (6, "A/B testing needs a hypothesis and a success metric. We randomize users, wait for a predefined duration, and check statistical significance with p-values while monitoring business guardrails.", 95),
    (6, "Just release the feature to some people and see if they like it more.", 15),
    (7, "For a cold start problem, we don't have user history. I would use content-based filtering or popularity-based recommendations until we gather enough data.", 85),
    (8, "Training-serving skew means the offline model differs from online. We monitor drift in feature distributions and segment the data, using a baseline to compare and setting alerts to retrain.", 92),
    (10, "I would define the conversion funnel, validate tracking, segment by channel and cohort, quantify drop-offs, then prioritize and A/B test changes with retention guardrails.", 94),
    (10, "I would look at the users and see where they drop off. Then maybe try to fix those pages.", 45),
    (11, "I'd use time-series forecasting models like ARIMA or Prophet. I'll split data temporally and use MAE or WAPE as forecast metrics, making sure to account for holidays and promotions.", 90),
    (12, "In my previous role (Situation), we had high latency (Task). I redesigned the pipeline (Action), which reduced latency by 30% and taught me about caching (Result/Reflection).", 95),
]
