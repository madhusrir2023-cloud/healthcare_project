pipeline {
    agent any

    stages {

        stage('Clone Code') {
            steps {
                echo 'Cloning from GitHub...'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Test Code') {
            steps {
                bat 'python -m py_compile app.py'
            }
        }

        stage('Finish') {
            steps {
                echo 'Build Completed Successfully!'
            }
        }

    }
}
