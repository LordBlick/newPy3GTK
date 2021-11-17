#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
# -*- tabstop: 4 -*-


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Gio, Pango #, Gladeui, Gio
from os import path as ph, getcwd as pwd, makedirs as mkdir
H = ph.expanduser('~') # Home dir
hh = lambda s: s.replace(H, '~')
from sys import stdout as sto
_p = lambda _str: sto.write(str(_str))
debug = (False, True)[0]
def _d(_str):
	if debug: _p(_str)
from glob import glob as ls
import json
import platform as ptf
psys = ptf.system()
prel = ptf.release()
from datetime import datetime as dttm
_l = None

class New_UI:
	def __init__(ui):
		ui.uiInit()

	uiEnter = lambda ui: Gtk.main()
	uiQuit = lambda ui: Gtk.main_quit()
	uiBind = lambda ui, w_nm: setattr(ui, w_nm, ui.bld.get_object(w_nm))

	def uiBinds(ui, s_bnds):
		for w_nm in s_bnds.split():
			ui.uiBind(w_nm)

	def uiInit(ui):
		ui.runpath = ph.dirname(ph.realpath(__file__))
		screen = Gdk.Screen.get_default()
		gtk_provider = Gtk.CssProvider()
		gtk_context = Gtk.StyleContext()
		gtk_context.add_provider_for_screen(screen, gtk_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		# Load the CSS
		f_css = Gio.File.new_for_path(f"{ui.runpath}/StdDarkGTK3.css")
		gtk_provider.load_from_file(f_css)

		ui.bld = Gtk.Builder()
		ui.bld.add_from_file(ph.join(ph.dirname(ph.abspath(__file__)), 'New.ui'))
		ui.uiBinds('mainWindow logView dlgNewName edNewName dlgDstDir')
		ui.mainWindow.show_all()
		ui.mainWindow.set_keep_above(True)
		ui.createTxtTags()

	def createTxtTags(ui):
		logBuff = ui.logView.get_buffer()
		ui.tgFlNm = logBuff.create_tag('fnm', weight = Pango.Weight.BOLD)
		ui.tgPhrs = logBuff.create_tag('phr', weight = Pango.Weight.BOLD)
		ui.tgFErr = logBuff.create_tag('err', weight = Pango.Weight.BOLD)
		ui.tgWarn = logBuff.create_tag('wrn', weight = Pango.Weight.BOLD)
		ui.tgEnum = logBuff.create_tag('num', weight = Pango.Weight.BOLD)
		for color_cfg, color_val in(
			('fgFlNm', 'yellow'),
			('fgPhrs', 'orange'), ('bgPhrs', '#002818'),
			('fgFErr', 'red'),
			('fgEnum', '#0F0'),
			('fgWarn', '#F85'),):
			tag_name = color_cfg.replace('bg', 'tg').replace('fg', 'tg')
			color = Gdk.color_parse(color_val)
			prop_name = {'bg': 'background-gdk', 'fg': 'foreground-gdk'}[color_cfg[0:2]]
			getattr(ui, tag_name).set_property(prop_name, color)

	def get_text(ui):
		tBuff = ui.editNew.get_buffer()
		return tBuff.get_text(tBuff.get_start_iter(), tBuff.get_end_iter(), False)


	set_text = lambda ui, txt='': ui.logView.get_buffer().set_text(txt)
	clr_text = lambda ui: ui.set_text()

	def _p(ui, txt, tag=None, short_path=False):
		buff = ui.logView.get_buffer()
		end = buff.get_end_iter()
		text = hh(txt) if short_path else txt
		if tag and(isinstance(tag, str)):
			tagTab = buff.get_tag_table()
			tagByNm = tagTab.lookup(tag)
			if tagByNm:
				tag = tagByNm
			elif hasattr(ui, tag):
				tag = getattr(ui, tag)
			else:
				tag = None
		if not(isinstance(tag, Gtk.TextTag)):
			buff.insert(end, text)
			return
		buff.insert_with_tags(end, text, tag)

	def _lp(ui, ls_txt, short_path=True):
		for idx, txt_obj in enumerate(ls_txt):
			if isinstance(txt_obj, str):
				ui._p(txt_obj, short_path=short_path)
			elif isinstance(txt_obj, tuple) and len(txt_obj)==2:
				ui._p(txt_obj[0], tag=txt_obj[1], short_path=short_path)
			else:
				raise TypeError(f"Unknown format in {ls_txt}[{idx}]")

class New:
	def __init__(mn):
		_p(f"Test platform…\n\tOS:{psys}\n\tRelease:{prel}\n")
		mn.uiInit()
		mn.setVars()
		mn.ui.uiEnter()

	appDlgHide = lambda mn, dlg: dlg.hide()

	def uiInit(mn):
		ui = mn.ui = New_UI()
		ui.mainWindow.connect("destroy", lambda w: mn.appQuit())
		handlers = {}
		for hn in (dr[3:] for dr in dir(mn) if dr[:3]=='app'):
			handlers['do_'+hn] = getattr(mn, 'app'+hn)
		ui.bld.connect_signals(handlers)
		global _l
		_l = ui._lp

	def setVars(mn):
		ui = mn.ui
		grt = Gtk.ResponseType
		ui.rspns = dict(map(lambda s: (int(getattr(grt, s)), f"Gtk.ResponseType.{s}"), sorted(
			filter(lambda a:a==a.upper() and(not(callable(getattr(grt, a)))), dir(grt)),
			key = lambda s: int(getattr(grt, s)), reverse=True)))

	def appClone(mn, b):
		ui = mn.ui
		response = ui.dlgNewName.run()
		#_l(("Response  „", (f"{ui.rspns[response]}", 'phr'), "”\n"))
		pn = ''
		if response == Gtk.ResponseType.OK:
			pn = ui.edNewName.get_text()
		if not pn:
			return
		response = ui.dlgDstDir.run()
		#_l(("Response  „", (f"{ui.rspns[response]}", 'phr'), "”\n"))
		dn = ''
		if response == Gtk.ResponseType.OK:
			dn = ui.dlgDstDir.get_filename()
		if not dn:
			return
		_l(("Clonning files:\n",))
		for fn in 'New.py New.ui StdDarkGTK3.css'.split():
			_l( ("  „", (f"{ph.join(dn, fn.replace('New', pn))}", 'fnm'), "”\n") )

	def appGo(mn, b):
		ui = mn.ui
		_l(("Gtk.Responses:\n"))
		for rsp in ui.rspns:
			_l(("  [", (f"{rsp: 3}", 'num'), "]:„", (f"{ui.rspns[rsp]}", 'phr'), "”\n"))
		_ls = ls('*')
		_l(("Current Dir: „", (f"{pwd()}", 'fnm'), "” with ", (f"{len(_ls)}", 'num'), " files:\n"))
		for idx, fn in enumerate(_ls):
			_l(("  [", (f"{idx+1}", 'num'), "]:„", (f"{fn}", 'fnm'), "”\n"))

	def appClrLog(mn, b):
		mn.ui.clr_text()

	def appQuit(mn, b):
		mn.ui.uiQuit()

# Entry point
if __name__ == "__main__":
	New()
