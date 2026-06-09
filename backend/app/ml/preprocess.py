import numpy as np
import pandas as pd
from typing import Dict, Any

class Preprocessor:
    def __init__(self):
        # In a real app, you would load saved scalers (e.g., joblib.load('scaler.pkl'))
        self.feature_names = [
            "age", "bmi", "sleep_hours", "stress_level", 
            "physical_activity", "smoking", "alcohol", 
            "blood_pressure", "glucose_level"
        ]

    def process(self, data: Dict[str, Any]) -> np.ndarray:
        """
        Convert raw input dictionary to scaled numpy array for the model.
        """
        df = pd.DataFrame([data])
        
        # Ensure correct feature order
        df = df[self.feature_names]
        
        # Placeholder for real scaling logic
        # scaled_data = self.scaler.transform(df)
        
        return df.values

preprocessor = Preprocessor()
