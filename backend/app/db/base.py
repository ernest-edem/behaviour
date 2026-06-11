# Import all the models, so that Base has them before being
# imported by Alembic or used to create tables
from app.db.session import Base  # noqa
from app.models.user import User  # noqa
from app.models.assessment import Assessment  # noqa
from app.models.prediction import Prediction  # noqa
from app.models.disease_prediction import DiseasePrediction  # noqa
from app.models.prediction_explanation import PredictionExplanation  # noqa
