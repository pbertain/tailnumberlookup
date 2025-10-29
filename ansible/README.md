# Ansible Deployment for Tail Number Lookup

This directory contains Ansible playbooks and configuration for deploying the Tail Number Lookup application.

## Prerequisites

- Ansible installed on your local machine
- SSH access to the target server (host74.nird.club)
- SSH key: `~/.ssh/keys/nirdclub__id_ed25519`

## Deployment

### Standard Deployment Command

```bash
ansible-playbook --ask-vault-pass \
  -u ansible \
  --private-key ~/.ssh/keys/nirdclub__id_ed25519 \
  -i inventory.yml \
  playbook.yml
```

### Quick Deployment (if no vault password)

```bash
ansible-playbook \
  -u ansible \
  --private-key ~/.ssh/keys/nirdclub__id_ed25519 \
  -i inventory.yml \
  playbook.yml
```

## What the Playbook Does

1. **Installs dependencies**: Python 3, pip, and venv
2. **Creates directories**: `/opt/tailnumberlookup` and data directory
3. **Copies application files**: Rsyncs all files except `.git`, `data`, `venv`, etc.
4. **Sets up virtual environment**: Creates and configures Python venv
5. **Installs Python packages**: Installs all requirements from `requirements.txt`
6. **Initializes database**: Creates SQLite database if it doesn't exist
7. **Configures systemd services**:
   - `faa-api.service`: API server running on port 49080
   - `faa-sync.service`: Data sync service
   - `faa-sync.timer`: Runs sync 4 times daily
8. **Starts services**: Enables and starts both API and sync timer

## Manual Operations

### Check Service Status

```bash
ansible -i inventory.yml all -m shell -a "systemctl status faa-api" \
  -u ansible --private-key ~/.ssh/keys/nirdclub__id_ed25519
```

### View API Logs

```bash
ansible -i inventory.yml all -m shell -a "journalctl -u faa-api -n 50" \
  -u ansible --private-key ~/.ssh/keys/nirdclub__id_ed25519
```

### View Sync Logs

```bash
ansible -i inventory.yml all -m shell -a "journalctl -u faa-sync.service -n 50" \
  -u ansible --private-key ~/.ssh/keys/nirdclub__id_ed25519
```

### Manually Trigger Sync

```bash
ansible -i inventory.yml all -m shell -a "systemctl start faa-sync.service" \
  -u ansible --private-key ~/.ssh/keys/nirdclub__id_ed25519
```

## Variables

Key variables can be modified in `playbook.yml`:

- `app_directory`: `/opt/tailnumberlookup` (deployment path)
- `api_port`: `49080` (API server port)
- `app_user`: `ansible` (user to run services)

## Files

- `inventory.yml`: Ansible inventory with host configuration
- `playbook.yml`: Main deployment playbook
- `faa-api.service.j2`: Systemd service template for API
- `faa-sync.service.j2`: Systemd service template for sync

