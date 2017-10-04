import os
import time
import random
import datetime
import urllib
import urllib2

from lxml import html


dayToInt = {'Lun': 1, 'Mar': 2, 'Mer': 3, 'Jeu': 4, 'Ven': 5, 'Sam': 6, 'Dim': 0}
HEADERS = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) '
			'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 '
			'Safari/537.36')]


def generate_datetime(year, week_number, day, hour):
	# day is Lun or Mar or...
	# year is YYYY
	# hour is : HH:mm
	d = "{}-W{}-{}-{}".format(str(year), str(week_number), str(dayToInt[day]), hour)
	# Ex: 2017-W43-5-14:00
	r = datetime.datetime.strptime(d, "%Y-W%W-%w-%H:%M")
	# iCal format:
	# 19980118T230000
	return r.strftime('%Y%m%dT%H%M%S')


def write_event(file, titre, debut, fin, description):
	file.write("BEGIN:VEVENT\n")
	file.write("DTSTART:{}\n".format(debut))
	file.write("DTEND:{}\n".format(fin))
	file.write("SUMMARY:{}\n".format(titre))
	file.write("DESCRIPTION:{}\n".format(description))
	file.write("END:VEVENT\n")


def write_calendar_header(file):
	file.write("BEGIN:VCALENDAR\n")
	file.write("VERSION:2.0\n")
	file.write("PRODID:Calendrier Metz\n")


def getDataFromEventNode(event):
	jour = event.xpath('./@id')[0][2:5]
	heure = event.xpath('.//td[@class="salle"]/text()')[0]
	try:
		heure_debut, heure_fin = heure.split('-')
	except:
		print('Mauvais format heure :{}'.format(heure))
		sys.exit(1)

	cours_liste = event.xpath('.//td[@class = "edtrv"]/text()')
	try:
		cours = cours_liste[0]
	except:
		cours = ''
		print("pas de cours trouve")

	try:
		cours += ' ' + cours_liste[1]
	except:
		cours += ''

	try:
		prof = cours_liste[2]
	except:
		prof = ''

	return jour, heure_debut, heure_fin, cours, prof


def getHTMLTreeForYearWeek(year, week, LOCAL):
	if LOCAL:
		print("Getting local HTML")
		with open('default.html', 'r') as f:
			content = f.read()
		f.close()
	else:
		print("Getting remote HTML for Y: {} W: {}".format(str(year), str(week)))

		opener = urllib2.build_opener()
		opener.addheaders = HEADERS
		values = dict(Semaine=str(week), Annee=str(year), Sequence='3ASIR')
		data = urllib.urlencode(values)
		url = 'https://ntnoe.metz.supelec.fr/cgi-bin/agenda/AffEdTEleves.php?Semaine='+str(week)+'&Annee='+str(year)+'&Sequence=3ASIR&Concerne='
		response = opener.open(url, data)
		content = response.read()

	return html.fromstring(unicode(content, 'iso-8859-15'))


def init_headers():

	token = 'Basic XXXXXXXXX'

	if os.path.exists('.token'):
		f = open('.token')
		t = f.readline().replace('\n', '')
		f.close()
		token = 'Basic {}'.format(t)

	HEADERS.append(('Authorization', token))


def main():

	calendar_file = open("calendar.ical", "w")
	write_calendar_header(calendar_file)

	year, week_number, _ = datetime.datetime.now().isocalendar()
	years = [year]
	if week_number > 21:
		years.append(year + 1)

	couples = []
	if len(years) == 2:
		for week in range(week_number, 53):
			c = years[0], week
			couples.append(c)
		for week in range(1, 14):
			c = years[1], week
			couples.append(c)
	else:
		for week in range(week_number, 14):
			c = years[0], week
			couples.append(c)

	for c in couples:
		year, week = c

		tree = getHTMLTreeForYearWeek(year, week, LOCAL=False)

		for event in tree.xpath('//div[@id[starts-with(.,"RV")]]'):

			try:
				jour, heure_debut, heure_fin, cours, prof = getDataFromEventNode(event)

				debut = generate_datetime(year, week, jour, heure_debut)
				fin = generate_datetime(year, week, jour, heure_fin)

				print(cours)
				print(prof)
				print("{} - {}".format(heure_debut, heure_fin))
				print('')

				write_event(calendar_file, cours.encode('utf-8'), debut, fin, prof.encode('utf-8'))
			except Exception as e:
				print('An exception occurred : ', e)

		time.sleep(random.randint(1, 5))

	calendar_file.write("END:VCALENDAR\n")
	calendar_file.close()


if __name__ == '__main__':
	init_headers()
	main()
