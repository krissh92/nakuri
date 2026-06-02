# Naukri Profile Auto-Update Setup Guide

## Overview
This automation updates your Naukri profile's last active timestamp daily at 6 AM using Jenkins and GitHub.

---

## Step 1: Prerequisites
- Jenkins server installed and running
- GitHub account with repository access
- Git installed on Jenkins server
- Python 3.7+ installed
- Naukri account credentials

---

## Step 2: GitHub Repository Setup

### 2.1 Create GitHub Repository
```bash
# Create a new repo and clone it locally
git clone https://github.com/your-username/naukri-profile-updater.git
cd naukri-profile-updater
```

### 2.2 Add Files to Repository
Copy these files to your repository:
- `naukri_profile_updater.py` - Main Python script
- `Jenkinsfile` - Jenkins pipeline configuration
- `requirements.txt` - Python dependencies
- `.gitignore` - Ignore sensitive files

### 2.3 Create .gitignore
```
# Ignore credentials and logs
*.log
*.json
.env
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
ENV/
```

### 2.4 Push to GitHub
```bash
git add .
git commit -m "Initial commit: Naukri profile updater automation"
git push origin main
```

---

## Step 3: Jenkins Setup

### 3.1 Install Required Plugins
In Jenkins, go to **Manage Jenkins → Plugin Manager** and install:
- Git plugin
- GitHub plugin
- Email Extension Plugin (optional, for notifications)
- Pipeline plugin

### 3.2 Create Jenkins Credentials

#### Add GitHub Credentials:
1. Go to **Manage Jenkins → Manage Credentials**
2. Click **Global credentials (unrestricted)**
3. Click **Add Credentials**
   - Kind: **Username with password**
   - Username: Your GitHub username
   - Password: Your GitHub personal access token
   - ID: `github-credentials`

#### Add Naukri Credentials:
1. Add **String** type credentials:
   - Secret: Your Naukri email
   - ID: `naukri-email`
2. Add another **String** type credentials:
   - Secret: Your Naukri password
   - ID: `naukri-password`

> **Security Note**: Use Jenkins Credentials Store, never commit credentials to Git!

### 3.3 Create Jenkins Pipeline Job

1. Click **New Item**
2. Enter job name: `naukri-profile-updater`
3. Select **Pipeline**
4. Click **OK**

### 3.4 Configure Pipeline Job

In the job configuration page:

**Pipeline Section:**
```
Definition: Pipeline script from SCM
SCM: Git
  Repository URL: https://github.com/your-username/naukri-profile-updater.git
  Branch: main
  Credentials: Select your GitHub credentials
  
Script Path: Jenkinsfile
```

Click **Save**

---

## Step 4: Configure Automation Schedule

The Jenkinsfile already includes:
```groovy
triggers {
    cron('0 6 * * *')  // Runs daily at 6 AM
}
```

This uses Linux cron syntax:
- `0 6 * * *` = Every day at 6:00 AM
- `0 6 * * 1-5` = Monday to Friday at 6:00 AM
- `0 */6 * * *` = Every 6 hours

To modify the schedule:
1. Edit `Jenkinsfile`
2. Change the cron expression in the `triggers` section
3. Commit and push changes
4. Jenkins will automatically apply the new schedule

---

## Step 5: Test the Setup

### Manual Test:
1. Go to your Jenkins job
2. Click **Build Now**
3. Check **Console Output** for logs
4. Verify `naukri_update_log.json` in GitHub repository

### Test Cron Expression:
Jenkins provides a validation tool:
1. In the job configuration, hover over the cron field
2. Jenkins shows next run times

---

## Step 6: Verify Daily Execution

After setting up, verify execution:

1. **Check Jenkins UI:**
   - Go to your job page
   - Confirm build history shows daily builds

2. **Check GitHub:**
   - Verify commit logs show daily updates around 6 AM
   - Check `naukri_update_log.json` for timestamps

3. **Check Naukri:**
   - Login to Naukri
   - Verify your "Last Active" time is updated daily at 6 AM

4. **View Logs:**
   - Logs are available in Jenkins job artifacts
   - Download `naukri_update.log` for detailed execution logs

---

## Step 7: Troubleshooting

### Build Fails with Login Error
- Verify credentials in Jenkins Credentials Store
- Test credentials manually with the Python script
- Check if Naukri has enabled API access

### No Logs in Repository
- Ensure Git is configured in Jenkins
- Check Jenkins user has write permissions to GitHub repo
- Verify GitHub Personal Access Token has `repo` scope

### Schedule Not Running
- Verify Jenkins time zone is correct
- Check if build triggers are enabled
- Review Jenkins system logs for SCM polling errors

### Python Script Errors
```bash
# Test locally first
export NAUKRI_EMAIL="your-email@example.com"
export NAUKRI_PASSWORD="your-password"
python naukri_profile_updater.py
```

---

## Step 8: Optional Enhancements

### Send Email Notifications
Uncomment email sections in Jenkinsfile:
```groovy
emailext(
    subject: "Naukri Profile Updated",
    body: "Profile updated successfully!",
    to: 'your-email@example.com'
)
```

### Add Slack Notifications
Install Slack plugin and add:
```groovy
slackSend(
    channel: '#notifications',
    message: "Naukri profile updated successfully!"
)
```

### Monitor with Webhooks
Add GitHub webhooks to trigger Jenkins on code changes:
1. Go to GitHub repo Settings → Webhooks
2. Payload URL: `http://your-jenkins-server:8080/github-webhook/`
3. Select "Let me select individual events" → Pushes

---

## File Structure
```
naukri-profile-updater/
├── naukri_profile_updater.py    # Main Python script
├── Jenkinsfile                   # Jenkins pipeline config
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
├── README.md                     # Documentation
├── naukri_update_log.json        # Update history (auto-generated)
└── naukri_update.log             # Execution logs (auto-generated)
```

---

## Security Best Practices

✓ Store credentials in Jenkins Credentials Store, not in files
✓ Use GitHub Personal Access Tokens instead of passwords
✓ Enable 2FA on both GitHub and Naukri
✓ Restrict Jenkins access with authentication
✓ Review build logs regularly for errors
✓ Use `.gitignore` to prevent credential commits
✓ Rotate credentials periodically

---

## Support & Monitoring

- **Jenkins Job URL**: `http://your-jenkins-server:8080/job/naukri-profile-updater/`
- **GitHub Repo**: `https://github.com/your-username/naukri-profile-updater`
- **Build Status**: Check Jenkins dashboard or GitHub status checks

---

## Summary of Automation Flow

```
6:00 AM (Daily)
    ↓
Jenkins Cron Trigger
    ↓
Checkout code from GitHub
    ↓
Setup Python environment
    ↓
Run naukri_profile_updater.py
    ↓
Login to Naukri
    ↓
Update profile (last active time)
    ↓
Log results to naukri_update_log.json
    ↓
Commit & Push to GitHub
    ↓
Email notification (optional)
```

---

Happy automating! Your Naukri profile will now be updated automatically every day at 6 AM.
