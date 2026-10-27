#!/usr/bin/env bash
# Start a disposable Jenkins controller, run the Jenkinsfile for the current
# Git commit, and save the build record in jenkins-evidence/.
# Used by GitHub Actions on every push; works the same way locally.
# KEEP_JENKINS=1 leaves Jenkins running at http://127.0.0.1:18080 afterwards.
set -euo pipefail
cd "$(dirname "$0")/.."
repo=$(pwd)
commit=${GIT_COMMIT_SHA:-$(git rev-parse HEAD)}
url=http://127.0.0.1:18080
name=adalqarau-a5-jenkins-ci
image=adalqarau-a5-jenkins:ci

cleanup() {
    if [[ ${KEEP_JENKINS:-0} != 1 ]]; then
        docker rm -f "$name" >/dev/null 2>&1 || true
        docker rm -f adalqarau-a5-test >/dev/null 2>&1 || true
    fi
}
trap cleanup EXIT

if [[ -n $(git status --porcelain) ]]; then
    echo "Note: uncommitted changes are not tested; Jenkins builds commit $commit." >&2
fi

docker build --tag "$image" ci/jenkins
docker rm -f "$name" >/dev/null 2>&1 || true
socket_gid=$(docker run --rm --entrypoint stat --volume /var/run/docker.sock:/var/run/docker.sock "$image" -c '%g' /var/run/docker.sock)
docker run --detach --name "$name" \
    --publish 127.0.0.1:18080:18080 \
    --group-add "$socket_gid" \
    --volume /var/run/docker.sock:/var/run/docker.sock \
    --volume "$repo:/repo:ro" \
    --env GIT_COMMIT_SHA="$commit" \
    "$image" >/dev/null

echo "Waiting for Jenkins on $url ..."
for attempt in $(seq 1 90); do
    if docker exec "$name" curl -fsS http://127.0.0.1:18080/job/assignment5/api/json >/dev/null 2>&1; then
        break
    fi
    if [[ $attempt == 90 ]]; then
        docker logs "$name"
        exit 1
    fi
    sleep 2
done

status=0
docker exec "$name" sh -c 'curl -fsS -o /tmp/jenkins-cli.jar http://127.0.0.1:18080/jnlpJars/jenkins-cli.jar &&
    java -jar /tmp/jenkins-cli.jar -s http://127.0.0.1:18080/ -webSocket build assignment5 -s -v' || status=$?

mkdir -p jenkins-evidence
api=http://127.0.0.1:18080/job/assignment5/lastBuild
docker exec "$name" curl -fsS "$api/api/json?pretty=true" > jenkins-evidence/build.json || true
docker exec "$name" curl -fsS "$api/consoleText" > jenkins-evidence/console.txt || true
docker exec "$name" curl -fsS "$api/artifact/summary.csv" > jenkins-evidence/summary.csv || true
echo "Jenkins build for $commit finished with exit code $status; record saved in jenkins-evidence/"
if [[ ${KEEP_JENKINS:-0} == 1 ]]; then
    echo "Jenkins is still running: $url/job/assignment5/"
    echo "Stop it with: docker rm -f $name adalqarau-a5-test"
fi
exit "$status"
