pipeline{
    agent{
        label 'any'
    }
    stages{
        stage('Build'){
            steps{
                echo 'Building'
            }
        }
        stage('Test'){
            steps{
                echo 'Testing'
            }
        }
        stage('Deploy-Staging'){
            steps{
                sh './deploystaging'
                sh './run-smoke-tests'
            }
        }
        stage('Sanitycheck'){
            steps{
                input "Does the staging environment look ok?"
            }
        }
        stage('Deploy-Production'){
            steps{
                sh './deployproduction'
            }
        }
    }
}
