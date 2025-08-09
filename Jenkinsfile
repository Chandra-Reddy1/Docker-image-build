pipeline {
    agent any

    environment {
        IMAGE_NAME = 'chandra219/welcome-app:latest123'
    }
    options {
        skipDefaultCheckout(true) // disables the automatic "Declarative: Checkout SCM"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }
        
        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat """
                     echo $DOCKER_PASS
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    """
                }
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                bat "docker buildx build --push --tag ${IMAGE_NAME} ."
            }
        }
    }
   
}
