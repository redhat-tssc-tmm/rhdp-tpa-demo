# Ansible Runner for OpenShift

Pre-built container image with Ansible and OpenShift dependencies for faster job execution.

## What's Included

**Python packages:**
- ansible-core, ansible-runner
- kubernetes, openshift
- PyYAML, requests, jmespath

**Ansible collections:**
- kubernetes.core
- community.general
- community.crypto

## Building

```bash
podman login registry.redhat.io
podman build -t quay.io/rhpds/ansible-runner-ocp:latest .
podman push quay.io/rhpds/ansible-runner-ocp:latest
```

## Using in Field Content

Update `values.yaml` to use the pre-built image:

```yaml
image:
  repository: quay.io/rhpds/ansible-runner-ocp
  tag: latest
```

## Adding Custom Dependencies

**Option 1: Build your own image**

```dockerfile
FROM quay.io/rhpds/ansible-runner-ocp:latest

# Add Python packages
RUN pip install --no-cache-dir my-custom-package

# Add Ansible collections
RUN ansible-galaxy collection install my_namespace.my_collection
```

**Option 2: Install at runtime**

Keep custom collections in `values.yaml` - they'll be installed when the job runs:

```yaml
ansible:
  collections:
    - my_namespace.my_collection:==1.0.0
```

The pre-installed collections are skipped, only new ones are downloaded.
