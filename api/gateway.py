"""API Gateway for SPAGeo cloud services."""

import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta, timezone
import uuid

from core.cloud_manager import CloudManager
from core.model_engine import ModelEngine

app = FastAPI(title="SPAGeo API", version="1.0.0")

# Security configuration
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")


class SPAGeoAPI:
    """SPAGeo REST API gateway."""

    def __init__(self, cloud_manager=None):
        """Initialize API."""
        self.secret_key = os.environ.get('SPAGEO_SECRET_KEY')
        if not self.secret_key:
            raise RuntimeError(
                "SPAGEO_SECRET_KEY is not configured."
            )

        self.cloud_manager = CloudManager()

    def validate_api_key(self, api_key: str) -> Dict:
        """Validate API key and return authenticated user info."""
        expected_key = os.environ.get('SPAGEO_API_KEY')

        if not expected_key:
            raise HTTPException(
                status_code=500,
                detail="SPAGEO_API_KEY is not configured"
            )

        if not api_key or api_key != expected_key:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key"
            )

        return {
            'user_id': 'test_user',
            'plan': 'pro'
        }
    async def create_model(self, config: Dict, user: Dict) -> Dict:
        """API endpoint for model creation."""
        # Validate config
        required_fields = ['name', 'grid', 'aquifer', 'boundary']
        for field in required_fields:
            if field not in config:
                raise HTTPException(400, f"Missing field: {field}")

        # Create model
        engine = ModelEngine()
        success = engine.create_model(
            config['grid'],
            config['boundary'],
            config['aquifer']
        )

        if not success:
            raise HTTPException(500, "Model creation failed")

        return {'status': 'success', 'model_id': config.get('name')}

    async def run_simulation(self, model_id: str, config: Dict, user: Dict) -> Dict:
        """API endpoint for simulation execution."""
        # Submit to cloud
        job_id = self.cloud_manager.submit_simulation(
            {'model_id': model_id, **config},
            user['user_id']
        )

        return {
            'status': 'submitted',
            'job_id': job_id,
            'estimated_cost': self.cloud_manager.get_cloud_cost_estimate(
                config.get('cells', 10000),
                config.get('duration', 3600)
            )
        }

    async def get_results(self, job_id: str, user: Dict) -> Dict:
        """API endpoint for retrieving results."""
        status = self.cloud_manager.get_simulation_status(job_id)

        if status['status'] == 'SUCCEEDED':
            # Download results
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                self.cloud_manager.download_results(job_id, tmpdir)
                # Convert to response format
                results = self._process_results(tmpdir)
                return {'status': 'completed', 'results': results}

        return {'status': status['status']}

    def _process_results(self, directory: str) -> Dict:
        """Process downloaded results."""
        # Load head results
        import flopy
        import os

        head_file = os.path.join(directory, 'heads.hds')
        if os.path.exists(head_file):
            heads = flopy.utils.HeadFile(head_file)
            data = heads.get_data()
            return {
                'heads': data.tolist(),
                'format': 'flopy-heads',
                'shape': data.shape
            }
        return {'error': 'Results not found'}

    def create_jwt(self, user_id: str, expires_days: int = 7) -> str:
        """Create JWT token for authentication."""
        payload = {
            'user_id': user_id,
            'exp': datetime.now(timezone.utc) + timedelta(days=expires_days),
            'iat': datetime.now(timezone.utc)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')


def get_api() -> SPAGeoAPI:
    """Provide the SPAGeo API gateway instance."""
    return SPAGeoAPI()
# ---------------------------------------------------------------------------
# FastAPI REST routes
# ---------------------------------------------------------------------------

api = get_api()


# ---------------------------------------------------------------------------
# Authentication dependency
# ---------------------------------------------------------------------------

def get_current_user(
    api_key: str = Security(API_KEY_HEADER)
) -> Dict:
    """Validate the supplied API key and return authenticated user info."""
    return api.validate_api_key(api_key)


# ---------------------------------------------------------------------------
# FastAPI REST routes
# ---------------------------------------------------------------------------

@app.post("/models")
async def create_model(
    config: Dict[str, Any],
    user: Dict = Depends(get_current_user)
):
    """Create a new groundwater model."""
    return await api.create_model(config, user)


@app.post("/simulations/{model_id}")
async def run_simulation(
    model_id: str,
    config: Dict[str, Any],
    user: Dict = Depends(get_current_user)
):
    """Submit a groundwater simulation to the cloud."""
    return await api.run_simulation(model_id, config, user)


@app.get("/results/{job_id}")
async def get_results(
    job_id: str,
    user: Dict = Depends(get_current_user)
):
    """Retrieve groundwater simulation results."""
    return await api.get_results(job_id, user)