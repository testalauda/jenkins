pipeline{
    agent any
    stages{
        stage('Build'){
            steps{
                echo 'Building12'
               
            }
        }
        stage('Test'){
            steps{
                echo 'Testing12'
               
            }
        }
        stage('Approve'){  
            steps{
                
                    script{
                        input message: 'Do you want to deploy?'
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
