from sqlalchemy.orm import Session

from app.models.user import User
from app.models.assessment import Assessment
from app.models.prediction import Prediction
from app.models.disease_prediction import DiseasePrediction


def load_resource(db: Session, model, resource_id: int):
    """
    Centralized resource loading for IAM checks
    """

    return db.query(model).filter(model.id == resource_id).first()