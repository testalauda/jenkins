pipeline{
    agent any
    stages{
        stage('Build'){
            steps{
                echo 'Building'
                echo 'Building'
                echo 'Building'
                echo 'Building'
                echo 'Building'
                
            }
        }
        stage('Test'){
            steps{
                echo 'Testing'
                echo 'Testing'
                echo 'Testing'
                echo 'Testing'
                echo 'Testing'
            }
        }
        stage('Approve'){  
            steps{
                timeout(time:15, unit:'MINUTES'){
                    script{
                        input message: 'Do you want to deploy?'
                        //input message: 'Do you want to deploy?', submitter: 'ops'
                    }
                }
            }
        }
        stage('Deploy-Staging1'){
            steps{
         
                echo 'Deploy-Staging1'
                echo 'Deploy-Staging2'
                
                
              
            }
        }
        
        stage('Deploy-Production'){
            steps{
                echo 'Deploy-Production'
                
            }
        }
    }
}
