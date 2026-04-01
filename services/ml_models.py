import joblib
import os
from pathlib import Path
import numpy as np
from typing import Dict, Any, List

# Path to trained models
MODELS_DIR = Path(__file__).parent.parent / "models" / "trained_models"

class MLModelManager:
    """Load and manage all trained ML models"""

    def __init__(self):
        self.models = {}
        self.models_loaded = False
        self.load_all_models()

    def load_all_models(self):
        """Load all .pkl models at startup"""
        try:
            # Classification model
            self.models['position_sector'] = joblib.load(
                MODELS_DIR / "best_model_classification_Position_sector.pkl"
            )

            # Regression models
            self.models['r_bio'] = joblib.load(
                MODELS_DIR / "best_model_regression_R_BIO.pkl"
            )
            self.models['t_ab'] = joblib.load(
                MODELS_DIR / "best_model_regression_T_AB.pkl"
            )
            self.models['t_bio'] = joblib.load(
                MODELS_DIR / "best_model_regression_T_BIO.pkl"
            )
            self.models['t_sr'] = joblib.load(
                MODELS_DIR / "best_model_regression_T_SR.pkl"
            )

            self.models_loaded = True
            print("[OK] All ML models loaded successfully")
        except Exception as e:
            print(f"[WARNING] Error loading ML models: {e}")
            self.models_loaded = False

    def predict_position_sector(self, features: List[float]) -> str:
        """Classify position/sector"""
        if not self.models_loaded:
            return "unknown"
        try:
            features_array = np.array(features).reshape(1, -1)
            prediction = self.models['position_sector'].predict(features_array)
            return str(prediction[0])
        except Exception as e:
            print(f"Error in position_sector prediction: {e}")
            return "unknown"

    def predict_r_bio(self, features: List[float]) -> float:
        """Predict biodiversity-related value"""
        if not self.models_loaded:
            return 50.0
        try:
            features_array = np.array(features).reshape(1, -1)
            prediction = self.models['r_bio'].predict(features_array)
            return float(prediction[0])
        except Exception as e:
            print(f"Error in r_bio prediction: {e}")
            return 50.0

    def predict_t_ab(self, features: List[float]) -> float:
        """Predict temperature/algal bloom value"""
        if not self.models_loaded:
            return 50.0
        try:
            features_array = np.array(features).reshape(1, -1)
            prediction = self.models['t_ab'].predict(features_array)
            return float(prediction[0])
        except Exception as e:
            print(f"Error in t_ab prediction: {e}")
            return 50.0

    def predict_t_bio(self, features: List[float]) -> float:
        """Predict thermal/biodiversity index"""
        if not self.models_loaded:
            return 50.0
        try:
            features_array = np.array(features).reshape(1, -1)
            prediction = self.models['t_bio'].predict(features_array)
            return float(prediction[0])
        except Exception as e:
            print(f"Error in t_bio prediction: {e}")
            return 50.0

    def predict_t_sr(self, features: List[float]) -> float:
        """Predict thermal/species risk"""
        if not self.models_loaded:
            return 50.0
        try:
            features_array = np.array(features).reshape(1, -1)
            prediction = self.models['t_sr'].predict(features_array)
            return float(prediction[0])
        except Exception as e:
            print(f"Error in t_sr prediction: {e}")
            return 50.0

    def predict_stress_index(self, region_data: Dict[str, float]) -> float:
        """
        Predict stress index using all models combined
        Input: {
            'species_risk': float,
            'fish_stock_level': float,
            'temperature_anomaly': float,
            'pollution_score': float
        }
        Output: Combined stress score (0-100)
        """
        try:
            # Use multiple models for comprehensive prediction
            t_sr_pred = self.predict_t_sr([region_data.get('temperature_anomaly', 50)])
            t_bio_pred = self.predict_t_bio([region_data.get('fish_stock_level', 50)])
            r_bio_pred = self.predict_r_bio([region_data.get('pollution_score', 50)])

            # Weighted combination of predictions
            combined_score = (
                0.35 * region_data.get('species_risk', 50) +
                0.30 * (100 - region_data.get('fish_stock_level', 50)) +
                0.20 * t_sr_pred +
                0.15 * region_data.get('pollution_score', 50)
            )

            return min(max(combined_score, 0), 100)
        except Exception as e:
            print(f"Error in stress_index prediction: {e}")
            return 50.0

# Initialize global model manager
model_manager = None

def init_models():
    """Initialize ML models (called on app startup)"""
    global model_manager
    model_manager = MLModelManager()
    return model_manager

def get_model_manager() -> MLModelManager:
    """Get the ML model manager"""
    global model_manager
    if model_manager is None:
        model_manager = init_models()
    return model_manager
