#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

repo=/home/ubuntu/practicas-aws/Minecraft-Enchanting-Tool
config=/home/ubuntu/.config/met-app2
export GIT_TERMINAL_PROMPT=0
export COMPOSE_PARALLEL_LIMIT=1
https_mode=0
build_directory=
if [ -f "$config/https-ip" ]; then
    https_mode=1
fi

cd "$repo/app2"
exec 9>/home/ubuntu/.config/met-app2/update.lock
flock -n 9 || exit 0

compose() {
    if [ "$https_mode" = 1 ]; then
        compose_file="$repo/app2/compose.ec2.yaml"
        if [ ! -f "$compose_file" ]; then
            compose_file="$config/bootstrap/compose.ec2.yaml"
        fi
        sudo -n --preserve-env=MET_APP2_BUILD_CONTEXT docker compose \
            --project-directory "$repo/app2" --env-file "$config/compose.env" \
            -f "$compose_file" "$@"
    else
        sudo -n docker compose "$@"
    fi
}

cleanup() {
    if [[ "$build_directory" = /tmp/met-app2-build.* ]]; then
        rm -rf -- "$build_directory"
    fi
}
trap cleanup EXIT

recover() {
    status=$?
    trap - ERR
    printf '%s\n' 'No se ha completado la actualización. Se mantienen o arrancan los contenedores existentes.' >&2
    compose start || true
    exit "$status"
}
trap recover ERR

git -C "$repo" diff --quiet
git -C "$repo" diff --cached --quiet
timeout 120 git -C "$repo" fetch origin main
git -C "$repo" merge --ff-only origin/main
if [ "$https_mode" = 1 ]; then
    public_ip=$(sudo -n /usr/local/bin/met-app2-certificate)
    build_directory=$(mktemp -d /tmp/met-app2-build.XXXXXX)
    git -C "$repo" archive HEAD app2 | tar -x -C "$build_directory"
    # Permite la primera instalación antes del commit del equipo. Una vez
    # versionados, siempre se usan los archivos que llegan de GitHub.
    for file in Dockerfile.ec2 .dockerignore backend/app/web.py; do
        if [ ! -f "$build_directory/app2/$file" ]; then
            cp "$config/bootstrap/$file" "$build_directory/app2/$file"
        fi
    done
    export MET_APP2_BUILD_CONTEXT="$build_directory/app2"
fi
compose config --quiet
# Construir antes de sustituir los contenedores. No detener la versión en uso.
compose build
compose up -d --no-build --wait --wait-timeout 90
ready=0
for attempt in {1..30}; do
    base_url=http://127.0.0.1:8080
    curl_options=()
    if [ "$https_mode" = 1 ]; then
        base_url="https://$public_ip"
        curl_options=(--connect-to "$public_ip:443:127.0.0.1:443")
    fi
    if curl "${curl_options[@]}" --fail --silent --max-time 2 "$base_url/" >/dev/null \
        && [ "$(curl "${curl_options[@]}" --silent --max-time 2 --output /dev/null --write-out '%{http_code}' \
            --request POST "$base_url/api/procesar")" = 401 ]; then
        ready=1
        break
    fi
    sleep 2
done
test "$ready" = 1
printf 'App2 arrancada con la versión %s\n' "$(git -C "$repo" rev-parse --short HEAD)"
