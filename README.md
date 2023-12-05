# analytiikka-muut



Hakemistorakenne:

analytiikka_muut/

analytiikka_muut_stack.py  cicd stack
analytiikka_muut_stage.py  pipeline staget (= dev/prod)
analytiikka_muut_services_stack.py  stage sisältämät palvelut. Uudet asiat lisätään tänne
helper_glue.py  Apukoodi Glue- ajojen luontiin
helper_lambda.py  Apukoodi Lambdojen luontiin

lambda/xxx/  Jokaiselle lambdalle oma hakemisto. Jos python, hakemistossa pitää olla requirements.txt mutta se voi olla tyhjä jos ei tarvita. Testattu python, Java, node. Layerit eii testattu, lisäkirjastot ei testattu. Vpc ok.
lambda/testi1/  Python testi
lambda/servicenow/  Servicenow api lukija, Java

glue/xxx/  Jokaiselle glue- jobille oma hakemisto. Python shell ja spark testattu. Connectin luonti ok, iimport eii testattu.






Profiileihin kopioitu väyläpilven tilapäiset kredentiaalit

Secret github- yhteyttä varten
aws secretsmanager create-secret --name analytiikka-github-token --secret-string <github token> --profile dev_LatausalueAdmin

Tuotantotili parametrista
aws ssm put-parameter --name analytiikka-prod-account --value <prod account id> --profile dev_LatausalueAdmin
aws ssm put-parameter --name analytiikka-prod-account --value <prod account id> --profile prod_LatausalueAdmin

Bootstrap kerran molemmille tileille
npx cdk bootstrap aws://DEV-ACCOUNT-ID/eu-west-1 --cloudformation-execution-policies "arn:aws:iam::aws:policy/AdministratorAccess" --profile dev_LatausalueAdmin

npx cdk bootstrap aws://PROD-ACCOUNT-ID/eu-west-1 --trust DEV-ACCOUNT-ID --cloudformation-execution-policies "arn:aws:iam::aws:policy/AdministratorAccess" --profile prod_LatausalueAdmin

git commit &  push

Deploy käsin kerran, kun valmis niin git commit & push riittää
npx cdk deploy --profile dev_LatausalueAdmin




HUOM: pitääkö laittaa cdk.context.json myös gittiin ?



https://github.com/aws-samples/aws-cdk-examples/tree/master/python

