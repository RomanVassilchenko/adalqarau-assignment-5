pipeline {
    agent any
    triggers { pollSCM('H/2 * * * *') }
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
        stage('Deploy test') {
            steps {
                sh '''
                    if docker container inspect adalqarau-a5-test >/dev/null 2>&1; then
                        owner=$(docker inspect --format '{{ index .Config.Labels "edu.adalqarau.assignment" }}' adalqarau-a5-test)
                        test "$owner" = assignment5 || { echo "Refusing to replace unowned container"; exit 1; }
                        docker rm -f adalqarau-a5-test
                    fi
                    docker run --rm --network host --entrypoint python3 adalqarau-a5:${BUILD_NUMBER} -c "import socket; s=socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); s.bind(('127.0.0.1', 18081)); s.close()"
                    docker run --detach --name adalqarau-a5-test --label edu.adalqarau.assignment=assignment5 --publish 127.0.0.1:18081:8080 adalqarau-a5:${BUILD_NUMBER} sh -c 'mkdir -p /tmp/a5-results && python processor.py testdata/contracts.csv /tmp/a5-results/summary.csv && exec python3 -m http.server 8080 --bind 0.0.0.0 --directory /tmp/a5-results'
                    deployed_image=$(docker inspect --format '{{.Image}}' adalqarau-a5-test)
                    built_image=$(docker image inspect --format '{{.Id}}' adalqarau-a5:${BUILD_NUMBER})
                    test "$deployed_image" = "$built_image"
                    docker run --rm --network host --entrypoint python3 adalqarau-a5:${BUILD_NUMBER} smoke_deployment.py
                '''
            }
        }
    }
    post {
        always { archiveArtifacts artifacts: 'testdata/contracts.csv,summary.csv', fingerprint: true }
    }
}
