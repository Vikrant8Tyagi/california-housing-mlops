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
                echo '📡 Triggering Airflow DAG via API...'
                // Using double quotes to allow potential Jenkins variable expansion
                sh """
                curl -X POST "http://airflow-webserver:8080/api/v1/dags/california_housing_dag/dagRuns" \
                  -H "Content-Type: application/json" \
                  --user "admin:admin" \
                  -d '{}'
                """
            }
        }

        stage('API Health Check (Wait for Model)') {
            steps {
                echo '🔍 Waiting for API to load the trained model...'
                timeout(time: 10, unit: 'MINUTES') {
                    script {
                        waitUntil {
                            def response = sh(script: "curl -s http://api:8000/health", returnStdout: true).trim()
                            echo "Health response: ${response}"
                            return response.contains('"status":"ok"')
                        }
                    }
                }
            }
        }

        stage('Functional Test') {
            steps {
                echo '🧪 Sending test prediction request...'
                script {
                    def response = sh(
                        script: '''
                        curl -s -X POST "http://api:8000/predict" \
                          -H "accept: application/json" \
                          -H "Content-Type: application/json" \
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
                        ''',
                        returnStdout: true
                    ).trim()

                    echo "Prediction response: ${response}"

                    if (response.contains("median_house_value")) {
                        echo "✅ Prediction successful!"
                    } else {
                        error "❌ Prediction failed or model not available"
                    }
                }
            }
        }
    }

    post {
        success {
            echo '🎊 Pipeline SUCCESS: Training + API + Prediction all verified!'
        }
        failure {
            echo '⚠️ Pipeline FAILED: Check Airflow DAG or API logs.'
        }
    }
}
