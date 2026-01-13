# Team Setup Guide - AWS Hackathon Man07

## Quick Start for Team Members

### 1. Clone and Setup
```bash
git clone https://github.com/work2fly/AWS-hackathon-man07.git
cd AWS-hackathon-man07
git checkout develop
```

### 2. Configure Git (First Time Only)
```bash
# Set your name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Helpful aliases
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.st status
```

### 3. Daily Workflow

#### Starting Work
```bash
# Always start from develop
git checkout develop
git pull origin develop

# Create your feature branch
git checkout -b feature/your-feature-name
```

#### During Work
```bash
# Commit frequently
git add .
git commit -m "feat: describe what you did"

# Push to backup your work
git push origin feature/your-feature-name
```

#### Finishing Work
1. Push your final changes
2. Go to GitHub and create a Pull Request to `develop`
3. Ask a teammate to review
4. Merge after approval

### 4. Branch Naming Examples
- `feature/user-authentication`
- `feature/aws-lambda-setup`
- `feature/frontend-dashboard`
- `feature/database-integration`
- `feature/api-endpoints`

### 5. Commit Message Format
- `feat: add user login functionality`
- `fix: resolve AWS connection timeout`
- `docs: update API documentation`
- `refactor: improve error handling`
- `test: add unit tests for auth`

### 6. Need Help?
- Check `BRANCHING_STRATEGY.md` for detailed workflow
- Ask in team chat before force-pushing
- When in doubt, create a PR and ask for review

### 7. Emergency Commands
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard all local changes
git checkout -- .

# Switch branches with uncommitted changes
git stash
git checkout other-branch
git stash pop
```

## Team Roles (Rotate Daily)

### Integrator (Today's Responsibility)
- [ ] Monitor develop branch
- [ ] Merge approved PRs
- [ ] Handle merge conflicts
- [ ] Deploy to staging/demo

### Everyone Else
- [ ] Review at least 1 PR per day
- [ ] Keep feature branches small
- [ ] Test before pushing
- [ ] Communicate blockers early

## Quick Reference

| Command | What it does |
|---------|-------------|
| `git status` | See what's changed |
| `git log --oneline` | See recent commits |
| `git branch -a` | See all branches |
| `git checkout develop` | Switch to develop |
| `git pull origin develop` | Get latest changes |
| `git push origin branch-name` | Push your branch |

Remember: We're here to build something awesome together! 🚀