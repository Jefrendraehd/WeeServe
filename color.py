
import weechat

class color:
	@staticmethod
	def title(a_string):
		return weechat.color("lred") + a_string + weechat.color("chat")
	@staticmethod
	def label(a_string):
		return weechat.color("green") + a_string + weechat.color("chat")
	@staticmethod
	def value(a_string):
		return weechat.color("cyan") + a_string + weechat.color("chat")
	@staticmethod
	def alert(a_string):
		return weechat.color("yellow") + a_string + weechat.color("chat")

	@staticmethod
	def green(a_string, bg_color=None):
		if bg_color:
			return weechat.color("green,"+bg_color) + a_string + weechat.color("chat")
		else:
			return weechat.color("green") + a_string + weechat.color("chat")

	@staticmethod
	def lgreen(a_string, bg_color=None):
		if bg_color:
			return weechat.color("lightgreen,"+bg_color) + a_string + weechat.color("chat")
		else:
			return weechat.color("lightgreen") + a_string + weechat.color("chat")

	@staticmethod
	def blue(a_string, bg_color=None):
		if bg_color:
			return weechat.color("blue,"+bg_color) + a_string + weechat.color("chat")
		else:
			return weechat.color("blue") + a_string + weechat.color("chat")

	@staticmethod
	def lblue(a_string, bg_color=None):
		if bg_color:
			return weechat.color("lightblue,"+bg_color) + a_string + weechat.color("chat")
		else:
			return weechat.color("lightblue") + a_string + weechat.color("chat")

	@staticmethod
	def cyan(a_string, bg_color=None):
		if bg_color:
			return weechat.color("cyan,"+bg_color) + a_string + weechat.color("chat")
		else:
			return weechat.color("cyan") + a_string + weechat.color("chat")

	@staticmethod
	def lcyan(a_string, bg_color=None):
		if bg_color:
			return weechat.color("lightcyan,"+bg_color) + a_string + weechat.color("chat")
		else:
			return weechat.color("lightcyan") + a_string + weechat.color("chat")

	@staticmethod
	def yellow(a_string, bg_color=None):
		if bg_color:
			return weechat.color("yellow,"+bg_color) + a_string + weechat.color("chat")
		else:
			return weechat.color("yellow") + a_string + weechat.color("chat")

	@staticmethod
	def magenta(a_string, bg_color=None):
		if bg_color:
			return weechat.color("magenta,"+bg_color) + a_string + weechat.color("chat")
		else:
			return weechat.color("magenta") + a_string + weechat.color("chat")

	@staticmethod
	def lmagenta(a_string, bg_color=None):
		if bg_color:
			return weechat.color("lmagenta,"+bg_color) + a_string + weechat.color("chat")
		else:
			return weechat.color("lmagenta") + a_string + weechat.color("chat")

	@staticmethod
	def white(a_string, bg_color=None):
		if bg_color:
			return weechat.color("white,"+bg_color) + a_string + weechat.color("chat")
		else:
			return weechat.color("white") + a_string + weechat.color("chat")

	@staticmethod
	def brown(a_string, bg_color=None):
		if bg_color:
			return weechat.color("brown,"+bg_color) + a_string + weechat.color("chat")
		else:
			return weechat.color("brown") + a_string + weechat.color("chat")

	@staticmethod
	def red(a_string, bg_color=None):
		if bg_color:
			return weechat.color("red,"+bg_color) + a_string + weechat.color("chat")
		else:
			return weechat.color("red") + a_string + weechat.color("chat")

	@staticmethod
	def lred(a_string, bg_color=None):
		if bg_color:
			return weechat.color("lightred,"+bg_color) + a_string + weechat.color("chat")
		else:
			return weechat.color("lightred") + a_string + weechat.color("chat")

