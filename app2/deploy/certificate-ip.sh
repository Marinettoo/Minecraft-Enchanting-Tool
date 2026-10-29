#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

config=/home/ubuntu/.config/met-app2
lineage=/etc/letsencrypt/live/met-app2-ip

copy_certificate() {
    install -d -m 0750 -o root -g 10001 "$config/tls"
    install -m 0640 -o root -g 10001 "$lineage/fullchain.pem" "$config/tls/fullchain.pem"
    install -m 0640 -o root -g 10001 "$lineage/privkey.pem" "$config/tls/privkey.pem"
}

if [ "${1:-}" = deploy ]; then
    # Certbot llama a esta opción después de renovar el certificado.
    [ "${RENEWED_LINEAGE:-}" = "$lineage" ] || exit 0
    copy_certificate
    if docker container inspect met-app2-https-app-1 >/dev/null 2>&1; then
        docker restart met-app2-https-app-1 >/dev/null
    fi
    exit 0
fi

exec 8>/run/lock/met-app2-certificate.lock
flock -w 120 8
metadata_token=$(curl --fail --silent --show-error --max-time 5 --request PUT \
    --header 'X-aws-ec2-metadata-token-ttl-seconds: 60' \
    http://169.254.169.254/latest/api/token)
public_ip=$(curl --fail --silent --show-error --max-time 5 \
    --header "X-aws-ec2-metadata-token: $metadata_token" \
    http://169.254.169.254/latest/meta-data/public-ipv4)
python3 -c 'import ipaddress,sys; assert ipaddress.IPv4Address(sys.argv[1]).is_global' "$public_ip"

renewal_option=--keep-until-expiring
if [ -f "$lineage/fullchain.pem" ] \
    && ! openssl x509 -in "$lineage/fullchain.pem" -checkip "$public_ip" -noout >/dev/null; then
    renewal_option=--force-renewal
fi

/snap/bin/certbot certonly --standalone --preferred-profile shortlived \
    --ip-address "$public_ip" --cert-name met-app2-ip "$renewal_option" \
    --non-interactive --agree-tos --register-unsafely-without-email >&2
copy_certificate

# Solo se actualizan datos públicos; las claves existentes se conservan.
python3 - "$public_ip" <<'PY'
import os
from pathlib import Path
import sys

config = Path('/home/ubuntu/.config/met-app2')
p = config / 'compose.env'
lines = p.read_text().splitlines()
updates = {'DOCKER_ALLOWED_ORIGINS': 'https://' + sys.argv[1]}
lines = [line for line in lines if line.split('=', 1)[0] not in updates]
lines.extend(f'{key}={value}' for key, value in updates.items())
p.write_text('\n'.join(lines) + '\n')
os.chmod(p, 0o600)
(config / 'public-ip').write_text(sys.argv[1] + '\n')
os.chown(config / 'public-ip', 1000, 1000)
os.chmod(config / 'public-ip', 0o600)
PY
printf '%s\n' "$public_ip"
