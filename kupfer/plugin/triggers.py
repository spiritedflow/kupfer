__kupfer_name__ = _("Triggers")
__kupfer_sources__ = ("Triggers", )
__kupfer_actions__ = (
	"AddTrigger",
)
__description__ = _("Assign global keybindings (triggers) to objects created "
                    "with 'Compose Command' (Ctrl+Return).")
__version__ = "2009-12-30"
__author__ = "Ulrik Sverdrup <ulrik.sverdrup@gmail.com>"

import gtk
import glib

from kupfer.obj.base import Action, Source, TextSource
from kupfer.obj.objects import TextLeaf, RunnableLeaf
from kupfer.obj.compose import ComposedLeaf
from kupfer import puid
from kupfer import kupferstring
from kupfer import task

from kupfer.ui import keybindings
from kupfer.ui import getkey_dialog


# we import the keybinder module for its side-effects --
# this plugin needs this module, lest it shall not function.
import keybinder

class Trigger (RunnableLeaf):
	def get_actions(self):
		for act in RunnableLeaf.get_actions(self):
			yield act
		yield RemoveTrigger()
	def run(self):
		return Triggers.perform_trigger(self.object)
	def repr_key(self):
		return self.object

class Triggers (Source):
	instance = None

	def __init__(self):
		Source.__init__(self, _("Triggers"))
		self.trigger_table = {}

	def config_save(self):
		return {"triggers": self.trigger_table, "version": self.version}

	def config_save_name(self):
		return __name__

	def config_restore(self, state):
		self.trigger_table = state["triggers"]
		return True
	
	def initialize(self):
		Triggers.instance = self
		keybindings.GetKeyboundObject().connect("keybinding", self._callback)
		for target, (keystr, name, id_) in self.trigger_table.iteritems():
			keybindings.bind_key(keystr, target)
		self.output_debug("Loaded triggers, count:", len(self.trigger_table))

	def finalize(self):
		for target, (keystr, name, id_) in self.trigger_table.iteritems():
			keybindings.bind_key(None, target)

	def _callback(self, keyobj, target, event_time):
		self.perform_trigger(target)

	def get_items(self):
		for target, (keystr, name, id_) in self.trigger_table.iteritems():
			label = gtk.accelerator_get_label(*gtk.accelerator_parse(keystr))
			yield Trigger(target, u"%s (%s)" % (label or keystr, name))

	def should_sort_lexically(self):
		return True

	def provides(self):
		yield Trigger

	@classmethod
	def perform_trigger(cls, target):
		try:
			keystr, name, id_ = cls.instance.trigger_table[target]
		except KeyError:
			return
		obj = puid.resolve_unique_id(id_)
		if obj is None:
			return
		return obj.run()

	@classmethod
	def add_trigger(cls, leaf, keystr):
		Triggers.instance._add_trigger(leaf, keystr)

	@classmethod
	def remove_trigger(cls, target):
		Triggers.instance._remove_trigger(target)
	
	def _add_trigger(self, leaf, keystr):
		for target in xrange(*keybindings.KEYRANGE_TRIGGERS):
			if target not in self.trigger_table:
				break
		keybindings.bind_key(keystr, target)
		name = unicode(leaf)
		self.trigger_table[target] = (keystr, name, puid.get_unique_id(leaf))
		self.mark_for_update()

	def _remove_trigger(self, target):
		self.trigger_table.pop(target, None)
		keybindings.bind_key(None, target)
		self.mark_for_update()

	def get_icon_name(self):
		return "key_bindings"

def try_bind_key(keystr):
	label = gtk.accelerator_get_label(*gtk.accelerator_parse(keystr))
	ulabel = kupferstring.tounicode(label)
	if len(ulabel) == 1 and ulabel.isalnum():
		return False
	target = keybindings.KEYRANGE_TRIGGERS[-1] - 1
	succ = keybindings.bind_key(keystr, target)
	if succ:
		keybindings.bind_key(None, target)
	return succ

class BindTask (task.Task):
	def __init__(self, leaf):
		self.leaf = leaf

	def start(self, finish_callback):
		glib.idle_add(self.ask_key, finish_callback)

	def ask_key(self, finish_callback):
		keystr = getkey_dialog.ask_for_key(try_bind_key)
		if keystr:
			Triggers.add_trigger(self.leaf, keystr)
		finish_callback(self)

class AddTrigger (Action):
	def __init__(self):
		Action.__init__(self, _("Add Trigger..."))
	
	def is_async(self):
		return True

	def activate(self, leaf):
		return BindTask(leaf)

	def item_types(self):
		yield ComposedLeaf

	def get_icon_name(self):
		return "list-add"

class RemoveTrigger (Action):
	def __init__(self):
		Action.__init__(self, _("Remove Trigger"))

	def activate(self, leaf):
		Triggers.remove_trigger(leaf.object)

	def get_icon_name(self):
		return "list-remove"

