from pydantic import BaseModel


class ModelOutput(BaseModel):
    direction: str    # up | down
    probability: float


class PredictionResponse(BaseModel):
    symbol: str
    prediction: str        # up | down
    confidence: float      # 0-1
    expected_return: float  # percentage
    xgboost: ModelOutput
    lstm: ModelOutput
