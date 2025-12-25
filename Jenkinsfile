pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
        }
    }

    stages {
        stage('Run Python in Container') {
            steps {
                sh '''
                  python --version
                  echo "Running inside Python container"
                '''
            }
        }
    }
}
