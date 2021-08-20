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

### Now let's go to kendra console and we'll add our FAQ.
### For this select add FAQ and choose browse S3 and select the help-desk-faq file.csv.
### For IAM function we will create a basic function to give access to kendra in our S3.
### Choose Sync run schedule we will select Run on Demand to give you access to it whenever requested.
### After clicking Sync Now.
### Now let's allow our Lambda function to see our Amazon Kendra.
### Choose the IAM role listed under Role name.

![Lambda](https://user-images.githubusercontent.com/78814110/130277894-913a168a-0dce-4c4c-a8d7-b64404ed3caa.jpg)

### The last step will be to deploy on a channel, I'll use Slack, however it may be up to Facebook Messenger.
### On the Amazon Lex console, choose Settings. You will need to publish a version of your bot to integrate it with Slack. 

![add](https://user-images.githubusercontent.com/78814110/130278132-3a297948-9e2d-44f6-870b-46ebd8738f61.jpg)

Once created and integrated, the Bot is ready to be stocked and used in our app.

![slack](https://user-images.githubusercontent.com/78814110/130278207-1ca8ada8-8c93-448c-96fd-bcdc504c6d9b.jpg)




