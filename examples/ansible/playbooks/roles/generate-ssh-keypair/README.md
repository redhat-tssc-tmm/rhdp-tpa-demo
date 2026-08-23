# Generate SSH Keypair Role

Generates an SSH keypair, stores the public key as an OpenShift secret, and makes the private key available for userinfo.

## Usage

```yaml
- name: Generate SSH keypair
  vars:
    ssh_keypair_namespace: "my-namespace"
    ssh_keypair_secret_name: "my-ssh-key"
  ansible.builtin.include_role:
    name: generate-ssh-keypair

# The private key is now available in the ssh_private_key variable
- name: Create userinfo with private key
  kubernetes.core.k8s:
    state: present
    definition:
      apiVersion: v1
      kind: ConfigMap
      metadata:
        name: my-userinfo
        labels:
          demo.redhat.com/userinfo: ""
      data:
        ssh_private_key: "{{ ssh_private_key }}"
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ssh_keypair_namespace` | `default` | Namespace for the public key secret |
| `ssh_keypair_secret_name` | `ssh-keypair` | Name of the secret |
| `ssh_keypair_type` | `rsa` | Key type (rsa, ed25519, etc.) |
| `ssh_keypair_size` | `4096` | Key size in bits |
| `ssh_keypair_comment` | `generated-by-ansible` | Comment added to the key |

## Output Variables

After running this role, the following variables are available:

- `ssh_private_key` - The full private key (PEM format)
- `ssh_public_key` - The public key (single line)

## Requirements

This role requires the `community.crypto` collection:

```yaml
# requirements.yml
collections:
  - community.crypto
```
