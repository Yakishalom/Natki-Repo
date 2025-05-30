# -*- coding: utf-8 -*-
import time
from windows.base_window import BaseDialog
from modules.settings import get_art_provider, avoid_episode_spoilers
# from modules.kodi_utils import notification# telemedia

# from modules.kodi_utils import logger

pause_time_before_end, hold_pause_time = 10, 900
button_actions = {'autoplay_nextep': {10: 'play', 11: 'show_sources', 12: 'cancel'}, 'autoscrape_nextep': {10: 'play', 11: 'close', 12: 'cancel'}}# telemedia
# button_actions = {'autoplay_nextep': {10: 'play', 11: 'close', 12: 'cancel'}, 'autoscrape_nextep': {10: 'play', 11: 'close', 12: 'cancel'}}# cobra original
class NextEpisode(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, *args)
		self.closed = False
		self.meta = kwargs.get('meta')
		self.selected = kwargs.get('default_action', 'cancel')

		self.play_type = kwargs.get('play_type', 'autoplay_nextep')
		self.focus_button = kwargs.get('focus_button', 10)
		self.poster_main, self.poster_backup, self.fanart_main, self.fanart_backup, self.clearlogo_main, self.clearlogo_backup = get_art_provider()
		self.set_properties()

	def onInit(self):
		# self.setFocusId(self.focus_button)# cobra original
		self.setFocusId(10)# telemedia
		self.monitor()

	def run(self):
		self.doModal()
		self.clearProperties()
		self.clear_modals()
		if self.selected == 'show_sources':# telemedia
			import xbmc
			url='plugin://plugin.video.cobra/?mode=playback.media&media_type=episode&tmdb_id={0}&season={1}&episode={2}'.format(self.meta['tmdb_id'],self.meta['season'],self.meta['episode'])
			xbmc.executebuiltin('RunPlugin(%s)'%url)
			return 'cancel'
		else:
			return self.selected
	def onAction(self, action):
		if action in self.closing_actions:
			#self.selected = 'close' # cobra original
			self.selected = 'cancel' # telemedia # לא מנגן את הפרק הבא כאשר סוגרים את החלון פרק הבא
			self.closed = True
			self.close()

	def onClick(self, controlID):
		self.selected = button_actions[self.play_type][controlID]
		self.closed = True
		self.close()

	def set_properties(self):
		self.setProperty('play_type', self.play_type)
		self.setProperty('title', self.meta['title'])
		self.setProperty('thumb', self.get_thumb())
		self.setProperty('clearlogo', self.original_clearlogo())
		self.setProperty('next_ep_title', self.meta['title'])
		self.setProperty('next_ep_season', '%02d' % self.meta['season'])
		self.setProperty('next_ep_episode', '%02d' % self.meta['episode'])
		self.setProperty('next_ep_ep_name', self.meta['ep_name'])

	def get_thumb(self):
		if avoid_episode_spoilers(): thumb = self.original_fanart()
		else: thumb = self.meta.get('ep_thumb', None) or self.original_fanart()
		return thumb

	def original_fanart(self):
		return self.meta.get('custom_fanart') or self.meta.get(self.fanart_main) or self.meta.get(self.fanart_backup) or ''

	def original_clearlogo(self):
		return self.meta.get('custom_clearlogo') or self.meta.get(self.clearlogo_main) or self.meta.get(self.clearlogo_backup) or ''

	def monitor(self):
		try: progress_bar = self.get_control(5000)# telemedia
		except: progress_bar = None# telemedia
		total_time = self.player.getTotalTime()
		total_remaining = total_time - self.player.getTime() # telemedia
		while self.player.isPlaying():
			remaining_time = round(total_time - self.player.getTime())
			current_point = (remaining_time / float(total_remaining)) * 100# telemedia
			# if self.play_type == 'autoscrape_nextep' and self.selected == 'play':
				# notification('מחפש מקורות לפרק הבא, המתן...')
			if progress_bar: progress_bar.setPercent(current_point)# telemedia
			if self.closed: break 
			elif self.play_type == 'autoplay_nextep' and self.selected == 'pause' and remaining_time <= pause_time_before_end:
				self.player.pause()
				self.sleep(500)
				break
			self.sleep(1000)
		if self.selected == 'pause':
			start_time = time.time()
			end_time = start_time + hold_pause_time
			current_time = start_time
			while current_time <= end_time and self.selected == 'pause':
				try:
					current_time = time.time()
					pause_timer = time.strftime('%M:%S', time.gmtime(max(end_time - current_time, 0)))
					self.setProperty('pause_timer', pause_timer)
					self.sleep(1000)
				except: break
			if self.selected != 'cancel': self.player.pause()
		self.close()
