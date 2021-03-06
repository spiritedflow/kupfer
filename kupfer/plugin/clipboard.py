__kupfer_name__ = _("Clipboards")
__kupfer_sources__ = ("ClipboardSource", )
__kupfer_actions__ = ("ClearClipboards", )
__description__ = _("Recent clipboards")
__version__ = ""
__author__ = "Ulrik Sverdrup <ulrik.sverdrup@gmail.com>"

from collections import deque

import gtk

from kupfer.objects import Source, TextLeaf, Action, SourceLeaf
from kupfer import plugin_support
from kupfer.weaklib import gobject_connect_weakly


__kupfer_settings__ = plugin_support.PluginSettings(
	{
		"key" : "max",
		"label": _("Number of recent clipboards"),
		"type": int,
		"value": 10,
	},
	{
		"key" : "use_selection",
		"label": _("Include recent selections"),
		"type": bool,
		"value": False,
	},
	{
		"key" : "sync_selection",
		"label": _("Copy selection to primary clipboard"),
		"type": bool,
		"value": False,
	},
)

class ClipboardText (TextLeaf):
	def get_description(self):
		lines = self.object.splitlines()
		desc = unicode(self)
		numlines = len(lines) or 1

		return ngettext('Clipboard "%(desc)s"',
			'Clipboard with %(num)d lines "%(desc)s"',
			numlines) % {"num": numlines, "desc": desc }


class ClearClipboards(Action):
	def __init__(self):
		Action.__init__(self, _("Clear"))

	def activate(self, leaf):
		leaf.object.clear()

	def item_types(self):
		yield SourceLeaf

	def valid_for_item(self, leaf):
		return isinstance(leaf.object, ClipboardSource)

	def get_description(self):
		return _("Remove all recent clipboards")

	def get_icon_name(self):
		return "edit-clear"


class ClipboardSource (Source):
	def __init__(self):
		Source.__init__(self, _("Clipboards"))
		self.clipboards = deque()

	def initialize(self):
		clip = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
		gobject_connect_weakly(clip, "owner-change", self._clipboard_changed)
		clip = gtk.clipboard_get(gtk.gdk.SELECTION_PRIMARY)
		gobject_connect_weakly(clip, "owner-change", self._clipboard_changed)

	def _clipboard_changed(self, clip, event, *args):
		is_selection = (event.selection == gtk.gdk.SELECTION_PRIMARY)
		if is_selection and not __kupfer_settings__["use_selection"]:
			return

		max_len = __kupfer_settings__["max"]
		newtext = clip.wait_for_text()
		if not (newtext and newtext.strip()):
			return

		if newtext in self.clipboards:
			self.clipboards.remove(newtext)
		# if the previous text is a prefix of the new selection, supercede it
		if (is_selection and self.clipboards
				and (newtext.startswith(self.clipboards[-1])
				or newtext.endswith(self.clipboards[-1]))):
			self.clipboards.pop()
		self.clipboards.append(newtext)

		if is_selection and __kupfer_settings__["sync_selection"]:
			gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD).set_text(newtext)

		while len(self.clipboards) > max_len:
			self.clipboards.popleft()
		self.mark_for_update()

	def get_items(self):
		for t in reversed(self.clipboards):
			yield ClipboardText(t)

	def get_description(self):
		return _("Recent clipboards")

	def get_icon_name(self):
		return "gtk-paste"

	def provides(self):
		yield TextLeaf

	def clear(self):
		self.clipboards.clear()
		self.mark_for_update()
