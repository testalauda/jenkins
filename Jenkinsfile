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
                timeout(time:1, unit:'MINUTES'){
                    script{
                        input message: 'Do you want to deploy?'
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
