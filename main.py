import urllib
import urllib2
import time
import random
import datetime
from lxml import html


dayToInt = {'Lun': 1,
			'Mar': 2,
			'Mer': 3,
			'Jeu': 4,
			'Ven': 5,
			'Sam': 6,
			'Dim': 0}

def generateDatetime(year, weekNumber, day, hour):
	#day is Lun or Mar or...
	#year is YYYY
	#hour is : HH:mm
	d = str(year)+'-W'+str(weekNumber)+'-'+str(dayToInt[day])+'-'+hour
	#Ex: 2017-W43-5-14:00
	r = datetime.datetime.strptime(d, "%Y-W%W-%w-%H:%M")
	#iCal format:
	# 19980118T230000
	return r.strftime('%Y%m%dT%H%M%S')

def writeEvent(file, titre, debut, fin, description):
	file.write("BEGIN:VEVENT\n")
	file.write("DTSTART:"+debut+"\n")
	file.write("DTEND:"+fin+"\n")
	file.write("SUMMARY:"+titre+"\n")
	file.write("DESCRIPTION:"+description+"\n")
	file.write("END:VEVENT\n")

def writeCalendarHeader(file):
	file.write("BEGIN:VCALENDAR\n")
	file.write("VERSION:2.0\n")
	file.write("PRODID:Calendrier Metz\n")

def getDataFromEventNode(event):
	jour = event.xpath('./@id')[0][2:5]
	heure = event.xpath('.//td[@class="salle"]/text()')[0]
	try:
		heureDebut, heureFin = heure.split('-')
	except:
		print('Mauvais format heure :'+heure)
		sys.exit(1)

	coursListe = event.xpath('.//td[@class = "edtrv"]/text()')
	try:
		cours = coursListe[0]
	except:
		print("pas de cours trouve")
		pass

	try:
		cours += ' '+coursListe[1]
	except:
		pass

	try:
		prof = coursListe[2]
	except:
		prof = ''

	return jour, heureDebut, heureFin, cours, prof 

def getHTMLTreeForYearWeek(year,week, LOCAL):
	if LOCAL:
		print("Getting local HTML")
		with open('default.html', 'r') as f:
			content = f.read()
		f.close()
	else:
		print("Getting remote HTML for Y: "+str(year)+" W: "+str(week))

		opener = urllib2.build_opener()
		opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'),
						 ('Authorization', 'Basic XXXXXXXXXX')]
		values = dict(Semaine=str(week), Annee=str(year), Sequence='3ASIR')
		data = urllib.urlencode(values)
		url = 'https://ntnoe.metz.supelec.fr/cgi-bin/agenda/AffEdTEleves.php?Semaine='+str(week)+'&Annee='+str(year)+'&Sequence=3ASIR&Concerne='
		response = opener.open(url, data)
		content = response.read()

	return html.fromstring(unicode(content, 'iso-8859-15'))

def main():

	F = open("calendar.ical", "w")
	writeCalendarHeader(F)

	year = 2018
	for week in range(1,14):

		tree = getHTMLTreeForYearWeek(year, week, LOCAL=False)

		for event in tree.xpath('//div[@id[starts-with(.,"RV")]]'):

			jour, heureDebut, heureFin, cours, prof = getDataFromEventNode(event)

			debut = generateDatetime(year, week, jour, heureDebut)
			fin = generateDatetime(year, week, jour, heureFin)
			
			print(cours)
			print(prof)
			print(heureDebut+" - "+heureFin)
			print('')

			writeEvent(F, cours.encode('utf-8'), debut, fin, prof.encode('utf-8'))


		time.sleep(random.randint(1, 5))

	F.write("END:VCALENDAR\n")
	F.close()


main()
