# coding=utf-8
from common.strings import StaticAnswers

# XEP-0012: Last Activity


class LastActivity:
	"""
	query the server uptime of the specified domain, defined by XEP-0012
	"""
	def __init__(self, static_answers: StaticAnswers):
		# init all necessary variables
		self.last_activity = None
		self.target, self.opt_arg = None, None
		self.staticAnswers = static_answers

	def process(self, granularity=4):
		seconds = self.last_activity['last_activity']['seconds']
		uptime = []
		messages = self.staticAnswers.lang.command_messages

		# tuple with displayable time sections
		intervals = (
			('uptime.years', 31536000),  # 60 * 60 * 24 * 365
			('uptime.weeks', 604800),  # 60 * 60 * 24 * 7
			('uptime.days', 86400),  # 60 * 60 * 24
			('uptime.hours', 3600),  # 60 * 60
			('uptime.minutes', 60),
			('uptime.seconds', 1)
		)

		# for every element in possible time section process the seconds
		for name, count in intervals:
			value = seconds // count
			if value:
				seconds -= value * count
				if value == 1:
					name = name.rstrip('s')
				uptime.append("{} {}".format(value, messages[name]))
		result = ' '.join(uptime[:granularity])

		# insert values into result string
		return messages['uptime.running'] % (self.target, result)

	def format(self, queries, target, opt_arg):
		self.last_activity = queries['xep_0012']

		self.target = target
		self.opt_arg = opt_arg

		return self.process()
