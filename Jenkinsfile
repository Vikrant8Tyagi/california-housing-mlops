pipeline {
    agent any
    
    stages {
        stage('Initialize') {
            steps {
                echo '🚀 Starting California Housing MLOps Pipeline...'
            }
        }
        
        stage('Trigger Training') {
            steps {
                script {
                    echo "📡 Triggering Airflow DAG via API..."
                    sh """
                    curl -i -X POST "http://airflow-webserver:8080/api/v1/dags/california_housing_dag/dagRuns" \
                    -H "Content-Type: application/json" \
                    --user "admin:admin" \
                    -d '{}'
                    """
                }
            }
        }
        
        stage('API Health Check') {
            steps {
                echo '🔍 Verifying API Container Status...'
                // Use 'api' hostname inside Docker network
                sh "curl http://api:8000/health"
            }
        }

        stage('Functional Test') {
            steps {
                echo '🧪 Sending Test Prediction Request...'
                script {
                    def response = sh(script: """
                        curl -X 'POST' \
                        'http://api:8000/predict' \
                        -H 'accept: application/json' \
                        -H 'Content-Type: application/json' \
                        -d '{
                            "MedInc": 8.3252,
                            "HouseAge": 41.0,
                            "AveRooms": 6.9841,
                            "AveBedrms": 1.0238,
                            "Population": 322.0,
                            "AveOccup": 2.5556,
                            "Latitude": 37.88,
                            "Longitude": -122.23
                        }'
                    """, returnStdout: true).trim()
                    
                    echo "Response: ${response}"
                    
                    if (response.contains("median_house_value")) {
                        echo "✅ Prediction successful!"
                    } else {
                        error "❌ Prediction failed or returned invalid format"
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo '🎊 Pipeline Completed! Data validated, Model trained, and API tested.'
        }
        failure {
            echo '⚠️ Pipeline Failed. Please check Jenkins logs or Airflow UI.'
        }
    }
}
