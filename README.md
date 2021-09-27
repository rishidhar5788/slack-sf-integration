# slack-sf-integration

run following commands using python package manager:

```pip install Django```

```pip install python-dotenv```

```pip install django-cors-headers```




Logic to get the salesforce case details to
show  up in slack using following custom slash command:

 1. '/demo-sf {SF case number}' - to show details of a salesforce case
 2. '/demo-sf date={YYYY-MM-DD}' - to show a very high level reporting 
 	  insight along with the case data in "demo-channels" slack channel
 	  for the cases that are created after the entered date in "YYYY-MM-DD" format

load your environment variables from .env file that
you can store anywhere in the project folder.
Following are the values that you would need in the .env file
 1. SLACK_BASE_URL - Slack base URL for API call
 2. SLACK_CHANNL_ID - Channel ID to see the details
 3. SF_BASE_URL - Salesforce Base URL
 4. SF_TOKEN - Auth token for Salesforce
 5. SLACK_BOT_TOKEN - Slack bot token to make API calls to Slack
 6. SECRET_KEY - Django secret key for the app
