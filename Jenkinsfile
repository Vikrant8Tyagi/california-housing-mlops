pipeline {
    agent any

    environment {
        AIRFLOW_API  = "http://airflow-webserver:8080/api/v1"
        AIRFLOW_USER = "admin"
        AIRFLOW_PASS = "admin"
        DAG_ID       = "california_housing_dag"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Trigger Airflow Training') {
            steps {
                echo '📡 Triggering Airflow DAG via REST API'
                sh """
                curl -f -X POST "${AIRFLOW_API}/dags/${DAG_ID}/dagRuns" \
                  -H "Content-Type: application/json" \
                  --user "${AIRFLOW_USER}:${AIRFLOW_PASS}" \
                  -d '{}'
                """
            }
        }

        stage('Wait for Training') {
            steps {
                echo '⏳ Waiting for model training to complete'
                sleep 45
            }
        }

        stage('Verify MLflow') {
            steps {
                echo '🔍 Verifying MLflow service'
                sh 'curl -f http://localhost:5000'
            }
        }

        stage('Start Prediction API') {
            steps {
                echo '🚀 Starting prediction API'
                sh 'docker compose up -d prediction-api'
                sleep 10
            }
        }

        stage('Functional Test') {
            steps {
                echo '🧪 Running prediction test'
                sh """
                curl -f -X POST http://localhost:8000/predict \
                  -H "Content-Type: application/json" \
                  -d '[8.32, 41.0, 6.98, 1.02, 322.0, 2.55, 37.88, -122.23]'
                """
            }
        }
    }

    post {
        success {
            echo '✅ PIPELINE COMPLETED SUCCESSFULLY'
        }
        failure {
            echo '❌ PIPELINE FAILED – check logs'
        }
    }
}
