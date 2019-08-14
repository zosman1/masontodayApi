from bs4 import BeautifulSoup
import jicson
import requests
import json

# const
IMAGE_URL = "https://static1.campusgroups.com"
MASON_360_URL = "https://mason360.gmu.edu"


def scrape360():
	r = requests.get("https://mason360.gmu.edu/ical/ical_gmu.ics")
	result = jicson.fromText(r.text)
	return result



def getEventCards():
	# endpoint 1
	# gets event cards for events page
	r = requests.get(
		"https://mason360.gmu.edu/mobile_ws/v17/mobile_events_list?range=0&limit=20")
	events = json.loads(r.text)

	eventList = []
	for event in events:
		# todo- remove date seperators here so they don't go through the logic below before not getting used
		fields = event["fields"].split(",")
		# if(fields == "") continue

		fieldNumber = 0
		newEvent = {}
		for field in fields:
			fieldData = event["p" + str(fieldNumber)]
			if(not (field == "" or fieldData == "")):
				newEvent[field] = fieldData

			fieldNumber += 1
		# here filter out garbage events

		if(not newEvent["displayType"] == "separator"):
			eventList.append(hydrateEvent(cleanupEvent(newEvent)))


	return eventList


def getDescriptionFromEventPage(eventUrl):
	r = requests.get(eventUrl)
	soup = BeautifulSoup(r.text, 'html.parser')
	
	for cardBlock in soup.find_all('div', class_="card-block"):
		if "Details" in cardBlock.get_text():
			description = list((filter(lambda div:  "\r\n\t\t\t\t\t" in div, cardBlock.contents)))[0]
			return description.strip()
	#returns description

# modify the event object to be a bit more friendly
def hydrateEvent(event):
	event["description"] = getDescriptionFromEventPage(event["eventUrl"])
	return event


def cleanupEvent(event):
	# cleanup image url
	if('eventPicture' in event.keys()):
		event["eventPicture"] = IMAGE_URL + event["eventPicture"]
	#cleanup event url
	if("eventUrl" in event.keys()):
		event["eventUrl"] = MASON_360_URL + event["eventUrl"]
	#cleanup event tags
	if("eventTags" in event.keys()):
		soup = BeautifulSoup(event["eventTags"], 'html.parser')
		eventTags = []
		for link in soup.find_all("a"):
			eventTag = {}
			eventTag['link'] = MASON_360_URL + link.get('href').split('&')[0]
			eventTag['name'] = link.span.string
			eventTags.append(eventTag)

		event['eventTags'] = eventTags
	#cleanup event dates
	if("eventDates" in event.keys()):
		soup = BeautifulSoup(event["eventDates"], 'html.parser')
		p = soup.find_all('p')
		if("&ndash;" in soup.find_all('p')[0].string):
			event['multiDayEvent'] = True
			event['startDateTimeStr'] = p[0].string.replace("&ndash;", "-")
			event['endDateTimeStr'] = p[1].string.replace("&ndash;", "-")
		else:
			event['multiDayEvent'] = False
			event['dateStr'] = p[0].string
			event['timeStr'] = p[1].string.replace("&ndash;", "2011\u201312")
		del event["eventDates"]



	return event


# print(getEventCards())
# getEventCards()
