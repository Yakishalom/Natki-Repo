# -*- coding: utf-8 -*-
from modules import kodi_utils
# logger = kodi_utils.logger

translate_path, get_property, tmdb_default_api, fanarttv_default_api = kodi_utils.translate_path, kodi_utils.get_property, kodi_utils.tmdb_default_api, kodi_utils.fanarttv_default_api
get_setting, current_skin, path_exists, custom_xml_path = kodi_utils.get_setting, kodi_utils.current_skin, kodi_utils.path_exists, kodi_utils.custom_xml_path
custom_skin_path, addon_path = kodi_utils.custom_skin_path, kodi_utils.addon_path
download_directories_dict = {'telemedia': 'cobra.telemedia_download_directory','movie': 'cobra.movie_download_directory', 'episode': 'cobra.tvshow_download_directory', 'thumb_url': 'cobra.image_download_directory',
							'image_url': 'cobra.image_download_directory','image': 'cobra.image_download_directory', 'premium': 'cobra.premium_download_directory',
							None: 'cobra.premium_download_directory', 'None': False}# telemedia
results_style_dict = {'true': 'contrast', 'false': 'non_contrast'}
results_window_numbers_dict = {'list': 2000, 'infolist': 2001, 'medialist': 2002, 'rows': 2003, 'widelist': 2004}
year_in_title_dict = {'movie': (1, 3), 'tvshow': (2, 3)}
default_action_dict = {'0': 'play', '1': 'cancel', '2': 'pause'}
extras_open_action_dict = {'movie': (1, 3), 'tvshow': (2, 3)}
paginate_dict = {True: 'cobra.paginate.limit_widgets', False: 'cobra.paginate.limit_addon'}
prescrape_scrapers_tuple = ('furk', 'easynews', 'rd_cloud', 'pm_cloud', 'ad_cloud', 'folders')
sort_to_top_dict = {'folders': 'cobra.results.sort_folders_first', 'rd_cloud': 'cobra.results.sort_rdcloud_first',
					'pm_cloud': 'cobra.results.sort_pmcloud_first', 'ad_cloud': 'cobra.results.sort_adcloud_first'}
internal_scrapers_clouds_list = [('rd', 'provider.rd_cloud'), ('pm', 'provider.pm_cloud'), ('ad', 'provider.ad_cloud')]
single_ep_format_dict = {'0': '%d-%m-%Y', '1': '%Y-%m-%d', '2': '%m-%d-%Y'}
default_art_provider_tuple = ('poster', 'poster2', 'fanart', 'fanart2', 'clearlogo', 'clearlogo2')
art_provider_dict = {True: ('poster2', 'poster', 'fanart2', 'fanart', 'clearlogo2', 'clearlogo'), False: ('poster', 'poster2', 'fanart', 'fanart2', 'clearlogo2', 'clearlogo')}
resolution_tuple = ({'poster': 'w185', 'fanart': 'w300', 'still': 'w185', 'profile': 'w185', 'clearlogo': 'original'},
					{'poster': 'w342', 'fanart': 'w780', 'still': 'w300', 'profile': 'w342', 'clearlogo': 'original'},
					{'poster': 'w780', 'fanart': 'w1280', 'still': 'original', 'profile': 'h632', 'clearlogo': 'original'},
					{'poster': 'original', 'fanart': 'original', 'still': 'original', 'profile': 'original', 'clearlogo': 'original'})

def generic_list_sorting(setting_id):
	return get_setting('cobra.sort.%s' % setting_id, 'popularity.desc').replace('&amp;', '&')

def skin_location(skin_xml):
	user_skin = current_skin()
	if not use_custom_skins(): return addon_path
	if path_exists(custom_xml_path % (user_skin, skin_xml)): return kodi_utils.path_join(custom_skin_path, user_skin)
	return addon_path

def use_skin_fonts():
	return get_setting('cobra.use_skin_fonts')

def use_custom_skins():
	return get_setting('cobra.use_custom_skins', 'true') == 'true'

def results_format():
	return str(get_setting('cobra.results.list_format', 'List').lower())

def results_style():
	return results_style_dict[get_setting('cobra.results.use_contrast', 'true')]

def results_xml_window_number(window_format=None):
	if not window_format: window_format = results_format()
	return results_window_numbers_dict.get(window_format.split(' ')[0], 2000)

def store_resolved_torrent_to_cloud(debrid_service, pack):
	setting_value = int(get_setting('cobra.store_resolved_torrent.%s' % debrid_service.lower(), '0'))
	return setting_value in (1, 2) if pack else setting_value == 1

def enabled_debrids_check(debrid_service):
	if not get_setting('cobra.%s.enabled' % debrid_service) == 'true': return False
	return authorized_debrid_check(debrid_service)

def authorized_debrid_check(debrid_service):
	if get_setting('cobra.%s.token' % debrid_service) in (None, ''): return False
	return True

def check_premium_account_status():
	return get_setting('cobra.check_premium_account_status', 'false') == 'true'

def playback_settings():
	return (int(get_setting('cobra.playback.watched_percent', '90')), int(get_setting('cobra.playback.resume_percent', '5')))

def monitor_playback():
	return get_setting('cobra.playback.monitor_success2', 'true') == 'true'

def playback_attempt_pause():
	return int(get_setting('cobra.playback.pause_start', '1500'))

def limit_resolve():
	return get_setting('cobra.playback.limit_resolve', 'false') == 'true'

def disable_content_lookup():
	return get_setting('cobra.playback.disable_content_lookup') == 'true'

def easynews_max_retries():
	return int(get_setting('cobra.playback.easynews_max_retries', '1'))

def show_unaired_watchlist():
	return get_setting('cobra.show_unaired_watchlist', 'false') == 'true'
	
def movies_directory():
	return translate_path(get_setting('cobra.movies_directory'))
	
def tv_show_directory():
	return translate_path(get_setting('cobra.tv_shows_directory'))

def download_directory(media_type):
	return translate_path(get_setting(download_directories_dict[media_type]))

def source_folders_directory(media_type, source):
	setting = 'cobra.%s.movies_directory' % source if media_type == 'movie' else 'cobra.%s.tv_shows_directory' % source
	if get_setting(setting) not in ('', 'None', None): return translate_path( get_setting(setting))
	else: return False

def avoid_episode_spoilers():
	return get_setting('cobra.avoid_episode_spoilers', 'false') == 'true'

def paginate(is_home):
	paginate_lists = int(get_setting('cobra.paginate.lists', '0'))
	if is_home: return paginate_lists in (2, 3)
	else: return paginate_lists in (1, 3)

def page_limit(is_home):	
	return int(get_setting(paginate_dict[is_home], '20'))

def jump_to_enabled():
	return int(get_setting('cobra.paginate.jump_to', '0'))

def use_year_in_search():
	return get_setting('cobra.meta_use_year_in_search') == 'true'

def quality_filter(setting):
	return get_setting('cobra.%s' % setting).split(', ')

def audio_filters():
	setting = get_setting('cobra.filter_audio')
	if setting in ('', None): return []
	return setting.split(', ')

def include_prerelease_results():
	return get_setting('cobra.include_prerelease_results', 'true') == 'true'

def auto_play(media_type):
	return get_setting('cobra.auto_play_%s' % media_type, 'false') == 'true'

def autoplay_next_episode():
	if auto_play('episode') and get_setting('cobra.autoplay_next_episode', 'false') == 'true': return True
	else: return False

def autoscrape_next_episode():
	if not auto_play('episode') and get_setting('cobra.autoscrape_next_episode', 'false') == 'true': return True
	else: return False

def auto_rescrape_with_all():
	return get_setting('cobra.results.autorescrape_with_all', 'false') == 'true'

def auto_nextep_settings(play_type):
	play_type = 'autoplay' if play_type == 'autoplay_nextep' else 'autoscrape'
	window_percentage = 100 - int(get_setting('cobra.%s_next_window_percentage' % play_type, '95'))
	use_chapters = get_setting('cobra.%s_use_chapters' % play_type, 'true') == 'true'
	scraper_time = int(get_setting('cobra.results.timeout', '60')) + 20
	if play_type == 'autoplay':
		alert_method = int(get_setting('cobra.autoplay_alert_method', '0'))
		default_action = default_action_dict[get_setting('cobra.autoplay_default_action', '1')] if alert_method == 0 else 'cancel'
	else: alert_method, default_action = '', ''
	return {'scraper_time': scraper_time, 'window_percentage': window_percentage, 'alert_method': alert_method, 'default_action': default_action, 'use_chapters': use_chapters}

def filter_status(filter_type):
	return int(get_setting('cobra.filter_%s' % filter_type, '0'))

def ignore_results_filter():
	return int(get_setting('cobra.results.ignore_filter', '0'))

def display_uncached_torrents():
	return get_setting('cobra.torrent.display.uncached', 'false') == 'true'

def trakt_sync_interval():
	setting = get_setting('cobra.trakt.sync_interval', '25')
	interval = int(setting) * 60
	return setting, interval

def trakt_sync_refresh_widgets():
	return get_setting('cobra.trakt.sync_refresh_widgets', 'true') == 'true'

def lists_sort_order(setting):
	return int(get_setting('cobra.sort.%s' % setting, '0'))

def auto_start_fen():
	return get_setting('cobra.auto_start_fen', 'false') == 'true'

def furk_active():
	if get_setting('cobra.provider.furk', 'false') == 'true':
		if not get_setting('cobra.furk_api_key'):
			furk_status = False if '' in (get_setting('cobra.furk_login'), get_setting('cobra.furk_password')) else True
		else: furk_status = True
	else: furk_status = False
	return furk_status

def easynews_active():
	if get_setting('cobra.provider.easynews', 'false') == 'true':
		easynews_status = False if '' in (get_setting('cobra.easynews_user'), get_setting('cobra.easynews_password')) else True
	else: easynews_status = False
	return easynews_status

def tv_progress_location():
	return int(get_setting('cobra.tv_progress_location', '0'))

def extras_enable_extra_ratings():
	return get_setting('cobra.extras.enable_extra_ratings', 'true') == 'true'

def extras_enabled_ratings():
	return get_setting('cobra.extras.enabled_ratings', 'Meta, Tom/Critic, Tom/User, IMDb, TMDb').split(', ')

def extras_enable_scrollbars():
	return get_setting('cobra.extras.enable_scrollbars', 'true')

def extras_exclude_non_acting():
	return get_setting('cobra.extras.exclude_non_acting_roles', 'true') == 'true'

def extras_windowed_playback():
	return get_setting('cobra.extras.windowed_playback', 'false') == 'true'

def extras_enabled_menus():
	setting = get_setting('cobra.extras.enabled', '2000,2050,2051,2052,2053,2054,2055,2056,2057,2058,2059,2060,2061,2062,2063')
	if setting in ('', None, 'noop', []): return []
	return [int(i) for i in setting.split(',')]

def check_prescrape_sources(scraper, media_type):
	if scraper in prescrape_scrapers_tuple: return get_setting('cobra.check.%s' % scraper) == 'true'
	if get_setting('cobra.check.%s' % scraper) == 'true' and auto_play(media_type): return True
	else: return False

def external_scraper_info():
	module = get_setting('cobra.external_scraper.module', None)
	if module: return module, module.split('.')[-1]
	else: return None, ''

def filter_by_name(scraper):
	if get_property('fs_filterless_search') == 'true': return False
	return get_setting('cobra.%s.title_filter' % scraper, 'false') == 'true'

def easynews_language_filter():
	enabled = get_setting('cobra.easynews.filter_lang') == 'true'
	if enabled: filters = get_setting('cobra.easynews.lang_filters').split(', ')
	else: filters = []
	return enabled, filters

def results_sort_order():
	sort_direction = -1 if get_setting('results.size_sort_direction') == '0' else 1
    
	if get_setting('show_torrent') == 'true':# telemedia
		return (
				lambda k: (k['quality_rank'], k['provider_rank'], sort_direction*k['size']), #Quality, Provider, Size
				lambda k: (k['quality_rank'], sort_direction*k['seeders'], k['provider_rank']), #Quality, Size, Provider
				lambda k: (k['provider_rank'], k['quality_rank'], sort_direction*k['size']), #Provider, Quality, Size
				lambda k: (k['provider_rank'], sort_direction*k['size'], k['quality_rank']), #Provider, Size, Quality
				lambda k: (sort_direction*k['size'], k['quality_rank'], k['provider_rank']), #Size, Quality, Provider
				lambda k: (sort_direction*k['size'], k['provider_rank'], k['quality_rank'])  #Size, Provider, Quality
				)[int(get_setting('results.sort_order', '1'))]
	else:
		return (
				lambda k: (k['quality_rank'], k['provider_rank'], sort_direction*k['size']), #Quality, Provider, Size
				lambda k: (k['quality_rank'], sort_direction*k['size'], k['provider_rank']), #Quality, Size, Provider
				lambda k: (k['provider_rank'], k['quality_rank'], sort_direction*k['size']), #Provider, Quality, Size
				lambda k: (k['provider_rank'], sort_direction*k['size'], k['quality_rank']), #Provider, Size, Quality
				lambda k: (sort_direction*k['size'], k['quality_rank'], k['provider_rank']), #Size, Quality, Provider
				lambda k: (sort_direction*k['size'], k['provider_rank'], k['quality_rank'])  #Size, Provider, Quality
				)[int(get_setting('results.sort_order', '1'))]

def active_internal_scrapers():
	settings = ['provider.external', 'provider.furk', 'provider.easynews', 'provider.folders']
	settings_append = settings.append
	for item in internal_scrapers_clouds_list:
		if enabled_debrids_check(item[0]): settings_append(item[1])
	active = [i.split('.')[1] for i in settings if get_setting('cobra.%s' % i) == 'true']
	return active

def provider_sort_ranks():
	fu_priority = int(get_setting('cobra.fu.priority', '6'))
	en_priority = int(get_setting('cobra.en.priority', '7'))
	rd_priority = int(get_setting('cobra.rd.priority', '8'))
	ad_priority = int(get_setting('cobra.ad.priority', '9'))
	pm_priority = int(get_setting('cobra.pm.priority', '10'))
	return {'furk': fu_priority, 'easynews': en_priority, 'real-debrid': rd_priority, 'premiumize.me': pm_priority, 'alldebrid': ad_priority,
			'rd_cloud': rd_priority, 'pm_cloud': pm_priority, 'ad_cloud': ad_priority, 'folders': 0}

def sort_to_top(provider):
	return get_setting(sort_to_top_dict[provider]) == 'true'

def auto_resume(media_type):
	auto_resume = get_setting('cobra.auto_resume_%s' % media_type)
	if auto_resume == '1': return True
	if auto_resume == '2' and auto_play(media_type): return True
	else: return False

def scraping_settings():
	highlight_type = int(get_setting('cobra.highlight.type', '0'))
	if highlight_type == 3:
		highlight = get_setting('cobra.scraper_single_highlight', 'FF008EB2')
		return {'highlight_type': 2, '4k': highlight, '1080p': highlight, '720p': highlight, 'sd': highlight}
	hoster_highlight, torrent_highlight, furk_highlight, easynews_highlight, debrid_cloud_highlight, folders_highlight = '', '', '', '', '', ''
	rd_highlight, pm_highlight, ad_highlight, highlight_4K, highlight_1080P, highlight_720P, highlight_SD = '', '', '', '', '', '', ''
	if highlight_type in (0, 1):
		furk_highlight = get_setting('cobra.provider.furk_colour', 'FFE6002E')
		easynews_highlight = get_setting('cobra.provider.easynews_colour', 'FF00B3B2')
		debrid_cloud_highlight = get_setting('cobra.provider.debrid_cloud_colour', 'FF7A01CC')
		folders_highlight = get_setting('cobra.provider.folders_colour', 'FFB36B00')
		if highlight_type == 0:
			hoster_highlight = get_setting('cobra.hoster.identify', 'FF0166FF')
			torrent_highlight = get_setting('cobra.torrent.identify', 'FFFF00FE')
		else:
			rd_highlight = get_setting('cobra.provider.rd_colour', 'FF3C9900')
			pm_highlight = get_setting('cobra.provider.pm_colour', 'FFFF3300')
			ad_highlight = get_setting('cobra.provider.ad_colour', 'FFE6B800')
	elif highlight_type == 2:
		highlight_4K = get_setting('cobra.scraper_4k_highlight', 'FFFF00FE')
		highlight_1080P = get_setting('cobra.scraper_1080p_highlight', 'FFE6B800')
		highlight_720P = get_setting('cobra.scraper_720p_highlight', 'FF3C9900')
		highlight_SD = get_setting('cobra.scraper_SD_highlight', 'FF0166FF')
	return {'highlight_type': highlight_type, 'hoster_highlight': hoster_highlight, 'torrent_highlight': torrent_highlight,'real-debrid': rd_highlight, 'premiumize': pm_highlight,
			'alldebrid': ad_highlight, 'rd_cloud': debrid_cloud_highlight, 'pm_cloud': debrid_cloud_highlight, 'ad_cloud': debrid_cloud_highlight, 'furk': furk_highlight,
			'easynews': easynews_highlight, 'folders': folders_highlight, '4k': highlight_4K, '1080p': highlight_1080P, '720p': highlight_720P, 'sd': highlight_SD}

def get_art_provider():
	if not get_fanart_data(): return default_art_provider_tuple
	return art_provider_dict[fanarttv_default()]

def omdb_api_key():
	return get_setting('cobra.omdb_api', '')

def metadata_user_info():
	tmdb_api = tmdb_api_key()
	extra_fanart_enabled = get_fanart_data()
	image_resolution = get_resolution()
	meta_language = get_language()
	mpaa_region = get_mpaa_region()
	hide_watched = widget_hide_watched()
	if extra_fanart_enabled: fanart_client_key = fanarttv_client_key()
	else: fanart_client_key = ''
	return {'extra_fanart_enabled': extra_fanart_enabled, 'image_resolution': image_resolution , 'language': meta_language, 'mpaa_region': mpaa_region,
			'fanart_client_key': fanart_client_key, 'tmdb_api': tmdb_api, 'widget_hide_watched': hide_watched}

def default_all_episodes():
	return int(get_setting('cobra.default_all_episodes'))

def max_threads():
	if not get_setting('cobra.limit_concurrent_threads', 'false') == 'true': return 60
	return int(get_setting('cobra.max_threads', '60'))

def widget_hide_next_page():
	return get_setting('cobra.widget_hide_next_page', 'false') == 'true'

def show_unaired():
	return get_setting('cobra.show_unaired', 'true') == 'true'

def use_season_title():
	return get_setting('cobra.use_season_title', 'true') == 'true'

def show_specials():
	return get_setting('cobra.show_specials', 'false') == 'true'

def calendar_sort_order():
	return int(get_setting('cobra.trakt.calendar_sort_order', '0'))

def ignore_articles():
	return get_setting('cobra.ignore_articles', 'false') == 'true'

def date_offset():
	return int(get_setting('cobra.datetime.offset', '0')) + 5

def single_ep_display_title():
	return int(get_setting('cobra.single_ep_display', '0'))

def single_ep_format():
	return single_ep_format_dict[get_setting('cobra.single_ep_format', '1')]

def include_year_in_title(media_type):
	return int(get_setting('cobra.include_year_in_title', '0')) in year_in_title_dict[media_type]

def extras_open_action(media_type):
	return int(get_setting('cobra.extras.open_action', '0')) in extras_open_action_dict[media_type]

def tmdb_api_key():
	return get_setting('cobra.tmdb_api', tmdb_default_api)

def get_fanart_data():
	return get_setting('cobra.get_fanart_data') == 'true'

def get_resolution():
	return resolution_tuple[int(get_setting('cobra.image_resolutions', '2'))]

def get_language():
	return get_setting('cobra.meta_language', 'en')

def get_meta_filter():
	return get_setting('cobra.meta_filter', 'true')

def get_mpaa_region():
	return get_setting('cobra.meta_mpaa_region', 'US')

def widget_hide_watched():
	return get_setting('cobra.widget_hide_watched', 'false') == 'true'

def fanarttv_client_key():
	return get_setting('cobra.fanart_client_key', fanarttv_default_api)

def watched_indicators():
	if get_setting('cobra.trakt.user') == '': return 0
	return int(get_setting('cobra.watched_indicators', '0'))

def fanarttv_default():
	return get_setting('cobra.fanarttv.default', 'false') == 'true'

def nextep_display_settings():
	include_airdate = get_setting('cobra.nextep.include_airdate', 'false') == 'true'
	return {'unaired_color': 'red', 'unwatched_color': 'darkgoldenrod', 'include_airdate': include_airdate}

def nextep_content_settings():
	sort_type = int(get_setting('cobra.nextep.sort_type', '0'))
	sort_order = int(get_setting('cobra.nextep.sort_order', '0'))
	sort_direction = sort_order == 0
	sort_key = 'last_played' if sort_type == 0 else 'first_aired' if sort_type == 1 else 'name'
	include_unaired = get_setting('cobra.nextep.include_unaired', 'false') == 'true'
	include_unwatched = int(get_setting('cobra.nextep.include_unwatched', '0'))
	sort_airing_today_to_top = get_setting('cobra.nextep.sort_airing_today_to_top', 'false') == 'true'
	return {'sort_key': sort_key, 'sort_direction': sort_direction, 'sort_type': sort_type, 'sort_order':sort_order,
			'include_unaired': include_unaired, 'include_unwatched': include_unwatched, 'sort_airing_today_to_top': sort_airing_today_to_top}

def update_delay():
	return int(get_setting('fen.update.delay', '45'))

def update_action():
	return int(get_setting('fen.update.action', '2'))