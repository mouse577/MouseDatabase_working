
# 🧠 Git Cheat Sheet (Developer Essentials)

---

## 🔍 STATUS & INFO

```bash
git status                     # Show current changes
git log                        # Show commit history
git diff                       # Show unstaged changes
git diff --staged              # Show staged changes
git branch                     # List local branches
git branch -a                  # List local + remote branches
git remote -v                  # Show connected remotes
```

---

## 🔄 CLONE & SYNC

```bash
git clone <repo-url>               # Clone a remote repo
git pull origin <branch>           # Pull latest changes
git push origin <branch>           # Push changes
git push --set-upstream origin <branch>  # Push a new branch for the first time
```

---

## ✍️ STAGE & COMMIT

```bash
git add <file1> <file2>            # Stage specific files
git add .                          # Stage all current directory changes
git commit -m "Message"            # Commit staged changes
git commit -am "Msg"               # Stage & commit tracked files
```

---

## 🌿 BRANCHING

```bash
git checkout <branch>             # Switch to existing branch
git checkout -b <new-branch>      # Create & switch to new branch
git branch -d <branch>            # Delete local branch
```

---

## 🔁 UNDO / RESET

```bash
git reset --soft HEAD~1           # Undo last commit, keep changes staged
git reset --mixed HEAD~1          # Undo commit, keep changes unstaged
git reset --hard HEAD~1           # Undo commit, discard changes (⚠️ destructive)

git reset HEAD <file>             # Unstage a specific file
git clean -fd                     # Delete untracked files/folders

git stash                         # Save uncommitted changes
git stash pop                     # Re-apply stashed changes
```

---

## 🚫 UNPUSH CHANGES (⚠️ Force Push Warning)

```bash
git reset --soft HEAD~1           # Undo last commit locally
git push --force                  # Force push to overwrite remote
```

---

## 👥 REMOTES & ALIASES

```bash
git remote add origin <url>       # Add a remote origin
git remote set-url origin <url>   # Change remote URL

# Aliases (optional shortcuts)
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.cm "commit -m"
```

---

## 🔐 .gitignore Examples

```
# Python
__pycache__/
*.py[cod]
.env

# Node
node_modules/

# VSCode
.vscode/

# Mac
.DS_Store
```
