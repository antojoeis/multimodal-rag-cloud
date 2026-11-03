# Git & GitHub Manual: multimodal-rag-cloud

How to create the GitHub repo, push this project, and keep the PC and the
test device (<device-ip>) in sync.

```
 Windows PC (write code)  --push-->  GitHub  --pull-->  Ubuntu test device (run it)
```

---

## 1. Create the repository on GitHub (one time)

1. Sign in at https://github.com
2. Click **+** (top right) → **New repository**
3. Fill in:
   - **Repository name:** `multimodal-rag-cloud`
   - **Description:** `Multimodal RAG service: local VLM (Ollama) to cloud (AWS), with Terraform and CI/CD`
   - **Public** (recruiters can see it)
   - Do **not** tick "Add a README", ".gitignore" or "license". The project already has them.
4. Click **Create repository**. Keep the page open; it shows your repo URL:
   `https://github.com/antojoeis/multimodal-rag-cloud.git`

---

## 2. Log in to GitHub from the command line (one time per machine)

GitHub no longer accepts your account password for `git push`. Use a
**Personal Access Token (PAT)**:

1. GitHub → profile picture → **Settings** → **Developer settings**
   → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**
2. Name: `multimodal-rag-cloud`, Expiration: 90 days
3. Repository access: **Only select repositories** → `multimodal-rag-cloud`
4. Permissions → Repository → **Contents: Read and write**
5. Generate and **copy the token** (it's shown only once)

When `git push` asks for a password, paste the token.

- **Windows PC:** Git Credential Manager saves it after the first push.
- **Ubuntu device:** run `git config --global credential.helper store` once,
  and the token is saved after the first push. It is stored in plain text in
  `~/.git-credentials`, so only do this on a machine you trust.

---

## 3. Set your name and email (one time per machine)

The PC is already configured (`antojoeis` / `antojoeis@gmail.com`). On the
Ubuntu device:

```bash
git config --global user.name  "antojoeis"
git config --global user.email "antojoeis@gmail.com"
git config --global init.defaultBranch main
```

Check with `git config --global --list`.

---

## 4. First push from the Windows PC

In PowerShell, inside `D:\AI project\MY\multimodal-rag-cloud`:

```powershell
git init
git add .
git status                 # check: no .env, no .venv, no work images
git commit -m "Week 1: FastAPI + Ollama VLM MVP"
git branch -M main
git remote add origin https://github.com/antojoeis/multimodal-rag-cloud.git
git push -u origin main
```

Refresh the GitHub page. Your files and README should appear.

---

## 5. Get the code onto the test device

```bash
ssh test@<device-ip>
sudo apt install -y git          # if not installed yet
cd ~
rm -rf multimodal-rag-cloud      # only if the folder is still empty
git clone https://github.com/antojoeis/multimodal-rag-cloud.git
cd multimodal-rag-cloud
```

---

## 6. Daily workflow

**On the PC, after changing code:**

```powershell
git status                      # what changed?
git add .
git commit -m "Add image size check to /ask"
git push
```

**On the device, to get the latest code:**

```bash
cd ~/multimodal-rag-cloud
git pull
```

Rule of thumb: **edit on the PC, only pull on the device.** If you do edit on
the device, commit and push there, then `git pull` on the PC before you edit
again, or you'll get conflicts.

---

## 7. Good commit messages

Recruiters read your history. Write what changed, in the present tense:

| Good | Bad |
|---|---|
| `Add Whisper speech-to-text endpoint` | `update` |
| `Fix timeout when Ollama runs on CPU` | `fix bug` |
| `Week 3: add CLIP image embeddings to RAG` | `changes` |

Commit small and often, at least once per working session.

---

## 8. Branches for bigger features (optional, from Week 3)

```bash
git checkout -b week3-rag        # new branch
# ...work, commit...
git push -u origin week3-rag
```

Then on GitHub open a **Pull Request** from `week3-rag` into `main`, review
your own diff, and merge. This shows a professional workflow on your profile.

---

## 9. What never goes into Git

Already covered by `.gitignore`. Check `git status` before each commit anyway:

- `.env` (hosts, keys, future AWS credentials)
- `.venv/`, `__pycache__/`
- **Work images, logs and screenshots from the company.** Keep test images in
  a `data/` folder (ignored) and describe failures in text instead.
- Passwords, tokens, AWS keys. If one is ever committed, **revoke it
  immediately**. Deleting the file is not enough, because it stays in the
  history.

---

## 10. Fixing common problems

| Problem | Fix |
|---|---|
| `remote origin already exists` | `git remote set-url origin <url>` |
| `Authentication failed` | Token expired or wrong scope. Make a new PAT (section 2) |
| `rejected ... fetch first` | Someone pushed first: `git pull --rebase`, then `git push` |
| Committed the wrong file (not pushed yet) | `git reset --soft HEAD~1`, fix it, commit again |
| Want to discard local changes to a file | `git restore <file>` |
| See history | `git log --oneline --graph` |
