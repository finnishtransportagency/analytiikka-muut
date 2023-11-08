# analytiikka-muut


cdk bootstrap aws://DEV-ACCOUNT-ID/eu-west-1
( npx cdk bootstrap aws://DEV-ACCOUNT-ID/ap-southeast-2 --qualifier myapp --toolkit-stack-name CDKToolkit-myapp --profile build )

aws secretsmanager create-secret --name github-token --secret-string ghp_73952xxxxxxxxxxxxx9f187b1 --region ap-southeast-2 --profile build


cdk bootstrap aws://PROD-ACCOUNT-ID/eu-west-1 --trust DEV-ACCOUNT-ID --cloudformation-execution-policies "arn:aws:iam::aws:policy/AdministratorAccess"


ensimmäisen kerran käsin:
npx cdk deploy --profile build


