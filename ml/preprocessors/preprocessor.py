
import numpy as np
from sklearn.preprocessing import StandardScaler

class ThesisPreprocessor:
    FEATURE_ORDER = [
        "GPA","age","salary_min","salary_max",
        "skill_overlap","is_frontend","is_backend","is_data","is_other"
    ]
    def __init__(self):
        self.scaler = StandardScaler()

    def fit(self, X):
        self.scaler.fit(X); return self

    def transform(self, X):
        return self.scaler.transform(X)
