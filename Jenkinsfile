pipeline {
    agent any

    environment {
        IMAGE_NAME            = "welcome-login-app"
        IMAGE_TAG             = "${BUILD_NUMBER}"
        CONTAINER_NAME        = "welcome-login-app"
        APP_PORT              = "5000"
        DOCKERHUB_CREDENTIALS = credentials('MY-docker-crds')  // 👈 Jenkins credential ID
        // credentials() auto-generates:
        //   DOCKERHUB_CREDENTIALS_USR  → your Docker Hub email (used for login only)
        //   DOCKERHUB_CREDENTIALS_PSW  → your Docker Hub password
        DOCKERHUB_USERNAME    = "chandrachandra42428"           // 👈 Your Docker Hub username (not email)
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
                echo "Building Docker image..."
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
                    docker run -d --name test-%IMAGE_NAME%-%BUILD_NUMBER% -p 5001:5000 %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%IMAGE_TAG%
                    timeout /t 5 /nobreak
                    curl -s -o NUL -w "%%{http_code}" http://localhost:5001/health > health_status.txt
                    set /p HTTP_STATUS=<health_status.txt
                    docker stop test-%IMAGE_NAME%-%BUILD_NUMBER%
                    docker rm test-%IMAGE_NAME%-%BUILD_NUMBER%
                    del health_status.txt
                    if "%HTTP_STATUS%"=="200" (
                        echo Health check passed
                    ) else (
                        echo Health check failed && exit /b 1
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

        stage('Deploy Container') {
            steps {
                echo 'Deploying container...'
                bat """
                    for /f %%i in ('docker ps -q -f name=%CONTAINER_NAME%') do docker stop %%i
                    for /f %%i in ('docker ps -aq -f name=%CONTAINER_NAME%') do docker rm %%i
                    docker run -d --name %CONTAINER_NAME% --restart unless-stopped -p %APP_PORT%:5000 %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%IMAGE_TAG%
                    echo Container deployed at http://localhost:%APP_PORT%
                """
            }
        }

        stage('Verify Deployment') {
            steps {
                echo 'Verifying deployment...'
                bat """
                    timeout /t 3 /nobreak
                    curl -s -o NUL -w "%%{http_code}" http://localhost:%APP_PORT%/health > verify_status.txt
                    set /p HTTP_STATUS=<verify_status.txt
                    del verify_status.txt
                    if "%HTTP_STATUS%"=="200" (
                        echo Deployment verified successfully!
                    ) else (
                        echo Deployment verification failed! && exit /b 1
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
            Build   : #${BUILD_NUMBER}
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