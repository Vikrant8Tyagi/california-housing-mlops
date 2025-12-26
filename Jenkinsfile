pipeline {
    agent any

    options {
        // 🔑 CRITICAL: stop Jenkins from auto-running git ls-remote
        skipDefaultCheckout(true)
    }

    stages {

        stage('Fix Git Safe Directory') {
            steps {
                echo 'Fixing Git dubious ownership issue BEFORE checkout...'
                sh '''
                    git config --global --add safe.directory /app
                    git config --global --add safe.directory /app/.git
                '''
            }
        }

        stage('Checkout') {
            steps {
                echo 'Manually checking out repository...'
                checkout scm
            }
        }

        stage('Trigger Training') {
            steps {
                echo "Triggering Airflow DAG..."
                sh """
                curl -X POST "http://airflow-webserver:8080/api/v1/dags/california_housing_dag/dagRuns" \
                  -H "Content-Type: application/json" \
                  --user "admin:admin" \
                  -d '{}'
                """
            }
        }

        stage('Health Check') {
            steps {
                echo 'Verifying API status...'
                sh "curl http://api:8000/health"
            }
        }
    }
}
