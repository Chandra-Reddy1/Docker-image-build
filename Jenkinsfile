pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub') // Jenkins credentials ID
        IMAGE_NAME = 'chandra219/welcome-app:latest'
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }
        stage('Set up Docker Buildx') {
            steps {
                // Optional: Install buildx if not present
                sh 'docker buildx version || docker buildx create --use'
            }
        }
        stage('Login to Docker Hub') {
            steps {
                script {
                    sh "echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin"
                }
            }
        }
        stage('Build and Push Docker Image') {
            steps {
                script {
                    sh "docker buildx build --push --tag ${IMAGE_NAME} ."
                }
            }
        }
    }
    post {
        always {
            sh 'docker logout'
        }
    }
}
