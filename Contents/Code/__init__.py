RE_SEASON_EP = Regex('Season (?P<season>\d+), Ep. (?P<episode>\d+)')

CW_ROOT = 'http://www.cwtv.com'
CW_SHOWS_LIST = 'http://www.cwtv.com/shows'
EP_URL = 'http://www.cwtv.com/shows'

####################################################################################################
def Start():

	ObjectContainer.title1 = 'The CW'

####################################################################################################
@handler('/video/thecw', 'The CW')
def MainMenu():

	oc = ObjectContainer()
	oc.add(DirectoryObject(key = Callback(Shows, title='Current Shows'), title='Current Shows'))
	oc.add(DirectoryObject(key = Callback(Shows, title='Also On The CW'), title='Also On The CW'))

	return oc

####################################################################################################
@route('/video/thecw/shows')
def Shows(title):

	oc = ObjectContainer(title2=title)
	html = HTML.ElementFromURL(CW_SHOWS_LIST)

	for item in html.xpath('//ul[@class="showsnav {}"]/li/a'.format(title.replace(' ', '').lower())):

		title = item.xpath('./p/text()')[0]

		if title in ['Whose Line Is It Anyway?']:
			continue

		url = CW_ROOT + item.xpath('./@href')[0]
		thumb = 'http://{}'.format(item.xpath('.//img/@data-origsrc')[0].split('//')[-1])

		oc.add(DirectoryObject(
			key = Callback(Episodes, url=url, title=title),
			title = title,
			thumb = thumb
		))

	return oc

####################################################################################################
@route('/video/thecw/episodes')
def Episodes(url, title):

	oc = ObjectContainer(title2=title)
	html = HTML.ElementFromURL(url)

	for item in html.xpath('//ul[@id="list_1"]/li/div/a[@class="thumbLink"]'):

		url = item.xpath('./@href')[0]
		if not url.startswith('http://') or not url.startswith('https://'):
			url = '{}{}'.format(CW_ROOT, url)

		thumb = item.xpath('.//img/@src')[0]
		episode_title = item.xpath('.//div[@class="videodetails1"]/p/text()')[0]

		try:
			season_and_episode = episode_title.split('Ep.')[1].split(')')[0]
			if len(season_and_episode) >3:
				season = season_and_episode[0] + season_and_episode[1]
			else:
				season = season_and_episode[0]

			try: season = int(season)
			except: season = None

			try: ep_index = int(season_and_episode)
			except: ep_index = None
		except:
			season = None
			ep_index = None

		try:
			date = item.xpath('.//p[@class="videodate"]//text()')[0]
			date = Datetime.ParseDate(date.split('Original Air Date: ')[1]).date()
		except:
			date = None

		if date:
			oc.add(EpisodeObject(
				url = url,
				title = episode_title,
				show = title,
				index = ep_index,
				season = season,
				originally_available_at = date,
				thumb = thumb
			))
		else:
			oc.add(VideoClipObject(
				url = url,
				title = episode_title,
				thumb = thumb
			))

	return oc
