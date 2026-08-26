"""Cloud resource management for SPAGeo."""

import os
import json
import time
import boto3
from typing import Dict, List, Optional
from enum import Enum


class CloudProvider(Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class DeploymentType(Enum):
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


class CloudManager:
    """Manage cloud resources for SPAGeo simulations."""

    def __init__(self, provider: CloudProvider = CloudProvider.AWS):
        """Initialize cloud manager."""
        self.provider = provider
        self.resources = {}
        self.simulation_queue = []
        self.active_simulations = {}

        if provider == CloudProvider.AWS:
            self._init_aws()
        elif provider == CloudProvider.GCP:
            self._init_gcp()
        elif provider == CloudProvider.AZURE:
            self._init_azure()

    def _init_aws(self):
        """Initialize AWS resources."""
        self.aws_region = os.environ.get(
            'AWS_REGION',
            os.environ.get('AWS_DEFAULT_REGION')
        )

        if not self.aws_region:
            raise RuntimeError(
                "AWS region is not configured. "
                "Set AWS_REGION or AWS_DEFAULT_REGION."
            )

        self.s3 = boto3.client('s3', region_name=self.aws_region)
        self.batch = boto3.client('batch', region_name=self.aws_region)
        self.sqs = boto3.client('sqs', region_name=self.aws_region)
        self.ecs = boto3.client('ecs', region_name=self.aws_region)

        # Configure batch job definition
        self.job_definition = os.environ.get(
            'SPAGEO_JOB_DEFINITION',
            'spageo-simulation'
        )
        self.job_queue = os.environ.get(
            'SPAGEO_JOB_QUEUE',
            'spageo-queue'
        )
        self.bucket = os.environ.get(
            'SPAGEO_BUCKET',
            'spageo-data'
        )

    def _init_gcp(self):
        """Initialize GCP resources."""
        # Implementation for Google Cloud
        pass

    def _init_azure(self):
        """Initialize Azure resources."""
        # Implementation for Microsoft Azure
        pass

    def submit_simulation(self, model_config: Dict, user_id: str) -> str:
        """
        Submit simulation job to cloud.

        Args:
            model_config: Model configuration dictionary
            user_id: User identifier

        Returns:
            str: Job ID
        """
        # Generate unique job ID
        job_id = f"spageo-{int(time.time())}-{user_id}"

        # Upload model data to cloud storage
        self._upload_model_data(model_config, job_id)

        # Submit job to batch system
        if self.provider == CloudProvider.AWS:
            response = self.batch.submit_job(
                jobName=job_id,
                jobDefinition=self.job_definition,
                jobQueue=self.job_queue,
                parameters={
                    'model_config': json.dumps(model_config),
                    'job_id': job_id
                }
            )
            job_id = response['jobId']

        # Add to active simulations
        self.active_simulations[job_id] = {
            'status': 'submitted',
            'submitted_at': time.time(),
            'user_id': user_id
        }

        return job_id

    def _upload_model_data(self, model_config: Dict, job_id: str):
        """Upload model data to cloud storage."""
        # Save config to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as f:
            json.dump(model_config, f)
            f.flush()

            # Upload to S3/GCS/Azure
            if self.provider == CloudProvider.AWS:
                self.s3.upload_file(
                    f.name,
                    self.bucket,
                    f"{job_id}/config.json"
                )

    def get_simulation_status(self, job_id: str) -> Dict:
        """Get status of simulation job."""
        if self.provider == CloudProvider.AWS:
            response = self.batch.describe_jobs(jobs=[job_id])
            if response['jobs']:
                job = response['jobs'][0]
                return {
                    'status': job['status'],
                    'created_at': job['createdAt'],
                    'started_at': job.get('startedAt'),
                    'stopped_at': job.get('stoppedAt'),
                    'exit_code': job.get('container', {}).get('exitCode')
                }

        return {'status': 'not_found'}

    def download_results(self, job_id: str, local_path: str) -> bool:
        """Download simulation results from cloud."""
        try:
            if self.provider == CloudProvider.AWS:
                # List objects in bucket
                response = self.s3.list_objects_v2(
                    Bucket=self.bucket,
                    Prefix=f"{job_id}/results/"
                )

                for obj in response.get('Contents', []):
                    key = obj['Key']
                    filename = key.split('/')[-1]
                    self.s3.download_file(
                        self.bucket,
                        key,
                        os.path.join(local_path, filename)
                    )

            return True

        except Exception as e:
            raise RuntimeError(f"Failed to download results: {str(e)}")

    def cleanup_job(self, job_id: str):
        """Clean up cloud resources for job."""
        # Delete data from storage
        if self.provider == CloudProvider.AWS:
            # Delete all objects with job prefix
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=f"{job_id}/"
            )

            if 'Contents' in response:
                objects = [{'Key': obj['Key']} for obj in response['Contents']]
                self.s3.delete_objects(
                    Bucket=self.bucket,
                    Delete={'Objects': objects}
                )

        # Remove from active simulations
        if job_id in self.active_simulations:
            del self.active_simulations[job_id]

    def get_cloud_cost_estimate(self, model_size: int, duration: int) -> float:
        """Estimate cloud compute cost."""
        # AWS pricing: ~$0.10 per vCPU-hour for spot instances
        # MODFLOW typically uses 1-4 vCPUs
        vcpus = min(max(model_size // 10000, 1), 4)
        cost_per_hour = 0.10 * vcpus

        return cost_per_hour * (duration / 3600)

    def is_cloud_beneficial(self, model_size: int, duration: int) -> bool:
        """Determine if cloud deployment is beneficial."""
        # Cloud beneficial for models larger than threshold
        threshold = 100000  # 100k cells
        return model_size > threshold or duration > 3600  # >1 hour
