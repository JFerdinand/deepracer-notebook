##### FIELDS TO FILL OUT #####
account_id = '318512209165' # Your IAM role account ID (12 digit number)
username = 'summit01' # Your IAM role username
password = 'CIH_win_0529' # Your IAM role password
race_url = 'https://us-east-1.console.aws.amazon.com/deepracer/home?region=us-east-1#competition/arn%3Aaws%3Adeepracer%3A%3A318512209165%3Aleaderboard%2Fd4f4275f-16aa-4a98-a752-bd8e82e463fe/submitModel' # The url of the race (default is October Pro Qualifier)
model_to_submit = 'k1999-optimization-cw-2-clone' # Name of the model you want to submit
##############################


creds = [account_id, username, password]
if __name__ == '__main__':
    from auto_submit_utils import start_selenium
    start_selenium(creds, race_url, model_to_submit, iam_role=True)