pipeline {
    agent any
    environment {
        // INTERNAL Docker network URL for Airflow
        AIRFLOW_API = "http://airflow-webserver:8080/api/v1"
        // INTERNAL Docker network URL for the FastAPI service (matches container_name)
        API_URL = "http://inference-api:8000"
    }
    stages {
        stage('Initialize') {
            steps {
                echo '🚀 Starting California Housing MLOps Pipeline...'
            }
        }
        stage('Trigger Training') {
            steps {
                echo '📡 Triggering Airflow DAG...'
                sh "curl -X POST ${AIRFLOW_API}/dags/california_housing_dag/dagRuns -H 'Content-Type: application/json' --user admin:admin -d '{}'"
            }
        }
        stage('API Health Check (Wait for Model)') {
            steps {
                echo '🔍 Waiting for API to load the trained model...'
                sh '''
                for i in {1..30}; do
                  # Using the environment variable defined above
                  RESPONSE=$(curl -s ${API_URL}/health)
                  echo "Health response: $RESPONSE"
                  
                  if echo "$RESPONSE" | grep -q '"status":"ok"'; then
                    echo "✅ API is READY"
                    exit 0
                  fi
                  
                  echo "⏳ Model not ready yet (Attempt $i/30), retrying in 10s..."
                  sleep 10
                done
                echo "❌ Model load timeout"
                exit 1
                '''
            }
        }
        stage('Functional Test') {
            steps {
                echo '🧪 Running Prediction Test...'
                sh '''
                curl -X POST ${API_URL}/predict \
                -H "Content-Type: application/json" \
                -d '{"MedInc": 8.3, "HouseAge": 41.0, "AveRooms": 6.9, "AveBedrms": 1.0, "Population": 322.0, "AveOccup": 2.5, "Latitude": 37.8, "Longitude": -122.2}'
                '''
            }
        }
    }
    post {
        failure {
            echo '⚠️ Pipeline FAILED: Check Airflow DAG or API logs.'
        }
    }
}
