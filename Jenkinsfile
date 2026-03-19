pipeline {
    agent any

    environment {
        IMAGE_NAME            = "welcome-login-app"
        IMAGE_TAG             = "${BUILD_NUMBER}"
        CONTAINER_NAME        = "welcome-login-app"
        APP_PORT              = "5000"
        DOCKERHUB_CREDENTIALS = credentials('MY-docker-crds')
        DOCKERHUB_USERNAME    = "chandra219"
    }

    stages {

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

        stage('Sonar Scan') {
            steps {
                echo 'Running SonarQube analysis...'
                script {
                    withSonarQubeEnv('SonarServer') {
                        def scannerHome = tool 'SonarServer'
                        bat "${scannerHome}\\bin\\sonar-scanner.bat -Dsonar.projectKey=My-project -Dsonar.sources=."
                    }
                }
                echo 'SonarQube analysis completed'
            }
        }

        stage('Snyk Security Scan') {
            steps {
                echo 'Running Snyk vulnerability scan...'
                bat 'pip install -r requirements.txt --timeout=120 --retries=5 -i https://pypi.org/simple/'
                script {
                    snykSecurity(
                        snykInstallation: 'snyk',
                        snykTokenId: 'snyk-token',
                        failOnIssues: false,
                        monitorProjectOnBuild: true,
                        additionalArguments: '--package-manager=pip --file=requirements.txt --severity-threshold=high'
                    )
                }
                echo 'Snyk scan completed'
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

        stage('Deploy Container') {
            steps {
                echo 'Deploying container...'
                bat """
                    @echo off
                    docker stop %CONTAINER_NAME% 2>nul
                    docker rm %CONTAINER_NAME% 2>nul
                    docker run -d --name %CONTAINER_NAME% -p %APP_PORT%:5000 --restart unless-stopped %DOCKERHUB_USERNAME%/%IMAGE_NAME%:%IMAGE_TAG%
                    echo Container deployed successfully
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

        // ✅ Update image tag in ArgoCD GitOps repo using GitHub PAT token
        stage('Update GitOps Repo') {
            steps {
                echo 'Updating image tag in GitOps repo...'
                withCredentials([string(credentialsId: 'my-git-token', variable: 'GIT_TOKEN')]) {
                    bat """
                        @echo off

                        REM Clean up any previous clone
                        if exist argocd-demo-app rd /s /q argocd-demo-app

                        REM Clone using GitHub PAT token directly in URL
                        git clone https://%GIT_TOKEN%@github.com/Chandra-Reddy1/argocd-demo-app.git
                        cd argocd-demo-app

                        REM Replace the image tag in deployment.yaml using PowerShell
                        powershell -Command "(Get-Content k8s/deployment.yaml) -replace 'image: chandra219/welcome-login-app:[^\\s]+', 'image: chandra219/welcome-login-app:%IMAGE_TAG%' | Set-Content k8s/deployment.yaml"

                        REM Verify the change was applied
                        powershell -Command "Select-String -Path k8s/deployment.yaml -Pattern 'image:'"

                        REM Commit and push using token
                        git config user.email "jenkins@ci.com"
                        git config user.name "Jenkins CI"
                        git add k8s/deployment.yaml
                        git commit -m "ci: update welcome-login-app image tag to %IMAGE_TAG%"
                        git push https://%GIT_TOKEN%@github.com/Chandra-Reddy1/argocd-demo-app.git main

                        REM Clean up clone
                        cd ..
                        rd /s /q argocd-demo-app

                        echo GitOps repo updated successfully with tag %IMAGE_TAG%
                    """
                }
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
            GitOps  : https://github.com/Chandra-Reddy1/argocd-demo-app
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