# -*- coding: utf-8 -*-
import time
from windows.base_window import open_window, create_window
from scrapers import external, folders
from modules import debrid, kodi_utils, settings, metadata, watched_status
from modules.player import FenPlayer
from modules.source_utils import get_cache_expiry, make_alias_dict
from modules.utils import clean_file_name, string_to_float, safe_string, remove_accents, get_datetime, append_module_to_syspath, manual_function_import, manual_module_import
# logger = kodi_utils.logger

ls, get_icon, notification, sleep, int_window_prop = kodi_utils.local_string, kodi_utils.get_icon, kodi_utils.notification, kodi_utils.sleep, kodi_utils.int_window_prop
select_dialog, confirm_dialog, get_setting, close_all_dialog = kodi_utils.select_dialog, kodi_utils.confirm_dialog, kodi_utils.get_setting, kodi_utils.close_all_dialog
json, show_busy_dialog, hide_busy_dialog, xbmc_player = kodi_utils.json, kodi_utils.show_busy_dialog, kodi_utils.hide_busy_dialog, kodi_utils.xbmc_player
Thread, get_property, set_property, clear_property = kodi_utils.Thread, kodi_utils.get_property, kodi_utils.set_property, kodi_utils.clear_property
display_uncached_torrents, check_prescrape_sources, source_folders_directory = settings.display_uncached_torrents, settings.check_prescrape_sources, settings.source_folders_directory
auto_play, active_internal_scrapers, provider_sort_ranks, audio_filters = settings.auto_play, settings.active_internal_scrapers, settings.provider_sort_ranks, settings.audio_filters
results_format, results_style, results_xml_window_number, filter_status = settings.results_format, settings.results_style, settings.results_xml_window_number, settings.filter_status
metadata_user_info, quality_filter, sort_to_top, monitor_playback = settings.metadata_user_info, settings.quality_filter, settings.sort_to_top, settings.monitor_playback
scraping_settings, include_prerelease_results, auto_rescrape_with_all = settings.scraping_settings, settings.include_prerelease_results, settings.auto_rescrape_with_all
playback_attempt_pause, get_art_provider, external_scraper_info = settings.playback_attempt_pause, settings.get_art_provider, settings.external_scraper_info
ignore_results_filter, results_sort_order, easynews_max_retries = settings.ignore_results_filter, settings.results_sort_order, settings.easynews_max_retries
autoplay_next_episode, autoscrape_next_episode, limit_resolve = settings.autoplay_next_episode, settings.autoscrape_next_episode, settings.limit_resolve
debrid_enabled, debrid_type_enabled, debrid_valid_hosts = debrid.debrid_enabled, debrid.debrid_type_enabled, debrid.debrid_valid_hosts
erase_bookmark, clear_local_bookmarks = watched_status.erase_bookmark, watched_status.clear_local_bookmarks
get_progress_percent, get_bookmarks = watched_status.get_progress_percent, watched_status.get_bookmarks
internal_include_list = ['easynews', 'furk', 'pm_cloud', 'rd_cloud', 'ad_cloud']
external_exclude_list = ['furk', 'easynews', 'gdrive', 'library', 'filepursuit', 'plexshare']
sd_check = ('SD', 'CAM', 'TELE', 'SYNC')
rd_info, pm_info, ad_info = ('apis.real_debrid_api', 'RealDebridAPI'), ('apis.premiumize_api', 'PremiumizeAPI'), ('apis.alldebrid_api', 'AllDebridAPI')
debrids = {'Real-Debrid': rd_info, 'rd_cloud': rd_info, 'rd_browse': rd_info, 'Premiumize.me': pm_info, 'pm_cloud': pm_info, 'pm_browse': pm_info,
			'AllDebrid': ad_info, 'ad_cloud': ad_info, 'ad_browse': ad_info}
debrid_providers = ('Real-Debrid', 'Premiumize.me', 'AllDebrid')
quality_ranks = {'4K': 1, '1080p': 2, '720p': 3, 'SD': 4, 'SCR': 5, 'CAM': 5, 'TELE': 5}
cloud_scrapers, folder_scrapers = ('rd_cloud', 'pm_cloud', 'ad_cloud'), ('folder1', 'folder2', 'folder3', 'folder4', 'folder5')
default_internal_scrapers = ('furk', 'easynews', 'rd_cloud', 'pm_cloud', 'ad_cloud', 'folders')
main_line = '%s[CR]%s[CR]%s'
scraper_timeout = 25
global stop # telemedia
stop=False # telemedia
class Sources():
	def __init__(self):
		self.params = {}
		self.prescrape_scrapers, self.prescrape_threads, self.prescrape_sources, self.uncached_torrents = [], [], [], []
		self.threads, self.providers, self.sources, self.internal_scraper_names, self.remove_scrapers = [], [], [], [], ['external']
		self.post_results_processed, self.clear_properties, self.filters_ignored, self.active_folders, self.resolve_dialog_made = False, True, False, False, False
		self.sources_total = self.sources_4k = self.sources_1080p = self.sources_720p = self.sources_sd = 0
		self.prescrape, self.disabled_ext_ignored, self.default_ext_only = 'true', 'false', 'false'
		self.ext_name, self.ext_folder, self.ext_default_providers, self.ext_sources = '', '', None, None
		self.progress_dialog = None
		self.playing_filename = ''
		self.monitor_playback = monitor_playback()
		self.easynews_max_retries = easynews_max_retries()
		self.playback_attempt_pause = playback_attempt_pause()
		self.count_tuple = (('sources_4k', '4K', self._quality_length), ('sources_1080p', '1080p', self._quality_length), ('sources_720p', '720p', self._quality_length),
							('sources_sd', '', self._quality_length_sd), ('sources_total', '', self.quality_length_final))

	def playback_prep(self, params=None):
		hide_busy_dialog()
		if params: self.params = params
		params_get = self.params.get
		self.play_type, self.background, self.prescrape = params_get('play_type', ''), params_get('background', 'false') == 'true', params_get('prescrape', self.prescrape) == 'true'
		self.random, self.random_continual = params_get('random', 'false') == 'true', params_get('random_continual', 'false') == 'true'
		if self.play_type:
			if self.play_type == 'autoplay_nextep': self.autoplay_nextep, self.autoscrape_nextep = True, False
			elif self.play_type == 'random_continual': self.autoplay_nextep, self.autoscrape_nextep = False, False
			else: self.autoplay_nextep, self.autoscrape_nextep = False, True
		else: self.autoplay_nextep, self.autoscrape_nextep = autoplay_next_episode(), autoscrape_next_episode()
		self.autoscrape = self.autoscrape_nextep and self.background
		self.auto_rescrape_with_all = auto_rescrape_with_all()
		self.nextep_settings, self.disable_autoplay_next_episode = params_get('nextep_settings', {}), params_get('disable_autoplay_next_episode', 'false') == 'true'
		self.ignore_scrape_filters = params_get('ignore_scrape_filters', 'false') == 'true'
		self.disabled_ext_ignored = params_get('disabled_ext_ignored', self.disabled_ext_ignored) == 'true'
		self.default_ext_only = params_get('default_ext_only', self.default_ext_only) == 'true'
		self.folders_ignore_filters = get_setting('cobra.results.folders_ignore_filters', 'false') == 'true'
		self.media_type, self.tmdb_id, self.ep_name, self.plot = params_get('media_type'), params_get('tmdb_id'), params_get('ep_name'), params_get('plot')
		self.custom_title, self.custom_year = params_get('custom_title', None), params_get('custom_year', None)
		self.custom_season, self.custom_episode = params_get('custom_season', None), params_get('custom_episode', None)
		if 'autoplay' in self.params: self.autoplay = self.params.get('autoplay', 'false') == 'true'
		else: self.autoplay = auto_play(self.media_type)
		if 'season' in self.params: self.season = int(params_get('season'))
		else: self.season = ''
		if 'episode' in self.params: self.episode = int(params_get('episode'))
		else: self.episode = ''
		if 'meta' in self.params: self.meta = json.loads(params_get('meta'))
		else: self._grab_meta()
		self.active_internal_scrapers = active_internal_scrapers()
		if not 'external' in self.active_internal_scrapers and (self.disabled_ext_ignored or self.default_ext_only): self.active_internal_scrapers.append('external')
		self.active_external = 'external' in self.active_internal_scrapers
		self.sleep_time, self.provider_sort_ranks, self.scraper_settings = 100, provider_sort_ranks(), scraping_settings()
		self.include_prerelease_results, self.ignore_results_filter, self.limit_resolve = include_prerelease_results(), ignore_results_filter(), limit_resolve()
		self.filter_hevc, self.filter_hdr = filter_status('hevc'), filter_status('hdr')
		self.filter_dv, self.filter_av1, self.filter_audio = filter_status('dv'), filter_status('av1'), 3
		self.hevc_filter_key, self.hdr_filter_key, self.dolby_vision_filter_key, self.av1_filter_key = '[B]HEVC[/B]', '[B]HDR[/B]', '[B]D/VISION[/B]', '[B]AV1[/B]'
		self.audio_filter_key = audio_filters()
		self.sort_function, self.display_uncached_torrents, self.quality_filter = results_sort_order(), display_uncached_torrents(), self._quality_filter()
		self.hybrid_allowed, self.filter_size_method = self.filter_hdr in (0, 2), int(get_setting('cobra.results.filter_size_method', '0'))
		self.include_unknown_size = get_setting('cobra.results.include.unknown.size', 'false') == 'true'
		self.include_3D_results = get_setting('cobra.include_3d_results', 'true') == 'true'
		self._update_meta()
		self._search_info()
		if self.autoscrape: self.autoscrape_nextep_handler()
		else: return self.get_sources()

	def get_sources(self):
		if not self.progress_dialog and not self.background: self._make_progress_dialog()
		results = []
		if self.prescrape and any(x in self.active_internal_scrapers for x in default_internal_scrapers):
			if self.prepare_internal_scrapers():
				results = self.collect_prescrape_results()
				if results: results = self.process_results(results)
		if not results:
			self.prescrape = False
			self.prepare_internal_scrapers()
			if self.active_external:
				self.activate_debrid_info()
				self.activate_external_providers()
			elif not self.active_internal_scrapers: self._kill_progress_dialog()
			self.orig_results = self.collect_results()
			if not self.orig_results and not self.active_external: self._kill_progress_dialog()
			results = self.process_results(self.orig_results)
		if not results: return self._process_post_results()
		if self.autoscrape: return results
		else: return self.play_source(results)

	def collect_results(self):
		self.sources.extend(self.prescrape_sources)
		threads_append = self.threads.append
		if self.active_folders: self.append_folder_scrapers(self.providers)
		self.providers.extend(self.internal_sources())
		if self.providers:
			for i in self.providers: threads_append(Thread(target=self.activate_providers, args=(i[0], i[1], False), name=i[2]))
			[i.start() for i in self.threads]
		if self.active_external or self.background:
			if self.active_external:
				self.external_args = (self.meta, self.external_providers, self.debrid_torrent_enabled, self.debrid_hoster_enabled, self.internal_scraper_names,
										self.prescrape_sources, self.progress_dialog, self.disabled_ext_ignored)
				self.activate_providers('external', external, False)
			if self.background: [i.join() for i in self.threads]
		elif self.active_internal_scrapers: self.scrapers_dialog()
		return self.sources

	def collect_prescrape_results(self):
		threads_append = self.prescrape_threads.append
		if self.active_folders:
			if self.autoplay or check_prescrape_sources('folders', self.media_type):
				self.append_folder_scrapers(self.prescrape_scrapers)
				self.remove_scrapers.append('folders')
		self.prescrape_scrapers.extend(self.internal_sources(True))
		if not self.prescrape_scrapers: return []
		for i in self.prescrape_scrapers: threads_append(Thread(target=self.activate_providers, args=(i[0], i[1], True), name=i[2]))
		[i.start() for i in self.prescrape_threads]
		self.remove_scrapers.extend(i[2] for i in self.prescrape_scrapers)
		if self.background: [i.join() for i in self.prescrape_threads]
		else: self.scrapers_dialog()
		return self.prescrape_sources

	def process_results(self, results):
		if self.prescrape: self.all_scrapers = self.active_internal_scrapers
		else:
			self.all_scrapers = list(set(self.active_internal_scrapers + self.remove_scrapers))
			clear_property('fs_filterless_search')
		self.uncached_torrents = self.sort_results([i for i in results if 'Uncached' in i.get('cache_provider', '')])
		if not self.display_uncached_torrents: results = [i for i in results if not i in self.uncached_torrents]
		if self.ignore_scrape_filters:
			self.filters_ignored = True
			results = self.sort_results(results)
			results = self._sort_first(results)
		else:
			results = self.filter_results(results)
			results = self.sort_results(results)
			results = self._special_filter(results, self.audio_filter_key, self.filter_audio)
			results = self._special_filter(results, self.hdr_filter_key, self.filter_hdr)
			results = self._special_filter(results, self.dolby_vision_filter_key, self.filter_dv)
			results = self._special_filter(results, self.av1_filter_key, self.filter_av1)
			results = self._special_filter(results, self.hevc_filter_key, self.filter_hevc)
			results = self._sort_first(results)
		return results

	def filter_results(self, results):
		if self.folders_ignore_filters:
			folder_results = [i for i in results if i['scrape_provider'] == 'folders']
			results = [i for i in results if not i in folder_results]
		else: folder_results = []
		results = [i for i in results if i['quality'] in self.quality_filter]
		if not self.include_3D_results: results = [i for i in results if not '3D' in i['extraInfo']]
		if self.filter_size_method:
			min_size = string_to_float(get_setting('cobra.results.size.min_manual', '0'), '0') / 1000
			if min_size == 0.0 and not self.include_unknown_size: min_size = 0.02
			if self.filter_size_method == 1:
				duration = self.meta['duration'] or (5400 if self.media_type == 'movie' else 2400)
				max_size = ((0.125 * (0.90 * string_to_float(get_setting('cobra.results.size.auto', '20'), '20'))) * duration)/1000
			elif self.filter_size_method == 2:
				max_size = string_to_float(get_setting('cobra.results.size.manual', '10000'), '10000') / 1000
			results = [i for i in results if i['scrape_provider'] == 'folders' or min_size <= i['size'] <= max_size]
		results += folder_results
		return results

	def sort_results(self, results):
		def _add_keys(item):
			provider = item['scrape_provider']
			if provider == 'external': account_type = item['debrid'].lower()
			else: account_type = provider.lower()
			item['provider_rank'] = self._get_provider_rank(account_type)
			item['quality_rank'] = self._get_quality_rank(item.get('quality', 'SD'))
		for item in results: _add_keys(item)
		try:#מתקן את השגיאה seeders
			results.sort(key=self.sort_function)
		except:pass
		results = self._sort_uncached_torrents(results)
		return results

	def prepare_internal_scrapers(self):
		if self.active_external and len(self.active_internal_scrapers) == 1: return
		active_internal_scrapers = [i for i in self.active_internal_scrapers if not i in self.remove_scrapers]
		if self.prescrape and not self.active_external and all([check_prescrape_sources(i, self.media_type) for i in active_internal_scrapers]): return False
		if 'folders' in active_internal_scrapers:
			self.folder_info = [i for i in self.get_folderscraper_info() if settings.source_folders_directory(self.media_type, i[1])]
			if self.folder_info:
				self.active_folders = True
				self.internal_scraper_names = [i for i in active_internal_scrapers if not i == 'folders'] + [i[0] for i in self.folder_info]
			else: self.internal_scraper_names = [i for i in active_internal_scrapers if not i == 'folders']
		else:
			self.folder_info = []
			self.internal_scraper_names = active_internal_scrapers[:]
		self.active_internal_scrapers = active_internal_scrapers
		if self.clear_properties: self._clear_properties()
		return True

	def activate_providers(self, module_type, function, prescrape):
		sources = self._get_module(module_type, function).results(self.search_info)
		# if sources==[]:# telemedia

			# sleep(500)#מחפש שוב מקורות כי לפעמים הם לא מופיעים
			# sources = self._get_module(module_type, function).results(self.search_info)
		# if sources==[]:

			# sleep(500)
			# sources = self._get_module(module_type, function).results(self.search_info)

		if not sources: return
		if prescrape: self.prescrape_sources.extend(sources)
		else: self.sources.extend(sources)

	def activate_debrid_info(self):
		self.debrid_enabled = debrid_enabled()
		self.debrid_torrent_enabled = debrid_type_enabled('torrent', self.debrid_enabled)
		self.debrid_hoster_enabled = debrid_valid_hosts(debrid_type_enabled('hoster', self.debrid_enabled))

	def activate_external_providers(self):
		# if not self.debrid_torrent_enabled and not self.debrid_hoster_enabled:# telemedia
		#בוטל עם מופעל חשבון RD
		if 0:
			if len(self.active_internal_scrapers) == 1 and 'external' in self.active_internal_scrapers: self.disable_external(32854)
		else:
			self.ext_folder, self.ext_name = external_scraper_info()
			if not self.ext_folder or not self.ext_name: return self.disable_external(33007)
			if not self.import_external_scrapers(): return self.disable_external(33009)
			exclude_list = []
			if not self.debrid_torrent_enabled: exclude_list.extend(self.external_scraper_names('torrents'))
			elif not self.debrid_hoster_enabled: exclude_list.extend(self.external_scraper_names('hosters'))
			self.external_providers = self.external_sources()+self.telemedia_torrent_sources()# telemedia
			if not self.external_providers: self.disable_external(33008)
			if exclude_list: self.external_providers = [i for i in self.external_providers if not i[0] in exclude_list]
	
	def import_external_scrapers(self):
		try:
			append_module_to_syspath('special://home/addons/%s/lib' % self.ext_folder)
			self.ext_sources = manual_module_import('%s.sources_%s' % (self.ext_name, self.ext_name))
			self.ext_default_providers = manual_function_import('%s.modules.control' % self.ext_name, 'getProviderDefaults')
		except: return False
		return True

	def disable_external(self, line1):
		notification(line1, 2000)
		try: self.active_internal_scrapers.remove('external')
		except: pass
		self.active_external = False
		self.external_providers = []

	def external_scraper_names(self, folder):
		if folder == 'torrents': return [i for i in self.ext_sources.torrent_providers if not i in external_exclude_list]
		elif folder == 'hosters': return [i for i in self.ext_sources.hoster_providers if not i in external_exclude_list]
		else: return [i for i in self.ext_sources.all_providers if not i in external_exclude_list]

	def internal_sources(self, prescrape=False):
		active_sources = [i for i in self.active_internal_scrapers if i in internal_include_list]
		try: sourceDict = [('internal', manual_function_import('scrapers.%s' % i, 'source'), i) for i in active_sources \
												if not (prescrape and not check_prescrape_sources(i, self.media_type))]
		except: sourceDict = []
		return sourceDict

	def external_sources(self):
		try:
			if self.disabled_ext_ignored: active_sources = self.ext_sources.total_providers['torrents']
			elif self.default_ext_only: active_sources = [k.split('.')[1] for k, v in self.ext_default_providers().items() if v == 'true']
			else: active_sources = [i for i in self.ext_sources.total_providers['torrents'] if \
									json.loads(get_property('%s_settings' % self.ext_name)).get('provider.%s' % i, 'false') == 'true']
			sourceDict = [(i, manual_function_import('%s.sources_%s.%s.%s' % (self.ext_name, self.ext_name, 'torrents', i), 'source')) for i in active_sources]
		except: sourceDict = self.legacy_external_sources()
		return sourceDict

	def legacy_external_sources(self):
		try: sourceDict = manual_function_import(self.ext_name, 'sources')(specified_folders=['torrents'], ret_all=self.disabled_ext_ignored)
		except: sourceDict = []
		return sourceDict
	def telemedia_torrent_sources(self):# telemedia
		try: sourceDict = manual_function_import(self.ext_name, 'sources')(specified_folders=['hosters'], ret_all=self.disabled_ext_ignored)
		except: sourceDict = []
		return sourceDict
	def folder_sources(self):
		def import_info():
			for item in self.folder_info:
				scraper_name = item[0]
				module = manual_function_import('scrapers.folders', 'source')
				yield ('folders', (module, (item[1], scraper_name, item[2])), scraper_name)
		sourceDict = list(import_info())
		try: sourceDict = list(import_info())
		except: sourceDict = []
		return sourceDict

	def play_source(self, results):
		if self.background or self.autoplay: return self.play_file(results)
		return self.display_results(results)

	def append_folder_scrapers(self, current_list):
		current_list.extend(self.folder_sources())

	def get_folderscraper_info(self):
		folder_info = [(get_setting('cobra.%s.display_name' % i), i, source_folders_directory(self.media_type, i)) for i in folder_scrapers]
		return [i for i in folder_info if not i[0] in (None, 'None', '') and i[2]]

	def scrapers_dialog(self):
		def _scraperDialog():
			monitor = kodi_utils.monitor
			start_time = time.time()
			while not self.progress_dialog.iscanceled() and not monitor.abortRequested():
				try:
					remaining_providers = [x.getName() for x in _threads if x.is_alive() is True]
					self._process_internal_results()
					current_progress = max((time.time() - start_time), 0)
					line1 = ', '.join(remaining_providers).upper()
					percent = int((current_progress/float(scraper_timeout))*100)
					self.progress_dialog.update_scraper(self.sources_sd, self.sources_720p, self.sources_1080p, self.sources_4k, self.sources_total, line1, percent)
					sleep(self.sleep_time)
					if len(remaining_providers) == 0: break
					if percent >= 100: break
				except:	return self._kill_progress_dialog()
		if self.prescrape: scraper_list, _threads = self.prescrape_scrapers, self.prescrape_threads
		else: scraper_list, _threads = self.providers, self.threads
		self.internal_scrapers = self._get_active_scraper_names(scraper_list)
		if not self.internal_scrapers: return
		_scraperDialog()
		try: del monitor
		except: pass

	def display_results(self, results):
		window_format = results_format()
		action, chosen_item = open_window(('windows.sources', 'SourcesResults'), 'sources_results.xml',
				window_format=window_format, window_style=results_style(), window_id=results_xml_window_number(window_format), results=results, meta=self.meta,
				scraper_settings=self.scraper_settings, prescrape=self.prescrape, filters_ignored=self.filters_ignored, uncached_torrents=self.uncached_torrents)
		if not action: self._kill_progress_dialog()
		elif action == 'play': return self.play_file(results, chosen_item)
		elif self.prescrape and action == 'perform_full_search':
			self.prescrape, self.clear_properties = False, False
			return self.get_sources()

	def _get_active_scraper_names(self, scraper_list):
		return [i[2] for i in scraper_list]

	def _process_post_results(self):
		if self.auto_rescrape_with_all and self.active_external and not self.post_results_processed:
			self.threads, self.post_results_processed, self.disabled_ext_ignored, self.prescrape = [], True, True, False
			return self.get_sources()
		if self.orig_results and not self.background:
			if self.display_uncached_torrents and not self.autoplay: return self.play_source(self.uncached_torrents)
			if self.ignore_results_filter == 0: return self._no_results()
			if self.ignore_results_filter == 1 or confirm_dialog(heading=self.meta.get('rootname', ''), text=32021): return self._process_ignore_filters()
		return self._no_results()

	def _process_ignore_filters(self):
		if self.autoplay: notification('%s & %s' % (ls(32686), ls(32071)))
		self.filters_ignored, self.autoplay = True, False
		results = self.sort_results(self.orig_results)
		results = self._sort_first(results)
		return self.play_source(results)

	def _no_results(self):
		from caches.providers_cache import ExternalProvidersCache
		from caches.base_cache import clear_cache
		self._kill_progress_dialog()
		hide_busy_dialog()
		if self.background: return notification('%s %s' % (ls(32801), ls(32760)), 5000)
		notification(32760, 2000)
		deleted = ExternalProvidersCache().delete_cache_single(self.media_type, str(self.meta['tmdb_id']))
		for item in ('internal_scrapers', 'external_scrapers'): clear_cache(item, silent=True)
		# if self.get_search_year()=='2023' or self.get_search_year()=='2024':
			# title, original_title = self.get_search_title_heb(), self.get_search_title_heb()
			# from modules import moviesdates
			# return moviesdates.moviesdates_parser(search_movie_bool='next', title=title, original_title=original_title)
		#מנקה קאש אם אין תוצאות 
		#telemedia
	def _update_meta(self):
		self.meta.update({'media_type': self.media_type, 'season': self.season, 'episode': self.episode, 'background': self.background, 'custom_title': self.custom_title,
						'custom_year': self.custom_year, 'custom_season': self.custom_season, 'custom_episode': self.custom_episode})

	def _search_info(self):
		title_heb = self.get_search_title_heb()
		title, year, season, episode, ep_name = self.get_search_title(), self.get_search_year(), self.get_season(), self.get_episode(), self.get_ep_name()
		aliases = make_alias_dict(self.meta, title)
		expiry_times = get_cache_expiry(self.media_type, self.meta, self.season)
		self.search_info = {'media_type': self.media_type, 'title': title, 'year': year, 'tmdb_id': self.tmdb_id, 'imdb_id': self.meta.get('imdb_id'), 'aliases': aliases,
							'season': season, 'episode': episode, 'tvdb_id': self.meta.get('tvdb_id'), 'ep_name': ep_name, 'expiry_times': expiry_times,
							'total_seasons': self.meta.get('total_seasons', 1),'title_heb':title_heb}
	def get_search_title_heb(self):
		search_title = None
		search_title = self.meta['title']
		if '(' in search_title: search_title = search_title.split('(')[0]
		search_title.replace('/', ' ')
		return search_title
	def get_search_title(self):# telemedia
		search_title = None
		custom_title = self.meta.get('custom_title', None)
		if custom_title: search_title = custom_title
		else:
			if get_setting('cobra.meta_language') == 'en': search_title = self.meta['title']
			else:
				english_title = self.meta.get('english_title')
				if english_title: search_title = english_title
				else:
					try:
						media_type = 'movie' if self.media_type == 'movie' else 'tv'
						meta_user_info = metadata_user_info()
						english_title = metadata.english_translation(media_type, self.meta['tmdb_id'], meta_user_info)
						if english_title: search_title = english_title
						else: search_title = self.meta['original_title']
					except: pass
				if not search_title: search_title = self.meta['original_title']
			if '(' in search_title: search_title = search_title.split('(')[0]
			search_title.replace('/', ' ')
		return search_title

	def get_search_year(self):
		custom_year = self.meta.get('custom_year', None)
		if custom_year: year = custom_year
		else:
			year = self.meta.get('year')
			if self.active_external and get_setting('cobra.search.enable.yearcheck', 'false') == 'true':
				from apis.imdb_api import imdb_year_check
				try:
					imdb_year = str(imdb_year_check(self.meta.get('imdb_id')))
					if imdb_year: year = imdb_year
				except: pass
		return year

	def get_season(self):
		season = self.meta.get('custom_season', None) or self.meta.get('season')
		try: season = int(season)
		except: season = None
		return season

	def get_episode(self):
		episode = self.meta.get('custom_episode', None) or self.meta.get('episode')
		try: episode = int(episode)
		except: episode = None
		return episode

	def get_ep_name(self):
		ep_name = None
		if self.meta['media_type'] == 'episode':
			ep_name = self.meta.get('ep_name')
			try: ep_name = safe_string(remove_accents(ep_name))
			except: ep_name = safe_string(ep_name)
		return ep_name

	def _process_internal_results(self):
		for i in self.internal_scrapers:
			win_property = get_property(int_window_prop % i)
			if win_property in ('checked', '', None): continue
			try: sources = json.loads(win_property)
			except: continue
			set_property(int_window_prop % i, 'checked')
			self._sources_quality_count(sources)
	
	def _sources_quality_count(self, sources):
		for item in self.count_tuple: setattr(self, item[0], getattr(self, item[0]) + item[2](sources, item[1]))

	def _quality_filter(self):
		setting = 'results_quality_%s' % self.media_type if not self.autoplay else 'autoplay_quality_%s' % self.media_type
		filter_list = quality_filter(setting)
		if self.include_prerelease_results and 'SD' in filter_list: filter_list += ['SCR', 'CAM', 'TELE']
		return filter_list

	def _get_quality_rank(self, quality):
		return quality_ranks[quality]

	def _get_provider_rank(self, account_type):
		return self.provider_sort_ranks[account_type] or 11

	def _sort_first(self, results):
		try:
			sort_first_scrapers = []
			if 'folders' in self.all_scrapers and sort_to_top('folders'): sort_first_scrapers.append('folders')
			sort_first_scrapers.extend([i for i in self.all_scrapers if i in cloud_scrapers and sort_to_top(i)])
			if not sort_first_scrapers: return results
			sort_first = [i for i in results if i['scrape_provider'] in sort_first_scrapers]
			sort_first.sort(key=lambda k: (self._sort_folder_to_top(k['scrape_provider']), k['quality_rank']))
			sort_last = [i for i in results if not i in sort_first]
			results = sort_first + sort_last
		except: pass
		return results

	def _sort_folder_to_top(self, provider):
		if provider == 'folders': return 0
		else: return 1

	def _sort_uncached_torrents(self, results):
		uncached = [i for i in results if 'Uncached' in i.get('cache_provider', '')]
		cached = [i for i in results if not i in uncached]
		return cached + uncached

	def _special_filter(self, results, key, enable_setting):
		if key == self.hevc_filter_key and enable_setting in (0,2):
			hevc_max_quality = self._get_quality_rank(get_setting('cobra.filter_hevc.%s' % ('max_autoplay_quality' if self.autoplay else 'max_quality'), '4K'))
			results = [i for i in results if not key in i['extraInfo'] or i['quality_rank'] >= hevc_max_quality]
		if enable_setting == 1:
			if key == self.dolby_vision_filter_key and self.hybrid_allowed:
				results = [i for i in results if all(x in i['extraInfo'] for x in (key, self.hdr_filter_key)) or not key in i['extraInfo']]
			else: results = [i for i in results if not key in i['extraInfo']]
		elif enable_setting == 2 and self.autoplay:
			priority_list = [i for i in results if key in i['extraInfo']]
			remainder_list = [i for i in results if not i in priority_list]
			results = priority_list + remainder_list
		elif enable_setting == 3: results = [i for i in results if not any(x in i['extraInfo'] for x in key)]
		return results

	def _grab_meta(self):
		meta_user_info = metadata_user_info()
		if self.media_type == 'movie': self.meta = metadata.movie_meta('tmdb_id', self.tmdb_id, meta_user_info, get_datetime())
		else:
			self.meta = metadata.tvshow_meta('tmdb_id', self.tmdb_id, meta_user_info, get_datetime())
			episodes_data = metadata.episodes_meta(self.season, self.meta, meta_user_info)
			try:
				episode_data = [i for i in episodes_data if i['episode'] == self.episode][0]
				art_providers = get_art_provider()
				thumb = episode_data.get('thumb', None) or self.meta.get('custom_fanart') or self.meta.get(art_providers[2]) or self.meta.get(art_providers[3]) or ''
				self.meta['tvshow_plot'] = self.meta['plot']
				self.meta.update({'media_type': 'episode', 'season': episode_data['season'], 'episode': episode_data['episode'], 'premiered': episode_data['premiered'],
								'ep_name': episode_data['title'], 'ep_thumb': episode_data.get('thumb', None), 'plot': episode_data['plot']})
			except: pass

	def _get_module(self, module_type, function):
		if module_type == 'external': module = function.source(*self.external_args)
		elif module_type == 'folders': module = function[0](*function[1])
		else: module = function()
		return module

	def _clear_properties(self):
		for item in default_internal_scrapers: clear_property(int_window_prop % item)
		if self.active_folders:
			for item in self.folder_info: clear_property(int_window_prop % item[0])

	def _make_progress_dialog(self):
		self.progress_dialog = create_window(('windows.sources', 'SourcesPlayback'), 'sources_playback.xml', meta=self.meta)
		Thread(target=self.progress_dialog.run).start()

	def _make_resolve_dialog(self):
		self.resolve_dialog_made = True
		if not self.progress_dialog: self._make_progress_dialog()
		self.progress_dialog.enable_resolver()

	def _make_resume_dialog(self, percent):
		if not self.progress_dialog: self._make_progress_dialog()
		self.progress_dialog.enable_resume(percent)
		return self.progress_dialog.resume_choice

	def _make_nextep_dialog(self, default_action='cancel', play_type='autoplay_nextep', focus_button=10):
		try: action = open_window(('windows.next_episode', 'NextEpisode'), 'next_episode.xml',
			meta=self.meta, default_action=default_action, play_type=play_type, focus_button=focus_button)
		except: action = 'cancel'
		return action

	def _kill_progress_dialog(self):
		try: self.progress_dialog.close()
		except: close_all_dialog()
		try: del self.progress_dialog
		except: pass
		self.progress_dialog = None

	def furkPacks(self, name, file_id, download=False):
		from apis.furk_api import FurkAPI
		show_busy_dialog()
		t_files = FurkAPI().t_files(file_id)
		t_files = [i for i in t_files if 'video' in i['ct'] and 'bitrate' in i]
		t_files.sort(key=lambda k: k['name'].lower())
		hide_busy_dialog()
		if download: return t_files
		list_items = [{'line1': '%.2f GB | %s' % (float(item['size'])/1073741824, clean_file_name(item['name']).upper())} for item in t_files]
		kwargs = {'items': json.dumps(list_items), 'heading': name, 'enumerate': 'true', 'narrow_window': 'true'}
		chosen_result = select_dialog(t_files, **kwargs)
		if chosen_result is None: return None
		link = chosen_result['url_dl']
		name = chosen_result['name']
		self._kill_progress_dialog()
		return FenPlayer().run(link, 'video')

	def debridPacks(self, debrid_provider, name, magnet_url, info_hash, download=False):
		show_busy_dialog()
		debrid_info = {'Real-Debrid': 'rd_browse', 'Premiumize.me': 'pm_browse', 'AllDebrid': 'ad_browse'}[debrid_provider]
		debrid_function = self.debrid_importer(debrid_info)
		try: debrid_files = debrid_function().display_magnet_pack(magnet_url, info_hash)
		except: debrid_files = None
		debrid_files = debrid_function().display_magnet_pack(magnet_url, info_hash)
		hide_busy_dialog()
		if not debrid_files: return notification(32574)
		debrid_files.sort(key=lambda k: k['filename'].lower())
		if download: return debrid_files, debrid_function
		list_items = [{'line1': '%.2f GB | %s' % (float(item['size'])/1073741824, clean_file_name(item['filename']).upper())} for item in debrid_files]
		kwargs = {'items': json.dumps(list_items), 'heading': name, 'enumerate': 'true', 'narrow_window': 'true'}
		chosen_result = select_dialog(debrid_files, **kwargs)
		if chosen_result is None: return None
		link = self.resolve_internal_sources(debrid_info, chosen_result['link'], '')
		name = chosen_result['filename']
		self._kill_progress_dialog()
		return FenPlayer().run(link, 'video')

	def play_file(self, results, source={}):
		self.playback_successful, self.cancel_all_playback = None, False
		tele=''# telemedia
		try:
			hide_busy_dialog()
			url = None
			results = [i for i in results if not 'Uncached' in i.get('cache_provider', '')]
			if not source: source = results[0]
			items = [source]
			try:
				tele=[source][0]
				tele=tele['provider']
			except:pass


			if 'telemedia' not in tele:# מבטל החלפת מקורות בניגון מטלמדיה# telemedia
				if not self.limit_resolve: 
					source_index = results.index(source)
					results.remove(source)
					leading_index = max(source_index-3, 0)
					items_prev = results[leading_index:source_index]
					trailing_index = 7 - len(items_prev)
					items_next = results[source_index+1:source_index+trailing_index]
					items = items + items_next + items_prev
			processed_items = []
			processed_items_append = processed_items.append
			for count, item in enumerate(items, 1):
				resolve_item = dict(item)
				provider = item['scrape_provider']
				if provider == 'external': provider = item['debrid'].replace('.me', '')
				elif provider == 'folders': provider = item['source']
				provider_text = provider.upper()
				if 'telemedia' == tele:# מציג את השם טלמדיה במסך הניגון# telemedia
					provider_text = 'TELEMEDIA'#.upper()# telemedia
				if 'vip' == tele:
					provider_text = 'POWER VIP'
				if 'speedlink' == tele:
					provider_text = 'SPEEDLINK'
				if 'filestream' == tele:
					provider_text = 'FILE STREAM'
				extra_info = '[B]%s[/B] | [B]%s[/B] | %s' %  (item['quality'], item['size_label'], item['extraInfo'])
				display_name = item['display_name'].upper()
				resolve_item['resolve_display'] = '%s[CR]%s[CR]%s' % ('%02d. [B]%s[/B]' % (count, provider_text), extra_info, display_name)
				processed_items_append(resolve_item)
				if provider == 'easynews' and self.monitor_playback and self.easynews_max_retries:
					for retry in range(1, self.easynews_max_retries + 1):
						resolve_item = dict(item)
						resolve_item['resolve_display'] = '%s[CR]%s[CR]%s' % ('%02d. [B]%s (RETRYx%s)[/B]' % (count, provider_text, retry), extra_info, display_name)
						processed_items_append(resolve_item)
			items = list(processed_items)
			if not self.continue_resolve_check(): return self._kill_progress_dialog()
			hide_busy_dialog()
			if 'telemedia' == tele:
				self.playback_percent =''
			else:
				self.playback_percent = self.get_playback_percent()

			if self.playback_percent == None: return self._kill_progress_dialog()
			if not self.resolve_dialog_made: self._make_resolve_dialog()
			if self.background: sleep(1000)
			monitor = kodi_utils.monitor
			url = None
			for count, item in enumerate(items, 1):
				try:
					hide_busy_dialog()
					if not self.progress_dialog: break
					self.progress_dialog.reset_is_cancelled()
					self.progress_dialog.update_resolver(text=item['resolve_display'])
					self.progress_dialog.busy_spinner()
					if count > 1:
						sleep(self.playback_attempt_pause)
						try: del player
						except: pass
					player = FenPlayer()
					url, self.playback_successful, self.cancel_all_playback = None, None, False
					self.playing_filename = item['name']
					try:
						if self.progress_dialog.iscanceled() or monitor.abortRequested(): break # telemedia
						url = self.resolve_sources(item, self.meta)#telemedia
						if url:
							if not self.monitor_playback:
								self._kill_progress_dialog()
								sleep(100)
								close_all_dialog()
								return player.run(url, self,link_name=item['display_name'].upper())# telemedia
							resolve_percent = 0
							self.progress_dialog.busy_spinner('false')
							self.progress_dialog.update_resolver(percent=resolve_percent)
							sleep(200)
							player.run(url, self,link_name=item['display_name'].upper())# telemedia
						if self.cancel_all_playback: break
						if self.playback_successful: break
						if count == len(items):
							self.cancel_all_playback = True
							player.stop()
							break
					except: pass
				except: pass
		except: self._kill_progress_dialog()
		if self.cancel_all_playback: return self._kill_progress_dialog()
		if not self.playback_successful or not url: self.playback_failed_action()
		try: del monitor
		except: pass

	def get_playback_percent(self):
		global stop # telemedia
		if self.media_type == 'episode' and any((self.random, self.random_continual)): return 0.0
		percent = get_progress_percent(get_bookmarks(settings.watched_indicators(), self.media_type), self.tmdb_id, self.season, self.episode)
		if not percent: return 0.0
		action = self.get_resume_status(percent)
		if action == 'cancel':
			stop=True # telemedia
			return None
		if action == 'start_over':
			erase_bookmark(self.media_type, self.tmdb_id, self.season, self.episode)
			return 0.0
		return float(percent)

	def get_resume_status(self, percent):
		if settings.auto_resume(self.media_type): return float(percent)
		return self._make_resume_dialog(percent)

	def playback_failed_action(self):
		self._kill_progress_dialog()
		if self.prescrape and self.autoplay:
			self.resolve_dialog_made, self.prescrape, self.prescrape_sources = False, False, []
			self.get_sources()

	def continue_resolve_check(self):
		try:
			if not self.background or self.autoscrape_nextep: return True
			if self.autoplay_nextep: return self.autoplay_nextep_handler()
			return self.random_continual_handler()
		except: return False

	def random_continual_handler(self):
		notification('%s %s S%02dE%02d' % (ls(32801), self.meta.get('title'), self.meta.get('season'), self.meta.get('episode')), 6500, self.meta.get('poster'))
		player = xbmc_player()
		while player.isPlayingVideo(): sleep(100)
		self._make_resolve_dialog()
		return True

	def autoplay_nextep_handler(self):
		if not self.nextep_settings: return False
		player = xbmc_player()
		if player.isPlayingVideo():
			total_time = player.getTotalTime()
			use_window, window_time, default_action = self.nextep_settings['use_window'], self.nextep_settings['window_time'], self.nextep_settings['default_action']
			action = None if use_window else 'close'
			continue_nextep = False
			while player.isPlayingVideo():
				try:
					remaining_time = round(total_time - player.getTime())
					if remaining_time <= window_time:
						continue_nextep = True
						break
					sleep(100)
				except: pass
			if continue_nextep:
				if use_window: action = self._make_nextep_dialog(default_action=default_action)
				else: notification('%s %s S%02dE%02d' % (ls(32801), self.meta.get('title'), self.meta.get('season'), self.meta.get('episode')), 6500, self.meta.get('poster'))
				if not action: action = default_action
				if action == 'cancel': return False
				elif action == 'pause':
					player.stop()
					return False
				elif action == 'play':
					# self._make_resolve_dialog()#בוטל, גרם לקודי לקרוס במעבר לפרק הבא במקורות של טלמדיה
					player.stop()
					return True
				else:
					while player.isPlayingVideo(): sleep(100)
					self._make_resolve_dialog()
					return True
			else: return False
		else: return False

	def autoscrape_nextep_handler(self):
		default_action = 'cancel'
		player = xbmc_player()
		if player.isPlayingVideo():
			action = self._make_nextep_dialog(play_type=self.play_type, focus_button=12)
			if action == 'cancel': return
			else:
				results = self.get_sources()
				if not results: return notification(33092, 3000)
				if action == 'play': player.stop()
				else:
					notification(33091, 3000)
					while player.isPlayingVideo(): sleep(100)
				self.display_results(results)
		else: return
	def is_hebrew(self,input_str):   
		subti=['hebsub','hesub']

		if 'ללא.תרגום' in input_str:
			return False
		for i in subti:
			if i in input_str:
				return True
		try:
			import unicodedata
			input_str=input_str.replace(' ','').replace('\n','').replace('\r','').replace('\t','').replace(' ','')
			nfkd_form = unicodedata.normalize('NFKD', input_str.replace(' ','').replace('\n','').replace('\r','').replace('\t','').replace(' ',''))
			a=False
			for cha in input_str:
				a='HEBREW' in unicodedata.name(cha.strip())
				if a:
					break
			return a
		except:
			return True
	def get_telemedia(self,url,original_title,size,name,season,episode,resume,imdb_id,tmdb_id,iconimage, fanart,watched_indicators,plot,rating,genre,year,premiered,check_subs):
		import urllib.parse,xbmc
		global stop
		if stop==True:
			return
		if xbmc.Player().isPlaying():
			xbmc.Player().stop()
		que=urllib.parse.quote_plus
		url_id=json.loads(url.replace('%20',' '))['id']
		m_id=json.loads(url.replace('%20',' '))['m_id']
		c_id=json.loads(url.replace('%20',' '))['c_id']

		name= bytes(name, 'utf-8').decode('utf-8', 'ignore')
		watched_indicators='1'
		tag_line=check_subs
		if self.is_hebrew((check_subs)):
			check_subs='1'
		else:
			check_subs='0'
		url='plugin://plugin.video.telemedia/?url=%s&no_subs=%s&season=%s&episode=%s&mode=40&original_title=%s&id=%s&tmdb_id=%s&data=&fanart=&url=%s&iconimage=&file_name=%s&description=%s&resume=%s&name=%s&heb_name=%s&iconimage=%s&fanart=%s&watched_indicators=%s&c_id=%s&m_id=%s&plot=%s&rating=%s&genre=%s&year=%s&premiered=%s&tag_line=%s&kitana=true'%(url_id,check_subs,season,episode,que(original_title),imdb_id,tmdb_id,url_id,que(name),size,resume,que(original_title),que(name),iconimage, fanart,watched_indicators,c_id,m_id,que(plot),rating,que(genre),year,premiered,que(tag_line))

		return url.replace('\n','').replace('\r','').replace('\t','')
	def debrid_importer(self, debrid_provider):
		return manual_function_import(*debrids[debrid_provider])

	def resolve_sources(self, item, meta=None):
		if meta: self.meta = meta
		url = None
		try:
			x=item['provider']
			if 'telemedia' == x:
				import xbmc
				
				url2=item['url']
				# if 'google.com' in url2 or 'https://dood' in url2:
					# import sys,xbmcvfs
					# url=url.replace('https://dood.so','https://dood.to').replace('%20','')
					# path=xbmcvfs.translatePath('special://home/addons/script.module.resolveurl/lib')
					# sys.path.append( path)
					# path=xbmcvfs.translatePath('special://home/addons/script.module.six/lib')
					# sys.path.append( path)
					# path=xbmcvfs.translatePath('special://home/addons/script.module.kodi-six/libs')
					# sys.path.append( path)
					# import resolveurl
					# url =resolveurl .HostedMediaFile (url =url ).resolve ()

					# return url
				
				imdb_id=meta['imdb_id']

				tmdb_id=meta['tmdb_id']

				plot=meta['plot']
				rating=meta['rating']
				genre=meta['genre']
				year=meta['year']
				premiered=meta['premiered']
				iconimage=meta.get('poster')

				resume = self.get_playback_percent()#self.bookmarkEzra()
				fanart=meta.get('fanart')
				size=item['size_label']
				check_subs=item['name']
				watched_indicators = settings.watched_indicators()
				url=self.get_telemedia(url2,meta.get('original_title'),size,meta.get('title'),self.season, self.episode,resume,imdb_id,tmdb_id,iconimage, fanart,watched_indicators,plot,rating,genre,year,premiered,check_subs)
				return url
		except:pass
		try:
			if item['direct'] == 'elementum':
				import os,xbmcvfs,xbmcgui,sys
				if not os.path.exists(xbmcvfs.translatePath("special://home/addons/") + 'plugin.video.elementum'):
					DIALOG         = xbmcgui.Dialog()
					choice = DIALOG.yesno('Cobra', "יש להתקין את התוסף אלמנטום", yeslabel="[B][COLOR WHITE]התקן כעת[/COLOR][/B]", nolabel="[B][COLOR white]ביטול[/COLOR][/B]")
					if choice == 1:
						from modules import elementum
					else:
						self._kill_progress_dialog()
				filename = item['url']
				uri_string = filename
				url= 'plugin://plugin.video.elementum/play?uri=%s' % uri_string
				return url
		except:pass
		try:
			x=item['provider']
			if 'vip' == x:
				url = item['url']
				if 'google.com' in url or 'https://dood' in url:
					import sys,xbmcvfs
					url=url.replace('https://dood.so','https://dood.to').replace('%20','')
					path=xbmcvfs.translatePath('special://home/addons/script.module.resolveurl/lib')
					sys.path.append( path)
					path=xbmcvfs.translatePath('special://home/addons/script.module.six/lib')
					sys.path.append( path)
					path=xbmcvfs.translatePath('special://home/addons/script.module.kodi-six/libs')
					sys.path.append( path)
					import resolveurl
					url =resolveurl .HostedMediaFile (url =url ).resolve ()

				return url
			if 'speedlink' == x:
				return item['url']
			if 'filestream' == x:
				return item['url']
		except:pass
		try:
			if 'cache_provider' in item:
				cache_provider = item['cache_provider']
				if self.meta['media_type'] == 'episode':
					if hasattr(self, 'search_info'):
						title, season, episode, pack = self.search_info['title'], self.search_info['season'], self.search_info['episode'], 'package' in item
					else: title, season, episode, pack = self.get_ep_name(), self.get_season(), self.get_episode(), 'package' in item
				else: title, season, episode, pack = self.get_search_title(), None, None, False
				if cache_provider in debrid_providers: url = self.resolve_cached_torrents(cache_provider, item['url'], item['hash'], title, season, episode, pack)
			elif item.get('scrape_provider', None) in default_internal_scrapers:
				url = self.resolve_internal_sources(item['scrape_provider'], item['id'], item['url_dl'], item.get('direct_debrid_link', False))
			elif item.get('debrid') in debrid_providers and not item['source'].lower() == 'torrent': url = self.resolve_debrid(item['debrid'], item['provider'], item['url'])
			else: url = item['url']
		except: pass
		return url

	def resolve_cached_torrents(self, debrid_provider, item_url, _hash, title, season, episode, pack):
		url = None
		debrid_function = self.debrid_importer(debrid_provider)
		store_to_cloud = settings.store_resolved_torrent_to_cloud(debrid_provider, pack)
		try: url = debrid_function().resolve_magnet(item_url, _hash, store_to_cloud, title, season, episode)
		except: pass
		return url

	def resolve_uncached_torrents(self, debrid_provider, item_url, pack):
		if not confirm_dialog(text=ls(32831) % debrid_provider.upper()): return None
		debrid_function = self.debrid_importer(debrid_provider)
		try: debrid_function().add_uncached_torrent(item_url, pack)
		except: return notification(32490, 3500)

	def resolve_debrid(self, debrid_provider, item_provider, item_url):
		url = None
		debrid_function = self.debrid_importer(debrid_provider)
		try: url = debrid_function().unrestrict_link(item_url)
		except: pass
		return url

	def resolve_internal_sources(self, scrape_provider, item_id, url_dl, direct_debrid_link=False):
		url = None
		try:
			if direct_debrid_link or scrape_provider == 'folders': url = url_dl
			elif scrape_provider == 'furk':
				from indexers.furk import resolve_furk
				url = resolve_furk(item_id, self.meta['media_type'], self.meta['season'], self.meta['episode'])
			elif scrape_provider == 'easynews':
				from indexers.easynews import resolve_easynews
				url = resolve_easynews({'url_dl': url_dl, 'play': 'false'})
			else:
				debrid_function = self.debrid_importer(scrape_provider)
				if any(i in scrape_provider for i in ('rd_', 'ad_')):
					url = debrid_function().unrestrict_link(item_id)
				else:
					if '_cloud' in scrape_provider: item_id = debrid_function().get_item_details(item_id)['link']
					url = debrid_function().add_headers_to_url(item_id)
		except: pass
		return url

	def _quality_length(self, items, quality):
		return len([i for i in items if i['quality'] == quality])

	def _quality_length_sd(self, items, dummy):
		return len([i for i in items if i['quality'] in sd_check])

	def quality_length_final(self, items, dummy):
		return len(items)
