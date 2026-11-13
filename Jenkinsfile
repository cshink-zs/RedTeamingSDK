pipeline {
    agent any

    environment {
        OAUTH_CLIENT_ID     = credentials('oauth-client-id')
        OAUTH_CLIENT_SECRET = credentials('oauth-client-secret')
        OAUTH_TOKEN_URL     = credentials('oauth-token-url')
        TARGET_ID           = credentials('target-id')
        TEST_RUN_NAME       = "jenkins-${env.BUILD_NUMBER}"
    }

    stages {
        stage('Trigger red teaming test run') {
            steps {
                sh '''
                    docker run --rm \
                      -e OAUTH_CLIENT_ID="$OAUTH_CLIENT_ID" \
                      -e OAUTH_CLIENT_SECRET="$OAUTH_CLIENT_SECRET" \
                      -e OAUTH_TOKEN_URL="$OAUTH_TOKEN_URL" \
                      -e TARGET_ID="$TARGET_ID" \
                      -e TEST_RUN_NAME="$TEST_RUN_NAME" \
                      cshink837/trigger_test_run:latest
                '''
            }
        }
    }
}
