pipeline{
    agent any
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
                sh 'cat ./a.sh'
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
