#!/usr/bin/env python2
# coding=utf-8
"""
SC-Controller - Action Editor - Per-Axis Component

Handles all XYActions
"""
from __future__ import unicode_literals
from scc.tools import _

from gi.repository import Gtk, Gdk, GLib, GObject
from scc.gui.ae import AEComponent, describe_action
from scc.gui.area_to_action import action_to_area
from scc.gui.simple_chooser import SimpleChooser
from scc.gui.action_editor import ActionEditor
from scc.gui.parser import GuiActionParser
from scc.actions import Action, NoAction, XYAction
from scc.special_actions import GesturesAction
from scc.modifiers import NameModifier

import os, logging
log = logging.getLogger("AE.PerAxis")

__all__ = [ 'GestureComponent' ]


class GestureComponent(AEComponent):
	GLADE = "ae/gesture.glade"
	NAME = "gesture"
	CTXS = Action.AC_STICK | Action.AC_PAD
	PRIORITY = 1
	
	def __init__(self, app, editor):
		AEComponent.__init__(self, app, editor)
		self.x = self.y = NoAction()
	
	
	def set_action(self, mode, action):
		lstGestures = self.builder.get_object("lstGestures")
		lstGestures.clear()
		if isinstance(action, GesturesAction):
			for gstr in action.gestures:
				o = GObject.GObject()
				o.action = action.gestures[gstr]
				o.gstr = gstr
				lstGestures.append( (
					GestureComponent.nice_gstr(gstr),
					o.action.describe(Action.AC_MENU),
					o
				) )
	
	
	ARROWS = {
		#'U' : '▲', 'D' : '▼', 'L' : '◀', 'R' : '▶',
		'U' : '↑', 'D' : '↓', 'L' : '←', 'R' : '→',
	}
	@staticmethod
	def nice_gstr(gstr):
		"""
		Replaces characters UDLR in gesture string with unicode arrows.
		▲ ▼ ◀ ▶
		← → ↑ ↓
		"""
		l = lambda x : GestureComponent.ARROWS[x] if x in GestureComponent.ARROWS else ""
		return "".join(map(l, gstr))
	
	
	def get_button_title(self):
		return _("Gestures")
	
	
	def handles(self, mode, action):
		return isinstance(action, GesturesAction)
	
	
	def send(self):
		self.editor.set_action(XYAction(self.x, self.y))
	
	
	def on_tvGestures_cursor_changed(self, tv, *a):
		tvGestures = self.builder.get_object("tvGestures")
		btEditGesture = self.builder.get_object("btEditGesture")
		btEditAction = self.builder.get_object("btEditAction")
		btRemove = self.builder.get_object("btRemove")
		model, iter = tvGestures.get_selection().get_selected()
		if iter is None:
			btEditGesture.set_sensitive(False)
			btEditAction.set_sensitive(False)
			btRemove.set_sensitive(False)
		else:
			btEditGesture.set_sensitive(True)
			btEditAction.set_sensitive(True)
			btRemove.set_sensitive(True)
	
	
	def on_btEditAction_clicked(self, *a):
		""" Handler for "Edit Action" button """
		tvGestures = self.builder.get_object("tvGestures")
		model, iter = tvGestures.get_selection().get_selected()
		item = model.get_value(iter, 2)
		# Setup editor
		e = ActionEditor(self.app, self.on_action_chosen)
		e.set_title(_("Edit Action"))
		e.set_input("ID", item.action, mode = Action.AC_BUTTON)
		# Display editor
		e.show(self.editor.window)
	
	
	def on_action_chosen(self, id, action):
		tvGestures = self.builder.get_object("tvGestures")
		model, iter = tvGestures.get_selection().get_selected()
		item = model.get_value(iter, 2)
		item.action = action
		model.set_value(iter, 1, action.describe(Action.AC_MENU))
		self.update()
	
	
	def update(self):
		a = GesturesAction()
		tvGestures = self.builder.get_object("tvGestures")
		model, iter = tvGestures.get_selection().get_selected()
		for row in model:
			item = row[2]
			a.gestures[item.gstr] = item.action
			if item.action.name:
				a.gestures[item.gstr] = NameModifier(item.action.name, item.action)
		self.editor.set_action(a)