pipeline {
    agent {
        docker {
            image 'nginx:alpine'
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
