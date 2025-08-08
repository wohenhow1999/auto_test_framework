pipeline {
    agent any

    options {
        buildDiscarder(logRotator(
            numToKeepStr: '30',
            artifactNumToKeepStr: '30'
        ))
    }

    triggers {
        cron('H 0 * * *')
    }

    environment {
        IMAGE_NAME = "devcontainer-test:latest"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    sh '''
                        docker build -t $IMAGE_NAME -f .devcontainer/Dockerfile .
                    '''
                }
            }
        }

        stage('Clean Old Logs') {
            steps {
                script {
                    sh '''
                        docker run --rm \
                            -v "$(pwd):/app" \
                            -w /app \
                            $IMAGE_NAME bash -c "rm -rf logs || true"
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh '''
                        docker run --rm \
                            -v "$(pwd):/app" \
                            -w /app \
                            $IMAGE_NAME bash run_test.sh
                    '''
                }
            }
        }

        stage('Publish Allure Report') {
            steps {
                allure results: [[path: 'reports/allure-results']]
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'artifacts/*.txt, logs/*.log', fingerprint: true
        }
    }
}