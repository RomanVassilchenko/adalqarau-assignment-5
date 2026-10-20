pipeline {
    agent any
    triggers { pollSCM('H/2 * * * *') }
    options { timestamps() }
    stages {
        stage('Unit tests') {
            steps {
                sh 'python3 -m unittest -v'
            }
        }
        stage('Build image') {
            steps {
                sh 'docker build --tag adalqarau-a5:${BUILD_NUMBER} .'
            }
        }
        stage('Smoke run') {
            steps {
                sh "docker run --rm adalqarau-a5:${BUILD_NUMBER} sh -c 'python processor.py testdata/contracts.csv /tmp/summary.csv && cat /tmp/summary.csv' > summary.csv"
                sh 'cmp summary.csv testdata/expected-yearly-summary.csv'
                sh 'cat summary.csv'
            }
        }
    }
    post {
        always { archiveArtifacts artifacts: 'testdata/contracts.csv,summary.csv', fingerprint: true }
    }
}
