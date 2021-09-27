import logging
import os
import requests
import json
import socket
from dotenv import load_dotenv, find_dotenv
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# load your environment variables from .env file that
# you can store anywhere in the project folder
load_dotenv(find_dotenv())

# Turn on the logging
logging.basicConfig(level=logging.DEBUG)

# Create your views here.
def index(request):
	return HttpResponse("Welocome to my website")

def admin_index(request):
	return HttpResponse("This is default index page")

# Logic to get the salesforce case details to
# show  up in slack using following custom slash command:
# 
# 1. '/demo-sf {SF case number}' - to show details of a salesforce case
# 2. '/demo-sf date={YYYY-MM-DD}' - to show a very high level reporting 
# 	  insight along with the case data in "demo-channels" slack channel
# 	  for the cases that are created after the entered date in "YYYY-MM-DD" format
@csrf_exempt
def demo(request):
# Section for high level reporting insight and granular information
# on cases created after a certain date
	if 'date' in request.POST['text']:
		date=request.POST['text']
		sf_date=date.split('=')

		# Make a GET call to Salesforce to fetch all cases after the input date
		sf_url = os.getenv('SF_BASE_URL') + """/services/data/v39.0/query/?q=SELECT Id, CaseNumber, Owner.Name,
		CreatedDate, LastModifiedDate, Description, Priority, Subject, Status, CreatedBy.Name 
		FROM Case WHERE CreatedDate >="""+sf_date[1]+"""T00:00:00Z"""
		sf_payload = {}
		files = {}
		sf_headers = {
		  	'Authorization': 'Bearer ' + os.getenv('SF_TOKEN')
		}
		sf_response = requests.request("GET", sf_url, headers=sf_headers, data=sf_payload, files=files)

		sf_block_prep_response = sf_response.json()
		if sf_block_prep_response['totalSize'] is not 0 or None:
			for val in sf_block_prep_response['records']:
				assigned_to = val['Owner']['Name']
				sf_case_url = val['attributes']['url']

				# extract url for the salesforce case
				str_builder = sf_case_url.split('/', maxsplit=5)
				final_sf_case_url = os.getenv('SF_BASE_URL') + "/lightning/r/" + str_builder[5] + "/view"

				sf_case_priority = val['Priority'] if val['Priority'] is not None else "No Priority present in *Salesforce*"
				sf_case_subject = val['Subject'] if val['Subject'] is not None else "No Subject present in *Salesforce*"
				sf_case_desc = val['Description'] if val['Description'] is not None else "No description present in *Salesforce*"
				sf_created_by = val['CreatedBy']['Name']

				# block builder for slack
				block_for_slack = get_block_for_slack(assigned_to,
				final_sf_case_url, sf_case_priority, sf_case_subject, 
				sf_case_desc, sf_created_by)
				

				# POST the block data from SF back to slack
				# Response sent out to slack for showing the data in slack
				slack_channel_call(block_for_slack)

			return HttpResponse("Total number of cases created after *" + sf_date[1] + "* are *" + str(sf_block_prep_response['totalSize']) + "* .\n"
				":white_check_mark: Check the demo_channels for the complete case summary!")
		else:
			return HttpResponse(":x: Failed to retrieve records!")

# Section for high level case details on the input case number
	else:
		try:
			# Make a GET call to Salesforce to fetch case info
			sf_url = os.getenv('SF_BASE_URL') + """/services/data/v39.0/query/?q=SELECT Id, CaseNumber, Owner.Name,
			CreatedDate, LastModifiedDate, Description, Priority, Subject, Status, CreatedBy.Name 
			FROM Case WHERE CaseNumber='"""+request.POST['text']+"""'"""
			sf_payload = {}
			files = {}
			sf_headers = {
		  		'Authorization': 'Bearer ' + os.getenv('SF_TOKEN')
			}
			sf_response = requests.request("GET", sf_url, headers=sf_headers, data=sf_payload, files=files)
		except Exception as e:
			raise "Error processing salesforce API call!!!\n" + e

			# format the json data for slack
		try:
			sf_block_prep_response = sf_response.json()
			if sf_block_prep_response['totalSize'] is not 0:
				assigned_to = sf_block_prep_response['records'][0]['Owner']['Name']
				sf_case_url = sf_block_prep_response['records'][0]['attributes']['url']

				# extract url for the salesforce case
				str_builder = sf_case_url.split('/', maxsplit=5)
				final_sf_case_url = os.getenv('SF_BASE_URL') + "/lightning/r/" + str_builder[5] + "/view"

				sf_case_priority = sf_block_prep_response['records'][0]['Priority'] if sf_block_prep_response['records'][0]['Priority'] is not None else "No Priority present in *Salesforce*"
				sf_case_subject = sf_block_prep_response['records'][0]['Subject'] if sf_block_prep_response['records'][0]['Subject'] is not None else "No Subject present in *Salesforce*"
				sf_case_desc = sf_block_prep_response['records'][0]['Description'] if sf_block_prep_response['records'][0]['Description'] is not None else "No description present in *Salesforce*"
				sf_created_by = sf_block_prep_response['records'][0]['CreatedBy']['Name']

				# block builder for slack
				block_for_slack = get_block_for_slack(assigned_to, 
					final_sf_case_url, sf_case_priority, sf_case_subject, 
					sf_case_desc, sf_created_by)
				
				# Post the block data from SF back to slack
				# /demo-sf 00001050
				try:
					# Response sent out to slack for showing the data in slack
					slack_channel_call(block_for_slack)
				except Exception as e:
					raise "Error processing slack API call\n!!!" + e
				else:
					return HttpResponse(":tada::tada::tada: Successfully retrieved the salesforce Case data: Check it in the *demo_channels*!")
		except Exception as e:
			raise "Error formatting salesforce JSON!!!\n" + e
		else:
			return HttpResponse(""":x: *Oh no*:exclamation::exclamation:\n 
				Looks like we have run into an issue! Don't worry :wink:, we have got you covered :grin: 
				\n*Check one or more of these suggested problems:*\n
				:white_check_mark: Salesforce permission issue\n
				:white_check_mark: Case created before *2020-03-05*\n
				:white_check_mark: No SF Case number entered\n
				:white_check_mark: The Case is locked\n
				:white_check_mark: Wrong input provided""")

def slack_channel_call(block_for_slack):
	slk_url = os.getenv('SLACK_BASE_URL') + "chat.postMessage"
	slk_payload = "{\"channel\": \"" + os.getenv('SLACK_CHANNL_ID') + "\",\"blocks\":" + block_for_slack + "}"
	slk_headers = {
			'Content-Type': 'application/json',
			'Authorization': 'Bearer ' + os.getenv('SLACK_BOT_TOKEN')
		}
	response = requests.request("POST", slk_url, headers=slk_headers, data=slk_payload.encode('utf-8'))

# prepare the json for the block to be sent as a response to slack
def get_block_for_slack(assigned_to, final_sf_case_url,
	sf_case_priority, sf_case_subject, sf_case_desc, sf_created_by):
	block = """[
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Welcome to the Slack and Salesforce Integration Demo:*\n *Please see the salesforce case details below.*\n\n *Salesforce Case details*"
			}
		},
	  {
	    "type": "divider"
	  },
	  {
	    "type": "section",
	    "text": {
	      "type": "mrkdwn",
	      "text": "*Go to the link to see complete case details on salesforce or else check the case summary here:*\n:heavy_minus_sign::heavy_minus_sign::heavy_minus_sign::heavy_minus_sign:\n<""" +final_sf_case_url+ """>"
	    },
	    "accessory": {
	      "type": "image",
	      "image_url": "https://i.ibb.co/NxqdWR8/Salesforce-com-logo-svg.png",
	      "alt_text": "alt text for image"
	    }
	  },
	  {
	    "type": "divider"
	  },
	  {
	    "type": "section",
	    "text": {
	      "type": "mrkdwn",
	      "text": "*Case Priority*\n:fire:\n""" +sf_case_priority+ """ "
	    }
	   },
	  {
	    "type": "section",
	    "text": {
	      "type": "mrkdwn",
	      "text": "*Assigned to*\n:factory_worker:\n""" +assigned_to+ """ "
	    }
	   },
	  {
	    "type": "section",
	    "text": {
	      "type": "mrkdwn",
	      "text": "\n:memo:\n*Subject:*\n""" +sf_case_subject+ """ "
	    }
	   },
	  {
	    "type": "section",
	    "text": {
	      "type": "mrkdwn",
	      "text": "*Description:*\n""" +sf_case_desc+ """ "
	    }
	   },
	  {
	    "type": "section",
	    "text": {
	      "type": "mrkdwn",
	      "text": "*Created By*\n:hammer:\n""" +sf_created_by+ """ "
	    }
	   }
	]"""

	return block