#!/usr/bin/env python3
import os

import requests
from elasticsearch import Elasticsearch, helpers
from dotenv import dotenv_values
from datetime import datetime



config = dotenv_values(os.path.dirname(__file__) + '/env')

headers={
    'Authorization':  'Bearer ' + config['MIGRATE_TOKEN']
}
API_URL=config['API_URL']

def post_to_directus(json):
	incoming_uuid = json['id']
	check = requests.head(API_URL + "/items/drievoor12updates/" + incoming_uuid, headers= headers)
	if check.status_code == 200:
		response = requests.patch(API_URL + "/items/drievoor12updates/" + incoming_uuid,
		headers= headers,
		json= json
	    )
	else:
		response = requests.post(API_URL + "/items/drievoor12updates/",
		headers= headers,
		json= json
	    )
	if response.status_code >= 200 and response.status_code < 300:
		print(response.status_code)
		if response.status_code == 204:
			pass
		else:
			print(response.json())
		return
	elif 400 == response.status_code:
		pass
	else:
		raise Exception("Error posting to Directus: " + str(response.status_code) + " " + response.text)


def map_to_directus(source):
	return {
	'id': source['id'],
	'title': source['title'],
	'subtitle': source['subtitle'],
	'text': source['text'],
	'publishDate': datetime.fromtimestamp(source['publishDate'] / 1000).isoformat(),
	'type': source['type'],

	 }



def migrate():
    es = Elasticsearch("http://localhost:9210")

    resp = helpers.scan(
      es,
      index="3voor12_updates",
      scroll = '3m',
      preserve_order=True,
      query= {
      'sort':'publishDate:desc'
      }
    )

    for num, doc in enumerate(resp):
        print("%s" % str(doc))
        source = doc["_source"]
        print(num)
        post_to_directus(map_to_directus(source))


migrate()
