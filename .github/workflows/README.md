# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated testing and deployment.

## Workflows

### Dev Deployment (`.github/workflows/dev-deploy.yml`)
- **Trigger**: Pushes to `dev` branch or manual dispatch
- **Port**: 49081
- **Directory**: `/opt/tailnumberlookup-dev`
- **Service Name**: `faa-api-dev`

### Prod Deployment (`.github/workflows/prod-deploy.yml`)
- **Trigger**: Pushes to `main` branch or manual dispatch
- **Port**: 49080
- **Directory**: `/opt/tailnumberlookup-prod`
- **Service Name**: `faa-api-prod`

## Setup Required

### GitHub Secrets

You need to add the following secret to your GitHub repository:

1. Go to Settings → Secrets and variables → Actions
2. Add a new secret named `SSH_PRIVATE_KEY`
3. Paste the contents of your SSH private key: `~/.ssh/keys/nirdclub__id_ed25519`

```bash
# To copy your key for GitHub:
cat ~/.ssh/keys/nirdclub__id_ed25519
```

## Workflow Process

Both workflows follow the same process:

1. **Test Job**: Runs unit tests using pytest
   - Installs dependencies
   - Runs all tests in `tests/` directory
   - Generates coverage report
   - **Deployment will fail if tests fail**

2. **Deploy Job**: Deploys via Ansible (only runs after tests pass)
   - Sets up SSH connection
   - Installs Ansible
   - Runs Ansible playbook with environment-specific variables
   - Verifies deployment by checking health endpoint

## Branch Structure

The repository uses two main branches:
- **`dev`**: Development branch - deploys to dev environment
- **`main`**: Production branch - deploys to prod environment

**Workflow:**
1. Make changes and commit to `dev` branch
2. Push `dev` → triggers dev deployment (if tests pass)
3. Merge `dev` into `main` when ready for production
4. Push `main` → triggers prod deployment (if tests pass)

## Manual Deployment

You can manually trigger deployments from the GitHub Actions tab:
- Go to Actions → Select the workflow → Run workflow

## Testing Locally

Before pushing, you can run tests locally:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=term-missing
```

