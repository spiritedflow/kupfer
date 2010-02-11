from __future__ import absolute_import

__kupfer_name__ = _("Gwibber")
__kupfer_actions__ = (
		"SendUpdate",
	)
__description__ = _("Send updates via the microblogging client Gwibber")
__version__ = ""
__author__ = "US"

import dbus

from kupfer.objects import Action, TextLeaf
from kupfer import plugin_support
from kupfer import pretty

plugin_support.check_dbus_connection()

def _get_interface(activate=False):
	"""Return the dbus proxy object for our Note Application.

	if @activate, we will activate it over d-bus (start if not running)
	"""
	bus = dbus.SessionBus()
	proxy_obj = bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus')
	dbus_iface = dbus.Interface(proxy_obj, 'org.freedesktop.DBus')

	if not activate and not dbus_iface.NameHasOwner(service_name):
		return

	service_name = "net.launchpad.Gwibber"
	obj_name = "/net/launchpad/gwibber/Interface"
	iface_name = "net.launchpad.Gwibber"

	try:
		proxyobj = bus.get_object(service_name, obj_name)
	except dbus.DBusException, e:
		pretty.print_error(__name__, e)
		return
	return dbus.Interface(proxyobj, iface_name)

# empty callback function for async callbacks
def _dummy(*args):
	pass

class SendUpdate (Action):
	def __init__(self):
		Action.__init__(self, _("Send Update"))
	def activate(self, leaf):
		gwibber = _get_interface(True)
		gwibber.send_message(leaf.object,
			reply_handler=_dummy, error_handler=_dummy)

	def item_types(self):
		yield TextLeaf

	def get_description(self):
		return __description__
