#!/usr/bin/env bash
set -euo pipefail

repo_dir="/home/mg/git/Allegro-Smart-Coffee-Price-Tracker"
unit_dir="$HOME/.config/systemd/user"

mkdir -p "$unit_dir"
ln -sfn "$repo_dir/deployment/systemd/coffee-observer.service" \
  "$unit_dir/coffee-observer.service"
systemctl --user daemon-reload
systemctl --user enable --now coffee-observer.service
systemctl --user --no-pager status coffee-observer.service
