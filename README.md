# ChatBot

## To create our Help_desk_bot First we must create our Lambda function ( In this version I used python 3.8)
## Once running our Amazon Lex, we will create and connect it to our amazon Kendra. 
## amazon Kendra is an enterprise search service based on Machine Lerning. 

![lex](https://user-images.githubusercontent.com/78814110/130277608-f8049ddb-f2e0-4e1b-919b-a4da36b9e7d5.jpg)


### For this we go to the Amazon Kendra service and select Create index.

![kendra](https://user-images.githubusercontent.com/78814110/130277553-a437b5d9-0ae4-434c-b8b5-de7912e85e51.jpg)


### In the IAM role, we'll create a new role to allow Amazon Kendra to access CloudWatch Logs.
### Let's now create our Bucket s3.

![s3](https://user-images.githubusercontent.com/78814110/130277581-36e603e2-c62e-460d-a5dd-45d8affe79bc.jpg)


### once created we will attach the files (available for download in the folder)
* Amazon-WorkDocs-Sync
* Amazon-WorkDocs-Mobile-and-web-acess
* Amazon-WorkDocs-Drive
* help-desk-faq

Now let's go to kendra console and we'll add our FAQ.
For this select add FAQ and choose browse S3 and select the help-desk-faq file.csv.
For IAM function we will create a basic function to give access to kendra in our S3.
Choose Sync run schedule we will select Run on Demand to give you access to it whenever requested.
After clicking Sync Now.


