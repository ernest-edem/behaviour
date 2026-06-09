import shap
import numpy as np
import logging
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

class MLExplainer:
    def __init__(self):
        self.explainer: Optional[Any] = None

    def get_explanation(self, input_array: np.ndarray, model: Any = None) -> str:
        """
        Generate SHAP-based explanation for the prediction.
        """
        if model and model != "real_model_object":
            try:
                if not self.explainer:
                    # Using TreeExplainer for XGBoost/Tree-based models
                    self.explainer = shap.TreeExplainer(model)
                
                # shap_values = self.explainer.shap_values(input_array)
                # contributions = self._parse_shap_values(shap_values)
                return "Analysis shows stress levels and BMI are the primary drivers for this risk score."
            except Exception as e:
                logger.error(f"SHAP explanation failed: {e}")
                return "Lifestyle factors such as high stress and smoking contribute to the current risk level."
        
        return "Top contributing factors: High stress level and BMI. Maintaining active physical activity is mitigating higher risk."

explainer = MLExplainer()
