pipeline {
    agent any

    environment {
        IMAGE_NAME            = "welcome-login-app"
        IMAGE_TAG             = "my-welcome"
        CONTAINER_NAME        = "welcome-login-app"
        APP_PORT              = "5000"
        DOCKERHUB_CREDENTIALS = credentials('MY-docker-crds')
        DOCKERHUB_USERNAME    = "chandra219"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Verify Files') {
            steps {
                echo 'Verifying required files exist...'
                bat '''
                    if exist welcome.py (
                        echo welcome.py found
                    ) else (
                        echo welcome.py missing! && exit /b 1
                    )
                    if exist Dockerfile (
                        echo Dockerfile found
                    ) else (
                        echo Dockerfile missing! && exit /b 1
                    )
                    if exist requirements.txt (
                        echo requirements.txt found
                    ) else (
                        echo requirements.txt missing! && exit /b 1
                    )
                '''
            }
        }

        stage('Docker Login') {
            steps {
                echo 'Logging in to Docker Hub...'
                bat "echo %DOCKERHUB_CREDENTIALS_PSW% | docker login -u %DOCKERHUB_CREDENTIALS_USR% --password-stdin"
                echo 'Docker login successful'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                bat """
                    docker build -t %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%IMAGE_TAG% .
                    docker tag %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%IMAGE_TAG% %DOCKERHUB_USERNAME%/%IMAGE_NAME%:latest
                    echo Image built successfully
                """
            }
        }

        stage('Test Container') {
            steps {
                echo 'Running smoke test...'
                bat """
                    @echo off
                    setlocal enabledelayedexpansion
                    docker run -d --name test-%IMAGE_NAME%-%BUILD_NUMBER% -p 5001:5000 %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%IMAGE_TAG%
                    ping -n 8 127.0.0.1 > NUL
                    curl -s -o NUL -w "%%{http_code}" http://localhost:5001/health > health_status.txt
                    set /p HTTP_STATUS=<health_status.txt
                    docker stop test-%IMAGE_NAME%-%BUILD_NUMBER%
                    docker rm test-%IMAGE_NAME%-%BUILD_NUMBER%
                    del health_status.txt
                    if "!HTTP_STATUS!"=="200" (
                        echo Health check passed
                    ) else (
                        echo Health check failed - Status: !HTTP_STATUS! && exit /b 1
                    )
                """
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing image to Docker Hub...'
                bat """
                    docker push %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%IMAGE_TAG%
                    docker push %DOCKERHUB_USERNAME%/%IMAGE_NAME%:latest
                    echo Image pushed successfully
                """
            }
        }

        
        stage('Verify Deployment') {
            steps {
                echo 'Verifying deployment...'
                bat """
                    @echo off
                    setlocal enabledelayedexpansion
                    ping -n 5 127.0.0.1 > NUL
                    curl -s -o NUL -w "%%{http_code}" http://localhost:%APP_PORT%/health > verify_status.txt
                    set /p HTTP_STATUS=<verify_status.txt
                    del verify_status.txt
                    if "!HTTP_STATUS!"=="200" (
                        echo Deployment verified successfully!
                    ) else (
                        echo Deployment verification failed! Status: !HTTP_STATUS! && exit /b 1
                    )
                """
            }
        }
    }

    post {
        success {
            echo """
            ================================================
            BUILD AND DEPLOY SUCCESSFUL
            ================================================
            Image   : ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}
            App URL : http://localhost:${APP_PORT}
            Hub     : https://hub.docker.com/r/${DOCKERHUB_USERNAME}/${IMAGE_NAME}
           
            ================================================
            """
        }
        failure {
            echo 'Pipeline failed! Cleaning up test containers...'
            bat "docker rm -f test-%IMAGE_NAME%-%BUILD_NUMBER% 2>nul || exit /b 0"
        }
        always {
            echo 'Logging out of Docker...'
            bat "docker logout || exit /b 0"
        }
    }
}