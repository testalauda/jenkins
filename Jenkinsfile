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
        
        stage('Deploy-Production'){
            steps{
                echo 'Deploy-Production'
            }
        }
    }
}
