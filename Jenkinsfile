// Jenkinsfile for Naukri Profile Auto-Update
// Triggers daily at 6 AM and updates profile via GitHub integration

pipeline {
    agent any
    
    // Environment variables
    environment {
        REPO_URL = 'https://github.com/your-username/naukri-profile-updater'
        BRANCH = 'main'
        PYTHON_SCRIPT = 'naukri_profile_updater.py'
        LOG_FILE = 'naukri_update.log'
        UPDATE_LOG = 'naukri_update_log.json'
    }
    
    // Schedule: Daily at 6 AM
    triggers {
        cron('0 6 * * *')  // 6 AM every day
    }
    
    options {
        // Keep last 30 builds
        buildDiscarder(logRotator(numToKeepStr: '30'))
        // Timeout after 15 minutes
        timeout(time: 15, unit: 'MINUTES')
        // Disable concurrent builds
        disableConcurrentBuilds()
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "Checking out code from GitHub..."
                    checkout(
                        [
                            $class: 'GitSCM',
                            branches: [[name: "*/${BRANCH}"]],
                            userRemoteConfigs: [[url: "${REPO_URL}.git"]]
                        ]
                    )
                }
            }
        }
        
        stage('Setup') {
            steps {
                script {
                    echo "Setting up Python environment..."
                    sh '''
                        python --version
                        pip install -r requirements.txt --quiet
                    '''
                }
            }
        }
        
        stage('Update Profile') {
            steps {
                script {
                    echo "Updating Naukri profile at 6 AM..."
                    withCredentials([
                        string(credentialsId: 'naukri-email', variable: 'NAUKRI_EMAIL'),
                        string(credentialsId: 'naukri-password', variable: 'NAUKRI_PASSWORD')
                    ]) {
                        sh '''
                            export NAUKRI_EMAIL=${NAUKRI_EMAIL}
                            export NAUKRI_PASSWORD=${NAUKRI_PASSWORD}
                            python ${PYTHON_SCRIPT}
                        '''
                    }
                }
            }
        }
        
        stage('Commit Update Log') {
            steps {
                script {
                    echo "Committing update log to GitHub..."
                    sh '''
                        git config user.name "Jenkins Bot"
                        git config user.email "jenkins@example.com"
                        git add ${UPDATE_LOG} ${LOG_FILE} || true
                        
                        # Only commit if there are changes
                        if ! git diff --cached --quiet; then
                            git commit -m "Automated: Naukri profile updated at $(date '+%Y-%m-%d %H:%M:%S')"
                            git push origin ${BRANCH}
                            echo "✓ Changes pushed to GitHub"
                        else
                            echo "No changes to commit"
                        fi
                    '''
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "Build completed!"
                // Archive logs
                archiveArtifacts artifacts: "${LOG_FILE},${UPDATE_LOG}", 
                                  allowEmptyArchive: true
            }
        }
        
        success {
            script {
                echo "✓ Profile update successful!"
                // Optional: Send notification
                emailext(
                    subject: "✓ Naukri Profile Updated Successfully",
                    body: """
                        Naukri profile has been updated at 6 AM.
                        Check logs: ${BUILD_URL}artifact/${LOG_FILE}
                    """,
                    to: '${CHANGE_AUTHOR_EMAIL}'
                ) || true
            }
        }
        
        failure {
            script {
                echo "✗ Profile update failed!"
                emailext(
                    subject: "✗ Naukri Profile Update Failed",
                    body: """
                        Failed to update Naukri profile.
                        Check logs: ${BUILD_URL}console
                    """,
                    to: '${CHANGE_AUTHOR_EMAIL}' 
                ) || true
            }
        }
    }
}
