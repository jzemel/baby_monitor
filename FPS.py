import datetime

class FPS_tracker: 
	def __init__(self):
		self.frame_count = 0
		self.frame_start = None
  
	def getFPS(self):
		if self.frame_start is None:
			return None
		else:
			return round(self.frame_count / ((datetime.datetime.now() - self.frame_start).total_seconds()),2)