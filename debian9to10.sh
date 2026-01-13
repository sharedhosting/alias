#!/bin/bash
set -e

echo "=== 备份原 sources.list ==="
cp /etc/apt/sources.list /etc/apt/sources.list.bak.$(date +%s)

echo "=== 写入 Debian 9 Archive 源（无签名） ==="
cat > /etc/apt/sources.list <<EOF
deb [trusted=yes] http://archive.debian.org/debian stretch main contrib non-free
deb [trusted=yes] http://archive.debian.org/debian-security stretch/updates main contrib non-free
EOF

echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until
echo 'Acquire::AllowInsecureRepositories "true";' > /etc/apt/apt.conf.d/99insecure
echo 'Acquire::AllowDowngradeToInsecureRepositories "true";' >> /etc/apt/apt.conf.d/99insecure

echo "=== 更新 Debian 9（强制无签名） ==="
apt-get -o Acquire::Check-Valid-Until=false -o Acquire::AllowInsecureRepositories=true update
apt-get -y --allow-unauthenticated dist-upgrade

echo "=== 切换到 Debian 10（Buster）源 ==="
cat > /etc/apt/sources.list <<EOF
deb http://deb.debian.org/debian buster main contrib non-free
deb http://deb.debian.org/debian-security buster/updates main contrib non-free
deb http://deb.debian.org/debian buster-updates main contrib non-free
EOF

echo "=== 更新 Debian 10 ==="
apt-get update
apt-get -y dist-upgrade

echo "=== 清理 ==="
apt-get autoremove -y
apt-get clean

echo "=== 升级完成，请 reboot ==="
