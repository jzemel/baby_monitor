class FPS_tracker: 
	def __init__(self):
		self.frame_count = 0
		self.frame_start = None
  
	def getFPS(self):
		if self.frame_start is None:
			return None
		else:
			return round(FPS.frame_count / ((datetime.datetime.now() - FPS.frame_start).total_seconds()),1)