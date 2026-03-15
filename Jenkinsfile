pipeline {
    agent any

    environment {
        IMAGE_NAME             = "welcome-login-app"
        IMAGE_TAG              = "${BUILD_NUMBER}"
        CONTAINER_NAME         = "welcome-login-app"
        APP_PORT               = "5000"
        DOCKERHUB_CREDENTIALS  = credentials('dockerhub-credentials')  // 👈 Jenkins credential ID
        // credentials() auto-generates:
        //   DOCKERHUB_CREDENTIALS_USR  → your Docker Hub username
        //   DOCKERHUB_CREDENTIALS_PSW  → your Docker Hub password
    }

    stages {

        stage('Checkout') {
            steps {
                echo '📥 Checking out source code...'
                checkout scm
            }
        }

        stage('Verify Files') {
            steps {
                echo '🔍 Verifying required files exist...'
                sh '''
                    test -f app.py           && echo "✅ app.py found"           || (echo "❌ app.py missing!"     && exit 1)
                    test -f Dockerfile       && echo "✅ Dockerfile found"       || (echo "❌ Dockerfile missing!" && exit 1)
                    test -f requirements.txt && echo "✅ requirements.txt found" || (echo "❌ requirements.txt missing!" && exit 1)
                '''
            }
        }

        stage('Docker Login') {
            steps {
                echo '🔐 Logging in to Docker Hub...'
                sh "echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin"
                echo '✅ Docker login successful'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "🐳 Building Docker image: ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:${IMAGE_TAG}..."
                sh '''
                    docker build -t ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag  ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:${IMAGE_TAG} \
                                ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:latest
                    echo "✅ Image built successfully"
                '''
            }
        }

        stage('Test Container') {
            steps {
                echo '🧪 Running smoke test...'
                sh '''
                    docker run -d --name test-${IMAGE_NAME}-${BUILD_NUMBER} \
                        -p 5001:5000 ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:${IMAGE_TAG}

                    sleep 5

                    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/health)

                    docker stop test-${IMAGE_NAME}-${BUILD_NUMBER}
                    docker rm   test-${IMAGE_NAME}-${BUILD_NUMBER}

                    if [ "$HTTP_STATUS" = "200" ]; then
                        echo "✅ Health check passed (HTTP $HTTP_STATUS)"
                    else
                        echo "❌ Health check failed (HTTP $HTTP_STATUS)"
                        exit 1
                    fi
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo '📤 Pushing image to Docker Hub...'
                sh '''
                    docker push ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:latest
                    echo "✅ Image pushed to Docker Hub"
                    echo "🔗 https://hub.docker.com/r/${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}"
                '''
            }
        }

        stage('Deploy Container') {
            steps {
                echo '🚀 Deploying container...'
                sh '''
                    if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
                        docker stop ${CONTAINER_NAME}
                    fi
                    if [ "$(docker ps -aq -f name=${CONTAINER_NAME})" ]; then
                        docker rm ${CONTAINER_NAME}
                    fi

                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        --restart unless-stopped \
                        -p ${APP_PORT}:5000 \
                        ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:${IMAGE_TAG}

                    echo "✅ Container deployed at http://localhost:${APP_PORT}"
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                echo '✅ Verifying deployment...'
                sh '''
                    sleep 3
                    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${APP_PORT}/health)
                    [ "$HTTP_STATUS" = "200" ] && echo "✅ Deployment verified!" || (echo "❌ Deployment failed!" && exit 1)
                '''
            }
        }
    }

    post {
        success {
            echo """
            ================================================
            ✅ BUILD & DEPLOY SUCCESSFUL
            ================================================
            Image   : ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:${IMAGE_TAG}
            App URL : http://localhost:${APP_PORT}
            Hub     : https://hub.docker.com/r/${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}
            Build   : #${BUILD_NUMBER}
            ================================================
            """
        }
        failure {
            echo '❌ Pipeline failed! Cleaning up...'
            sh 'docker rm -f test-${IMAGE_NAME}-${BUILD_NUMBER} 2>/dev/null || true'
        }
        always {
            echo '🔓 Logging out of Docker & cleaning old images...'
            sh '''
                docker logout || true
                docker images ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME} --format "{{.Tag}}" \
                | grep -E '^[0-9]+$' | sort -n | head -n -3 \
                | xargs -r -I {} docker rmi ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:{} 2>/dev/null || true
            '''
        }
    }
}