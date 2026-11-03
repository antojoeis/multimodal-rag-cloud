# Device Setup Manual: Ubuntu GPU Test Machine

How the Ubuntu test device was prepared to run this project with a local
vision-language model on its NVIDIA GPU.

| Item | Value |
|---|---|
| OS | Ubuntu 24.04.5 LTS (upgraded from 22.04), kernel 6.8 |
| CPU | Intel Core i7-8700K, 6 cores / 12 threads |
| RAM | 16 GB |
| GPU | NVIDIA GeForce GTX 1660, 6 GB VRAM |
| Driver | `nvidia-driver-595-open` 595.99.02, CUDA 13.2 |
| Python | 3.12.3 |

---

## 1. Enable SSH (on the device, one time)

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
sudo ufw allow ssh            # only if ufw is active
sudo ss -tlnp | grep :22      # should show sshd on 0.0.0.0:22
ip -4 addr                    # note the device IP
```

From the PC: `ssh <user>@<device-ip>`

**Optional, key login instead of a password (on the Windows PC):**

```powershell
ssh-keygen -t ed25519
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh <user>@<device-ip> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

---

## 2. Check before installing anything

```bash
lsb_release -ds                       # OS version
lspci | grep -iE "vga|3d"             # is an NVIDIA GPU present?
mokutil --sb-state                    # Secure Boot state
ubuntu-drivers devices | grep recommended
```

- **Secure Boot disabled:** the driver loads directly. This was the case here.
- **Secure Boot enabled:** apt asks you to set a MOK password, and you must
  approve the key on the device's screen at the next reboot. Do this at the
  console, not over SSH.

If `apt` says `Could not get lock /var/lib/dpkg/lock-frontend`, find out who
holds it before doing anything:

```bash
sudo fuser -v /var/lib/dpkg/lock-frontend
ps -eo pid,etime,args | grep -E "apt|dpkg|release-upgrade" | grep -v grep
```

Here it was an Ubuntu release upgrade waiting on a dialog on the device's
screen. **Never kill an apt, dpkg or upgrade process.** Finish or cancel it at
the console.

---

## 3. Install the NVIDIA driver and base tools

```bash
sudo apt update
sudo apt install -y nvidia-driver-595-open git curl python3-pip python3-venv
sudo reboot
```

- Use the version that `ubuntu-drivers devices` marks as **recommended**.
- `-open` (open kernel modules) works on Turing (GTX 16xx / RTX 20xx) and newer.
  For older GPUs, use the non-`open` package.

---

## 4. Verify the GPU after reboot

```bash
nvidia-smi                      # should list the GTX 1660, 6144MiB
lsmod | grep -E "^nvidia|^nouveau"
```

Expected: an `nvidia` module, **no** `nouveau`.

| Problem | Fix |
|---|---|
| `nvidia-smi: command not found` | Driver not installed. Repeat step 3 |
| `NVIDIA-SMI has failed ... couldn't communicate with the driver` | Not rebooted yet, or Secure Boot blocked the module (see step 2) |
| `nouveau` still loaded | `sudo apt install --reinstall nvidia-driver-595-open && sudo reboot` |
| Black screen after reboot | Boot the recovery kernel, `sudo apt purge 'nvidia-*'`, reboot, try the next recommended version |

---

## 5. Install Ollama and the vision model

```bash
curl -fsSL https://ollama.com/install.sh | sh
systemctl status ollama          # should be active (running)
ollama pull qwen2.5vl:3b         # ~3 GB, fits fully in 6 GB VRAM
ollama run qwen2.5vl:3b "Say hello"
ollama ps                        # PROCESSOR column should say 100% GPU
```

Model choice for a 6 GB GPU:

| Model | Fits in VRAM? | Use |
|---|---|---|
| `qwen2.5vl:3b` | Yes, fast | Daily testing |
| `qwen2.5vl:7b` | Partly, spills to CPU, slower | Quality comparison |

To let the Windows PC call Ollama on the device (optional):

```bash
sudo systemctl edit ollama
# add:
# [Service]
# Environment="OLLAMA_HOST=0.0.0.0:11434"
sudo systemctl restart ollama
```

Only do this on a trusted network. Ollama has no authentication.

---

## 6. Get the project and run it

```bash
cd ~
git clone https://github.com/antojoeis/multimodal-rag-cloud.git
cd multimodal-rag-cloud
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
sed -i 's/qwen2.5vl:7b/qwen2.5vl:3b/' .env
pytest -q                                     # 5 passed
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://<device-ip>:8000/docs` from the PC, choose **/ask**, upload an
image and ask a question. Watch the GPU in a second terminal with
`watch -n1 nvidia-smi`.

Get new code later with `git pull` (see [GIT_MANUAL.md](GIT_MANUAL.md)).
