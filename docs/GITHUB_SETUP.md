# GitHub Setup & Remote Deployment Guide

## Repository: `SIH26083-Heat-Risk`

This repository is maintained on GitHub under:
`https://github.com/fatehbrar07/SIH26083-Heat-Risk`

---

### Push & Synchronization Commands

To push local commits to GitHub:

```bash
cd /home/ubuntu/sih26083-heat-risk

# Check git status
git status

# Stage changes
git add .

# Commit with conventional commit format
git commit -m "feat: complete SIH26083 prototype with scientific biometeorology, GIS, and API"

# Push to GitHub main branch
git push -u origin main
```

---

### Initial Setup (If recreating on a new machine)

```bash
# Initialize local repo
git init -b main
git remote add origin https://github.com/fatehbrar07/SIH26083-Heat-Risk.git
git add .
git commit -m "feat: initial prototype release for SIH26083"
git push -u origin main
```
