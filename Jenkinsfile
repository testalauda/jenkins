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
        stage('Approve'){  
            steps{
                input message: 'Do you want to deploy?', submitter: 'ops' 
            }
        } 
        stage('Deploy-Staging'){
            steps{
                echo 'Deploy-Staging12345yuykjhgdf'
            }
        }
        
        stage('Deploy-Production'){
            steps{
                echo 'Deploy-Production'
            }
        }
    }
}
