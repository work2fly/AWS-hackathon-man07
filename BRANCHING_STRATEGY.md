# Branching Strategy - AWS Hackathon Man07

## Overview
This document outlines the Git branching strategy for our 5-person AWS hackathon team to ensure smooth collaboration and minimize merge conflicts.

## Branch Structure

### Main Branches
- **`main`** - Production-ready code, always deployable
- **`develop`** - Integration branch for features, staging environment

### Supporting Branches
- **`feature/*`** - Individual feature development
- **`hotfix/*`** - Critical fixes that need immediate deployment
- **`release/*`** - Prepare releases (if needed for hackathon milestones)

## Workflow

### 1. Feature Development
```bash
# Start new feature from develop
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name

# Work on your feature
git add .
git commit -m "feat: add your feature description"

# Push and create PR to develop
git push origin feature/your-feature-name
```

### 2. Integration
- All features merge into `develop` via Pull Requests
- `develop` is merged into `main` for releases/demos

### 3. Hotfixes (if needed)
```bash
# Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix

# Fix and merge back to both main and develop
```

## Branch Naming Conventions

### Features
- `feature/user-authentication`
- `feature/aws-lambda-integration`
- `feature/frontend-dashboard`
- `feature/data-processing-pipeline`

### Team Member Prefixes (Optional)
- `feature/john/user-auth`
- `feature/sarah/lambda-functions`
- `feature/mike/frontend-ui`

## Pull Request Guidelines

### Required for ALL merges to develop/main
1. **Code Review** - At least 1 team member approval
2. **Testing** - Ensure your code works locally
3. **Description** - Clear description of changes
4. **No Direct Pushes** - Always use PRs for develop/main

### PR Template
```
## What does this PR do?
Brief description of changes

## How to test?
Steps to verify the changes work

## Checklist
- [ ] Code works locally
- [ ] No console errors
- [ ] Follows team coding standards
- [ ] Updated documentation if needed
```

## Daily Workflow

### Morning Sync
```bash
git checkout develop
git pull origin develop
# Start your feature branch from latest develop
```

### End of Day
```bash
# Commit your work
git add .
git commit -m "wip: progress on feature X"
git push origin feature/your-branch
```

## Merge Strategy
- **Squash and Merge** for feature branches (keeps history clean)
- **Merge Commit** for develop → main (preserves feature history)

## Emergency Protocols

### Broken Develop Branch
1. Identify the breaking commit
2. Create hotfix branch from last working commit
3. Fix and merge back
4. Notify team immediately

### Merge Conflicts
1. Pull latest develop: `git pull origin develop`
2. Resolve conflicts locally
3. Test thoroughly
4. Push resolved version

## Team Responsibilities

### Everyone
- Keep feature branches small and focused
- Commit frequently with clear messages
- Test before pushing
- Review others' PRs promptly

### Designated Integrator (rotate daily)
- Monitor develop branch health
- Merge approved PRs
- Handle any integration issues
- Deploy to staging/demo environment

## Quick Commands Cheat Sheet

```bash
# Setup
git clone https://github.com/work2fly/AWS-hackathon-man07.git
cd AWS-hackathon-man07

# Daily start
git checkout develop && git pull origin develop
git checkout -b feature/my-new-feature

# Daily end
git add . && git commit -m "feat: describe your work"
git push origin feature/my-new-feature

# Switch between features
git stash                    # save current work
git checkout other-branch    # switch
git stash pop               # restore work later
```

## Tools & Automation

### Recommended Git Aliases
```bash
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.unstage 'reset HEAD --'
```

### GitHub Settings
- Enable branch protection on `main` and `develop`
- Require PR reviews
- Require status checks to pass
- Dismiss stale reviews when new commits are pushed

## Hackathon-Specific Notes

- **Demo Branch**: Create `demo/presentation` before final presentation
- **Backup Strategy**: Tag important milestones
- **Quick Fixes**: Use hotfix branches even for small issues during crunch time
- **Communication**: Use PR comments for quick team updates

Remember: The goal is to move fast while staying organized. When in doubt, communicate with the team!