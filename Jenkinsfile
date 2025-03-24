pipeline {
    agent any

    parameters {
        booleanParam(name: 'BD_IMG_CHANGED', defaultValue: false, description: 'Set to true if backend image needs to be rebuilt')
        booleanParam(name: 'FD_IMG_CHANGED', defaultValue: false, description: 'Set to true if frontend image needs to be rebuilt')
    }

    environment {
        // Docker Hub credentials and repository details
        DOCKER_HUB = "docker.io"
        DOCKER_USERNAME = "Replace_with_yours"
        BACKEND_IMAGE = "${DOCKER_USERNAME}/world-time-app-backend"
        FRONTEND_IMAGE = "${DOCKER_USERNAME}/world-time-app-frontend"

        // Generate image versions dynamically based on timestamp to avoid manual updates
        IMAGE_TAG_BD = "1.0-${BUILD_NUMBER}"
        IMAGE_TAG_FD = "1.0-${BUILD_NUMBER}"

        // Credentials ID for Docker login (Best practice: Use Access Token instead of password)
        DOCKER_CREDENTIALS_ID = "docker-hub-access-token"

        // Git repository details
        GIT_REPO = "https://github.com/devopsritiks/wta_jenkins_docker.git"
        GIT_BRANCH = "main"
    }

    options {
        timeout(time: 30, unit: 'MINUTES') // Timeout to prevent stuck builds
    }

    stages {
        stage('Prepare Environment') {
            steps {
                echo "// Checking Terraform version..."
                sh 'terraform --version'
            }
        }

        stage('Clone Repository') {
            steps {
                echo "// Cloning the Git repository..."
                git branch: "${GIT_BRANCH}", url: "${GIT_REPO}"
            }
        }

        stage('Terraform Apply') {
            steps {
                echo "// Initializing and applying Terraform configuration..."
                dir('terraform') {
                    sh "terraform init"
                    sh "terraform apply -auto-approve"
                }

                echo "// Retrieving EC2 instance public IP..."
                script {
                    def tfOutput = sh(script: "terraform output -json", returnStdout: true).trim()
                    def tfOutputJson = readJSON text: tfOutput
                    env.EC2_PUBLIC_IP = tfOutputJson.ec2_public_ip.value
                }

                echo "EC2 Public IP: ${env.EC2_PUBLIC_IP}"
            }
        }

        stage('Update Configuration Files') {
            steps {
                echo "// Updating app.py and index.html with EC2 public IP..."
                sh """
                    sed -i 's|http://public_ip:5000|http://${env.EC2_PUBLIC_IP}:5000|g' backend/app.py
                    sed -i 's|http://public_ip:5000|http://${env.EC2_PUBLIC_IP}:5000|g' frontend/index.html
                """
            }
        }

        stage('Build and Push Backend Image') {
            when {
                expression { params.BD_IMG_CHANGED == true }
            }
            steps {
                echo "// Building and pushing new backend image..."
                withCredentials([string(credentialsId: "${DOCKER_CREDENTIALS_ID}", variable: 'DOCKER_ACCESS_TOKEN')]) {
                    sh '''
                        docker logout || true
                        echo $DOCKER_ACCESS_TOKEN | docker login --username $DOCKER_USERNAME --password-stdin

                        docker rmi ${BACKEND_IMAGE}:latest || true

                        docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG_BD} ./backend
                        docker tag ${BACKEND_IMAGE}:${IMAGE_TAG_BD} ${BACKEND_IMAGE}:latest
                        docker push ${BACKEND_IMAGE}:${IMAGE_TAG_BD}
                        docker push ${BACKEND_IMAGE}:latest
                    '''
                }
            }
        }

        stage('Build and Push Frontend Image') {
            when {
                expression { params.FD_IMG_CHANGED == true }
            }
            steps {
                echo "// Building and pushing new frontend image..."
                withCredentials([string(credentialsId: "${DOCKER_CREDENTIALS_ID}", variable: 'DOCKER_ACCESS_TOKEN')]) {
                    sh '''
                        docker logout || true
                        echo $DOCKER_ACCESS_TOKEN | docker login --username $DOCKER_USERNAME --password-stdin

                        docker rmi ${FRONTEND_IMAGE}:latest || true

                        docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG_FD} ./frontend
                        docker tag ${FRONTEND_IMAGE}:${IMAGE_TAG_FD} ${FRONTEND_IMAGE}:latest
                        docker push ${FRONTEND_IMAGE}:${IMAGE_TAG_FD}
                        docker push ${FRONTEND_IMAGE}:latest
                    '''
                }
            }
        }

        stage('Deploy Application') {
            steps {
                echo "# Updating .env file with latest image tags..."
                sh """
                    echo "BACKEND_IMAGE_TAG=${IMAGE_TAG_BD}" > .env
                    echo "FRONTEND_IMAGE_TAG=${IMAGE_TAG_FD}" >> .env
                """

                echo "# Deploying the application using Docker Compose..."
                withEnv(["COMPOSE_HTTP_TIMEOUT=1800"]) {
                    sh '''
                        docker-compose down || true
                        docker-compose up -d
                    '''
                }
            }
        }

        stage('Prune Unused Docker Images') {
            steps {
                echo "// Removing unused Docker images to free up space..."
                sh "docker image prune -af"
            }
        }
    }

    post {
        success {
            echo "Pipeline executed successfully!"
        }
        failure {
            echo "Pipeline failed. Please check logs for details."
        }
    }
}
