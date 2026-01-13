#!/bin/bash

set -e

echo "=== 备份原 sources.list ==="
cp /etc/apt/sources.list /etc/apt/sources.list.bak.$(date +%s)

echo "=== 写入 Debian 9 Archive 源 ==="
cat > /etc/apt/sources.list <<EOF
deb http://archive.debian.org/debian stretch main contrib non-free
deb http://archive.debian.org/debian-security stretch/updates main contrib non-free
deb http://archive.debian.org/debian stretch-updates main contrib non-free
EOF

echo "=== 更新软件包列表（Debian 9） ==="
apt-get -o Acquire::Check-Valid-Until=false update

echo "=== 升级 Debian 9 到最新（EOL） ==="
apt-get -y dist-upgrade

echo "=== 切换到 Debian 10（Buster）源 ==="
cat > /etc/apt/sources.list <<EOF
deb http://deb.debian.org/debian buster main contrib non-free
deb http://deb.debian.org/debian-security buster/updates main contrib non-free
deb http://deb.debian.org/debian buster-updates main contrib non-free
EOF

echo "=== 更新软件包列表（Debian 10） ==="
apt-get update

echo "=== 开始升级到 Debian 10 ==="
apt-get -y dist-upgrade

echo "=== 自动清理 ==="
apt-get autoremove -y
apt-get clean

echo "=== 升级完成，建议重启 ==="
echo "执行 reboot 重启系统"
