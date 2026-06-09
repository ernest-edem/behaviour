import random
from app.schemas.assessment import AssessmentCreate, AssessmentResult, RiskLevel


class AssessmentService:
    @staticmethod
    def predict_risk(data: AssessmentCreate) -> AssessmentResult:
        # Mock ML logic
        # In a real scenario, this would load a model and run inference
        
        # Simple heuristic for mock output
        risk_score = (
            (data.stress_level * 0.2) + 
            (data.bmi * 0.1) + 
            (data.smoking * 2.0) + 
            (data.alcohol * 1.0)
        ) / 10.0
        
        # Normalize to 0-1
        risk_score = min(max(risk_score, 0.0), 1.0)
        
        if risk_score < 0.2:
            level = RiskLevel.LOW
            explanation = "Your lifestyle indicators suggest a very low risk of behavioral diseases."
        elif risk_score < 0.4:
            level = RiskLevel.MILD
            explanation = "Minor lifestyle adjustments could help maintain your healthy status."
        elif risk_score < 0.6:
            level = RiskLevel.MODERATE
            explanation = "Some risk factors detected. Consider improving sleep and physical activity."
        elif risk_score < 0.8:
            level = RiskLevel.HIGH
            explanation = "Significant risk factors identified. Consulting a professional is recommended."
        else:
            level = RiskLevel.CRITICAL
            explanation = "High risk detected. Immediate medical consultation and lifestyle changes are advised."

        return AssessmentResult(
            risk_score=round(risk_score, 2),
            risk_level=level,
            confidence=round(random.uniform(0.85, 0.98), 2),
            explanation=explanation
        )


assessment_service = AssessmentService()
