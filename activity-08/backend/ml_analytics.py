import numpy as np
import pandas as pd
import logging
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import json

logger = logging.getLogger("MLAnalytics")

class MLAnalytics:
    def __init__(self):
        self.pca = PCA(n_components=2, random_state=42)
        self.regressor = None
        self.feature_columns = []
        self.label_encoders = {}
        self.model_trained = False

    def perform_clustering_and_projection(self, companies_with_embeddings: list[dict], n_clusters: int = 5) -> list[dict]:
        """
        Groups company embeddings using K-Means and projects the 768-dimensional vectors to 2D using PCA.
        """
        if not companies_with_embeddings:
            return []

        embeddings = np.array([c["embedding"] for c in companies_with_embeddings])
        
        # Apply K-Means
        kmeans = KMeans(n_clusters=min(n_clusters, len(companies_with_embeddings)), random_state=42, n_init='auto')
        cluster_labels = kmeans.fit_predict(embeddings)
        
        # Apply PCA to project to 2D
        coords_2d = self.pca.fit_transform(embeddings)
        
        results = []
        for i, comp in enumerate(companies_with_embeddings):
            results.append({
                "company_id": comp["company_id"],
                "name": comp["name"],
                "cluster_id": int(cluster_labels[i]),
                "x": float(coords_2d[i, 0]),
                "y": float(coords_2d[i, 1]),
                "category": comp["metadata"].get("category", "NA")
            })
        return results

    def _parse_employee_size(self, size_str: str) -> float:
        """
        Parses employee count from string. E.g. "740,000 employees" -> 740000.
        """
        if not size_str or size_str == "NA":
            return 500.0  # default median fallback
        try:
            # Strip non-numeric characters
            clean_str = "".join([c for c in size_str if c.isdigit() or c == "."])
            if clean_str:
                return float(clean_str)
        except Exception:
            pass
        return 500.0

    def _parse_ai_adoption(self, level_str: str) -> float:
        """
        Maps adoption text to numerical index.
        """
        lvl = str(level_str).lower()
        if "high" in lvl or "leader" in lvl or "forward" in lvl:
            return 3.0
        if "medium" in lvl or "average" in lvl:
            return 2.0
        if "low" in lvl or "limited" in lvl or "none" in lvl:
            return 1.0
        return 1.5

    def train_predictive_model(self, companies: list[dict]) -> dict:
        """
        Extracts features and trains a Random Forest regressor to predict company YoY growth rate.
        """
        if len(companies) < 5:
            logger.warning("Too few companies to train a predictive model. Defaulting feature importance.")
            return {"status": "skipped", "reason": "Insufficient data"}
            
        data = []
        for comp in companies:
            metadata = comp.get("metadata", {}) or {}
            
            # Target YoY growth rate (convert float, e.g. 0.05)
            yoy = metadata.get("yoy_growth_rate")
            if yoy is None:
                continue
            try:
                yoy_val = float(yoy)
            except ValueError:
                continue
                
            # Features
            category = metadata.get("category", "Enterprise")
            inc_year = metadata.get("incorporation_year")
            try:
                age = 2026 - int(inc_year) if inc_year else 15
            except ValueError:
                age = 15
                
            size = self._parse_employee_size(metadata.get("employee_size", ""))
            ai_level = self._parse_ai_adoption(metadata.get("ai_ml_adoption_level", ""))
            nature = metadata.get("nature_of_company", "Private")
            social = float(metadata.get("social_media_followers") or 5000)
            
            data.append({
                "yoy_growth_rate": yoy_val,
                "category": category,
                "age": age,
                "employee_size": size,
                "ai_adoption": ai_level,
                "nature": nature,
                "social_followers": social
            })
            
        df = pd.DataFrame(data)
        if len(df) < 5:
            return {"status": "skipped", "reason": "Insufficient valid feature columns"}

        # Encode categoricals
        categorical_cols = ["category", "nature"]
        self.label_encoders = {}
        for col in categorical_cols:
            le = LabelEncoder()
            df[col] = le.fit_predict(df[col])
            self.label_encoders[col] = le
            
        # Split features and target
        X = df.drop(columns=["yoy_growth_rate"])
        y = df["yoy_growth_rate"]
        
        self.feature_columns = list(X.columns)
        
        # Train Random Forest Regressor
        self.regressor = RandomForestRegressor(n_estimators=50, random_state=42)
        self.regressor.fit(X, y)
        self.model_trained = True
        
        # Calculate feature importance
        importances = list(self.regressor.feature_importances_)
        feature_importance_map = [
            {"feature": self.feature_columns[i], "importance": float(importances[i])}
            for i in range(len(self.feature_columns))
        ]
        feature_importance_map.sort(key=lambda x: x["importance"], reverse=True)
        
        logger.info("Successfully trained Predictive ML Model for YoY growth forecasting.")
        return {
            "status": "trained",
            "features": self.feature_columns,
            "feature_importances": feature_importance_map,
            "sample_size": len(df)
        }

    def predict_growth_rate(self, input_data: dict) -> float:
        """
        Runs prediction for an input dictionary of features.
        """
        if not self.model_trained or self.regressor is None:
            return 0.05 # Default median fallback growth rate
            
        # Parse inputs matching our feature structure
        category = input_data.get("category", "Enterprise")
        age = float(input_data.get("age", 15))
        size = self._parse_employee_size(str(input_data.get("employee_size", "")))
        ai_level = self._parse_ai_adoption(str(input_data.get("ai_adoption", "")))
        nature = input_data.get("nature", "Private")
        social = float(input_data.get("social_followers", 5000))
        
        # Encode categorical variables using trained label encoders
        def encode_col(col_name, val):
            le = self.label_encoders.get(col_name)
            if le is None:
                return 0
            try:
                # If seen, transform, else return first class or default
                if val in le.classes_:
                    return int(le.transform([val])[0])
                else:
                    return 0
            except Exception:
                return 0
                
        cat_encoded = encode_col("category", category)
        nature_encoded = encode_col("nature", nature)
        
        # Align features
        features_aligned = []
        for col in self.feature_columns:
            if col == "category":
                features_aligned.append(cat_encoded)
            elif col == "age":
                features_aligned.append(age)
            elif col == "employee_size":
                features_aligned.append(size)
            elif col == "ai_adoption":
                features_aligned.append(ai_level)
            elif col == "nature":
                features_aligned.append(nature_encoded)
            elif col == "social_followers":
                features_aligned.append(social)
                
        pred = self.regressor.predict([features_aligned])[0]
        return float(pred)
