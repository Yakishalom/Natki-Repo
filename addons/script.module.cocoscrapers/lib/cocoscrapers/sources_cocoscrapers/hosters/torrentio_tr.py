# -*- coding: utf-8 -*-
# created by Venom for Fenomscrapers (updated 7-19-2022)
'''
	Fenomscrapers Project
'''

from json import loads as jsloads
import re,xbmcaddon
from cocoscrapers.modules import client
from cocoscrapers.modules import source_utils

class source:
	priority = 1
	pack_capable = True
	cobra=xbmcaddon.Addon('plugin.video.cobra')
	show_torrent=cobra.getSetting('show_torrent')
	if show_torrent=='true':
		hasMovies = True
		hasEpisodes = True
	else:
		hasMovies = False
		hasEpisodes = False

	def __init__(self):
		self.language = ['en']
		self.base_link = "https://torrentio.strem.fun"
		#self.movieSearch_link = '/providers=yts,eztv,rarbg,1337x,thepiratebay,kickasstorrents,torrentgalaxy|language=english/stream/movie/%s.json' #found this to be broken 12-9-22 umbrelladev
		#self.tvSearch_link = '/providers=yts,eztv,rarbg,1337x,thepiratebay,kickasstorrents,torrentgalaxy|language=english/stream/series/%s:%s:%s.json' #found this to be broken 12-9-22 umbrelladev
		self.movieSearch_link = '/providers=yts,eztv,rarbg,1337x,thepiratebay,kickasstorrents,torrentgalaxy/stream/movie/%s.json'
		self.tvSearch_link = '/providers=yts,eztv,rarbg,1337x,thepiratebay,kickasstorrents,torrentgalaxy/stream/series/%s:%s:%s.json'
		self.min_seeders = 2
# Currently supports YTS(+), EZTV(+), RARBG(+), 1337x(+), ThePirateBay(+), KickassTorrents(+), TorrentGalaxy(+), HorribleSubs(+), NyaaSi(+), NyaaPantsu(+), Rutor(+), Comando(+), ComoEuBaixo(+), Lapumia(+), OndeBaixa(+), Torrent9(+).

	def sources(self, data, hostDict):
		sources = []
		if not data: return sources
		sources_append = sources.append
		try:
			aliases = data['aliases']
			year = data['year']
			imdb = data['imdb']
			if 'tvshowtitle' in data:
				title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ').replace('$', 's')
				episode_title = data['title']
				season = data['season']
				episode = data['episode']
				hdlr = 'S%02dE%02d' % (int(season), int(episode))
				years = None
				url = '%s%s' % (self.base_link, self.tvSearch_link % (imdb, season, episode))
			else:
				title = data['title'].replace('&', 'and').replace('/', ' ').replace('$', 's')
				episode_title = None
				hdlr = year
				years = [str(int(year)-1), str(year), str(int(year)+1)]
				url = '%s%s' % (self.base_link, self.movieSearch_link % imdb)
			#log_utils.log('url = %s' % url)
			results = client.request(url, timeout=5)
			try: files = jsloads(results)['streams']
			except: return sources
			_INFO = re.compile(r'👤.*')
			undesirables = source_utils.get_undesirables()
			check_foreign_audio = source_utils.check_foreign_audio()
		except:
			source_utils.scraper_error('TORRENTIO')
			return sources

		for file in files:
			try:
				hash = file['infoHash']
				file_title = file['title'].split('\n')
				file_info = [x for x in file_title if _INFO.match(x)][0]
				name = source_utils.clean_name(file_title[0])

				if not source_utils.check_title(title, aliases, name.replace('.(Archie.Bunker', ''), hdlr, year, years): continue
				name_info = source_utils.info_from_name(name, title, year, hdlr, episode_title)
				if source_utils.remove_lang(name_info, check_foreign_audio): continue
				if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

				url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name) 
				try:
					seeders = int(re.search(r'(\d+)', file_info).group(1))
					if self.min_seeders > seeders: continue
				except: seeders = 0
				host='load.to'
				quality, info = source_utils.get_release_quality(name_info, url)
				try:
					size = re.search(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', file_info).group(0)
					dsize, isize = source_utils._size(size)
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)

				sources_append({'provider': 'torrents', 'source': host, 'seeders': seeders, 'name': name+' '+str(seeders), 'name_info': name_info,
											'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': 'elementum', 'debridonly': False, 'size': dsize})
			except:
				source_utils.scraper_error('TORRENTIO')
		return sources

	def sources_packs(self, data, hostDict, search_series=False, total_seasons=None, bypass_filter=False):
		sources = []
		if not data: return sources
		sources_append = sources.append
		try:
			title = data['tvshowtitle'].replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ').replace('$', 's')
			aliases = data['aliases']
			imdb = data['imdb']
			year = data['year']
			season = data['season']
			url = '%s%s' % (self.base_link, self.tvSearch_link % (imdb, season, data['episode']))
			results = client.request(url, timeout=5)
			try: files = jsloads(results)['streams']
			except: return sources
			_INFO = re.compile(r'👤.*')
			undesirables = source_utils.get_undesirables()
			check_foreign_audio = source_utils.check_foreign_audio()
		except:
			source_utils.scraper_error('TORRENTIO')
			return sources

		for file in files:
			try:
				hash = file['infoHash']
				file_title = file['title'].split('\n')
				file_info = [x for x in file_title if _INFO.match(x)][0]
				name = source_utils.clean_name(file_title[0])

				episode_start, episode_end = 0, 0
				if not search_series:
					if not bypass_filter:
						valid, episode_start, episode_end = source_utils.filter_season_pack(title, aliases, year, season, name.replace('.(Archie.Bunker', ''))
						if not valid: continue
					package = 'season'

				elif search_series:
					if not bypass_filter:
						valid, last_season = source_utils.filter_show_pack(title, aliases, imdb, year, season, name.replace('.(Archie.Bunker', ''), total_seasons)
						if not valid: continue
					else: last_season = total_seasons
					package = 'show'

				name_info = source_utils.info_from_name(name, title, year, season=season, pack=package)
				if source_utils.remove_lang(name_info, check_foreign_audio): continue
				if undesirables and source_utils.remove_undesirables(name_info, undesirables): continue

				url = 'magnet:?xt=urn:btih:%s&dn=%s' % (hash, name)
				try:
					seeders = int(re.search(r'(\d+)', file_info).group(1))
					if self.min_seeders > seeders: continue
				except: seeders = 0

				quality, info = source_utils.get_release_quality(name_info, url)
				try:
					size = re.search(r'((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', file_info).group(0)
					dsize, isize = source_utils._size(size)
					info.insert(0, isize)
				except: dsize = 0
				info = ' | '.join(info)
				host='load.to'
				item = {'provider': 'torrents', 'source': host, 'seeders': seeders, 'name': name+' '+str(seeders), 'name_info': name_info, 'quality': quality,
							'language': 'en', 'url': url, 'info': info, 'direct': 'elementum', 'debridonly': False, 'size': dsize, 'package': package}
				if search_series: item.update({'last_season': last_season})
				elif episode_start: item.update({'episode_start': episode_start, 'episode_end': episode_end}) # for partial season packs
				sources_append(item)
			except:
				source_utils.scraper_error('TORRENTIO')
		return sources