pipeline {
    agent {
        node {
            label ''
            customWorkspace '/Users/Shared/jenkins_workspace/RADIX-Pipeline'
        }
    }

    environment {
        // Reference to credentials ID 'ENV' configured in Jenkins (Step 7)
        ENV_CREDENTIAL = credentials('ENV')
    }

    stages {
        stage('Inject Environment Configuration') {
            steps {
                echo 'Injecting .env file to backend...'
                sh 'cp ${ENV_CREDENTIAL} activity-06/backend/.env'
            }
        }

        // --- FRONT-END PIPELINE ---
        stage('Frontend - Install Dependencies') {
            steps {
                dir('activity-06/frontend') {
                    sh 'npm install'
                }
            }
        }

        stage('Frontend - Build & Validate') {
            steps {
                dir('activity-06/frontend') {
                    sh 'npm run build'
                    sh 'npm run lint || true' // continue even if lint warnings exist
                }
            }
        }

        stage('Frontend - Docker Build') {
            steps {
                sh 'docker build -t radix-frontend:latest ./activity-06/frontend'
            }
        }

        // --- BACK-END PIPELINE ---
        stage('Backend - Install Dependencies') {
            steps {
                dir('activity-06/backend') {
                    sh 'python3 -m venv venv'
                    sh './venv/bin/pip install -r requirements.txt'
                }
            }
        }

        stage('Backend - Execute Tests') {
            steps {
                dir('activity-06/backend') {
                    sh './venv/bin/python -m unittest test_pipeline_logic.py'
                }
            }
        }

        stage('Backend - Docker Build') {
            steps {
                sh 'docker build -t radix-backend:latest ./activity-06/backend'
            }
        }

        // --- AGENTIC ORCHESTRATION PIPELINE ---
        stage('Orchestration - Service Initialization') {
            steps {
                dir('activity-06') {
                    echo 'Tearing down existing containers if any...'
                    sh 'docker compose down --remove-orphans || true'
                    echo 'Starting company intelligence stack...'
                    sh 'docker compose up -d'
                }
            }
        }

        stage('Orchestration - Workflow Verification') {
            steps {
                echo 'Waiting for services to initialize...'
                sleep 5
                echo 'Verifying FastAPI Service Health...'
                sh 'curl -f http://localhost:8000/docs || curl -I http://localhost:8000/'
                echo 'Verifying Streamlit Admin UI Availability...'
                sh 'curl -f http://localhost:8501 || curl -I http://localhost:8501/'
                echo 'Verifying React Frontend Portal Availability...'
                sh 'curl -f http://localhost:8080 || curl -I http://localhost:8080/'
            }
        }
    }

    post {
        always {
            echo 'Pipeline Execution Completed.'
        }
        success {
            echo 'Build and Deployment succeeded!'
        }
        failure {
            echo 'Pipeline failed. Check stage logs for details.'
        }
    }
}
