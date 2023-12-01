# analytiikka-muut



Hakemistorakenne:

analytiikka_muut/

analytiikka_muut_stack.py  cicd stack
analytiikka_muut_stage.py  pipeline staget (= dev/prod)
analytiikka_muut_services_stack.py  stage sisältämät palvelut. Uudet asiat lisätään tänne
helper_glue.py  Apukoodi Glue- ajojen luontiin
helper_lambda.py  Apukoodi Lambdojen luontiin

lambda/xxx/  Jokaiselle lambdalle oma hakemisto. Jos python, hakemistossa pitää olla requirements.txt mutta se voi olla tyhjä jos ei tarvita
lambda/testi1/  Python testi
lambda/servicenow/  Servicenow api lukija, Java

glue/xxx/  Jokaiselle glue- jobille oma hakemisto. Ei testattu






Profiileihin kopioitu väyläpilven tilapäiset kredentiaalit

npx cdk bootstrap aws://DEV-ACCOUNT-ID/eu-west-1 --cloudformation-execution-policies "arn:aws:iam::aws:policy/AdministratorAccess" --profile dev_LatausalueAdmin

npx cdk bootstrap aws://PROD-ACCOUNT-ID/eu-west-1 --trust DEV-ACCOUNT-ID --cloudformation-execution-policies "arn:aws:iam::aws:policy/AdministratorAccess" --profile prod_LatausalueAdmin

aws secretsmanager create-secret --name github-token --secret-string <github token> --profile dev_LatausalueAdmin

dev- tilille luotu parametri jossa prod- tilin id

git commit &  push

npx cdk deploy --profile dev_LatausalueAdmin








https://github.com/aws-samples/aws-cdk-examples/tree/master/python

