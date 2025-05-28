# -*- coding: utf-8 -*-
from modules import service_functions
from modules.kodi_utils import Thread, xbmc_monitor, logger, local_string as ls

fen_str = ls(32036).upper()
on_notification_actions = service_functions.OnNotificationActions()
on_settings_changed_actions = service_functions.OnSettingsChangedActions()

class FenMonitor(xbmc_monitor):
	def __init__ (self):
		xbmc_monitor.__init__(self)
		self.startUpServices()

	def startUpServices(self):
		try: service_functions.InitializeDatabases().run()
		except: pass
		try: service_functions.CheckSettings().run()
		except: pass
		# try: service_functions.FirstRunActions().run() # telemedia
		# except: pass
		# try: service_functions.ReuseLanguageInvokerCheck().run()  # telemedia
		# except: pass
		Thread(target=service_functions.TraktMonitor().run).start()
		Thread(target=service_functions.CustomActions().run).start()
		# Thread(target=service_functions.CustomFonts().run).start() # telemedia
		# Thread(target=service_functions.PremiumExpiryCheck().run).start()
		try:
			from indexers import real_debrid
			Thread(target=real_debrid.active_days_notify_only()).start()
		except:
			pass
		try: service_functions.ClearSubs().run()
		except: pass
		# try: service_functions.AutoRun().run() # telemedia
		# except: pass
		Thread(target=service_functions.DatabaseMaintenance().run).start()

	def onSettingsChanged(self):
		on_settings_changed_actions.run()

	def onNotification(self, sender, method, data):
		on_notification_actions.run(sender, method, data)

logger(fen_str, 'Main Monitor Service Starting')
logger(fen_str, 'Settings Monitor Service Starting')
FenMonitor().waitForAbort()
logger(fen_str, 'Settings Monitor Service Finished')
logger(fen_str, 'Main Monitor Service Finished')