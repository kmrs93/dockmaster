# ⚓ DockMaster

**DockMaster** is a lightweight, high-performance Docker Compose manager designed for Raspberry Pi and home servers. It provides a sleek UI to manage stacks, edit configurations, and monitor system health.

---

## 🚀 Key Features

* **Global Environment Registry**: Manage one global `.env` file that syncs across all stacks.
* **Multi-Arch Support**: Native builds for `ARM64` (Raspberry Pi) and `AMD64`.
* **Live Terminals**: Real-time deployment logs and container output via WebSockets.
* **Stack Editor**: Built-in editor with an intelligent variable inspector and **Delete Stack** support.
* **System Monitor**: Real-time tracking of CPU, RAM, Disk, and CPU Temperature.

---

## 🛠 Quick Start

### 1. Requirements
* Docker & Docker Compose
* A projects directory (e.g., `~/DATA/stacks`)

### 2. Setup Environment Variables
Create a local `.env` file in your installation directory (this file should remain local and not be committed to Git):

# App Settings
DOCKER_HOST_IP=192.168.1.100
JWT_SECRET=your_32_bit_secret
DOCKMASTER_PASSWORD_HASH=$2b$12$agF1w3GGUyhadar2ZgYNLeMfadEiIe3auVoNMNPBg0TVAoC2mD0tK

# Path Mapping
STACKS_PATH=/home/kmrs93/DATA/stacks
CONFIG_PATH=/home/kmrs93/AppData/dockmaster/config
### 3. Deploy
Pull the image from the GitHub Container Registry and start:

'''Bash

docker compose pull
docker compose up -d
🌍 The Global .env Strategy
DockMaster implements a centralized environment management system:

Single Source of Truth: All stacks reference a single .env file at the root of your project directory.

Auto-Detection: The Stack Editor parses ${VARIABLES} from your docker-compose.yml and allows you to map them to the global registry instantly.

Portability: This ensures shared variables like TZ, PUID, or DOMAIN are managed globally rather than per-stack.

🛠 Tech Stack
Frontend: Vue 3 (Vite), Tailwind CSS, Xterm.js

Backend: FastAPI (Python), Docker SDK

CI/CD: GitHub Actions (Docker Buildx multi-platform)

📝 License
MIT


### Push to GitHub
Run these commands to finalize the update on your git page:

'''bash
git add README.md
git commit -m "docs: finalize readme with global env documentation"
git push origin main
