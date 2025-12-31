# ⚓ DockMaster

**DockMaster** is a lightweight, high-performance Docker Compose manager designed for Raspberry Pi and home servers. It provides a sleek UI to manage stacks, edit configurations, and monitor system health.

---

## 🌐 Production Deployment

For a production environment, DockMaster is designed to run behind a Reverse Proxy (like Caddy or Nginx Proxy Manager) with secure authentication and persistent storage.

### 1. Prerequisites
- **Docker & Docker Compose** installed.
- **Reverse Proxy**: We recommend **Caddy** for automatic SSL.
- **GitHub Registry Access**: DockMaster is hosted on GHCR.

### 2. Prepare the Directory Structure
```bash
# Create the standard DockMaster structure
mkdir -p ~/dockmaster/config
mkdir -p ~/DATA/stacks
cd ~/dockmaster
```

###3. Configure the Environment
Create a local .env file. Important: Use a strong, unique secret for the JWT and a pre-hashed Bcrypt password.

```bash
# Public IP or Domain of your host
DOCKER_HOST_IP=your-server-ip-or-domain.com

# Authentication
# Generate via: openssl rand -hex 32
JWT_SECRET=4f92...a381
# Your hashed master password
DOCKMASTER_PASSWORD_HASH=$2b$12$agF1w3GGUyhadar2ZgYNLeMfadEiIe3auVoNMNPBg0TVAoC2mD0tK

# Path Mappings
STACKS_PATH=/home/kmrs93/DATA/stacks
CONFIG_PATH=/home/kmrs93/AppData/dockmaster/config
```

###4. Production Docker Compose
Save this as docker-compose.yml. This configuration mounts the Docker socket and host binaries to allow DockMaster to manage other containers on the host.

```YAML
services:
  dockmaster:
    image: ghcr.io/kmrs93/dockmaster:latest
    container_name: dockmaster
    restart: unless-stopped
    network_mode: "host"
    pid: "host"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker
      - /usr/libexec/docker/cli-plugins:/usr/libexec/docker/cli-plugins
      - ${STACKS_PATH}:/app/projects
      - ${CONFIG_PATH}:/app/config
      - /:/host:ro
    environment:
      - STACKS_ROOT=/app/projects
      - DOCKER_HOST_IP=${DOCKER_HOST_IP}
      - DOCKMASTER_PASSWORD_HASH=${DOCKMASTER_PASSWORD_HASH}
      - JWT_SECRET=${JWT_SECRET}
```

###5. Launch

```Bash
docker compose pull
docker compose up -d
```

###🔒 Security Best Practices
1. Firewall: Ensure port 5555 is only accessible via your internal network or your Reverse Proxy.
2. Docker Socket: Mounting /var/run/docker.sock gives the container root-level access to your host. Only deploy this on a secured server you control.
3. Password Hashing: Never store your password in plain text. Use a Bcrypt generator to create your DOCKMASTER_PASSWORD_HASH.

###📝 License
MIT
