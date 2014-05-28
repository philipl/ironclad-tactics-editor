#!/usr/bin/env python

from gi.repository import Gtk, Gio
from save_pb2 import SaveFile
from save_pb2 import _SAVEFILE_CARDID as CardDescriptor
import struct
import sys

UI_INFO = """
<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menuitem action='FileOpen' />
      <menuitem action='FileSave' />
      <menuitem action='FileSaveAs' />
      <separator/>
      <menuitem action='FileQuit' />
    </menu>
  </menubar>
</ui>
"""

class Page():
  def __init__(self, box, store, buffer):
    self.box = box
    self.store = store
    self.buffer = buffer

class MainWindow(Gtk.ApplicationWindow):
  def __init__(self, application):
    Gtk.Window.__init__(self, title="Ironclad Tactics Editor",
                        type=Gtk.WindowType.TOPLEVEL)
    self.application = application

    self.set_default_size(640, 360)

    self.build_window()

  def build_menu(self):
    uimanager = Gtk.UIManager()
    uimanager.add_ui_from_string(UI_INFO)
    accelgroup = uimanager.get_accel_group()
    self.add_accel_group(accelgroup)

    action_group = Gtk.ActionGroup("actions")
    uimanager.insert_action_group(action_group)

    action_filemenu = Gtk.Action("FileMenu", "File", None, None)
    action_group.add_action(action_filemenu)

    action_fileopen = Gtk.Action("FileOpen", None, None, Gtk.STOCK_OPEN)
    action_fileopen.connect("activate", self.on_file_open)
    action_group.add_action(action_fileopen)

    action_filesave = Gtk.Action("FileSave", None, None, Gtk.STOCK_SAVE)
    action_group.add_action(action_filesave)

    action_filesaveas = Gtk.Action("FileSaveAs", None, None, Gtk.STOCK_SAVE_AS)
    action_group.add_action(action_filesaveas)

    action_filequit = Gtk.Action("FileQuit", None, None, Gtk.STOCK_QUIT)
    action_filequit.connect("activate", self.on_menu_file_quit)
    action_group.add_action(action_filequit)

    return uimanager

  def build_window(self):
    grid = Gtk.Grid()
    self.add(grid)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    uimanager = self.build_menu()
    menubar = uimanager.get_widget("/MenuBar")
    grid.attach(menubar, 0, 0, 2, 1)

    magiclabel = Gtk.Label()
    magiclabel.set_markup("<b>Magic:</b>")
    magiclabel.set_justify(Gtk.Justification.RIGHT)
    magiclabel.set_hexpand(False)
    magiclabel.set_halign(Gtk.Align.END)
    grid.attach(magiclabel, 0, 1, 1, 1)

    self.magic = Gtk.Entry()
    self.magic.set_editable(False)
    self.magic.set_sensitive(False)
    self.magic.set_hexpand(True)
    grid.attach(self.magic, 1, 1, 1, 1)

    self.notebook = Gtk.Notebook()
    grid.attach(self.notebook, 0, 2, 2, 1)
    self.profile0 = self.build_profile_page(self.notebook, "Profile 0")
    self.profile1 = self.build_profile_page(self.notebook, "Profile 1")
    self.profile2 = self.build_profile_page(self.notebook, "Profile 2")
    self.profile3 = self.build_profile_page(self.notebook, "Profile 3")

    activebox = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)

    activelabel = Gtk.Label()
    activelabel.set_markup("<b>Active Profile:</b>")
    activelabel.set_justify(Gtk.Justification.RIGHT)
    activebox.pack_start(activelabel, False, False, 0)

    self.activeprofile = Gtk.SpinButton.new_with_range(0, 3, 1)
    activebox.pack_start(self.activeprofile, True, True, 0)

    self.notebook.set_action_widget(activebox, Gtk.PackType.END)
    activebox.show_all()
    self.notebook.set_sensitive(False)

  def build_profile_page(self, notebook, title):
    label = Gtk.Label(title)

    box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
    notebook.append_page(box, label)

    stack = Gtk.Stack()
    stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
    stack.set_transition_duration(250)

    stackswitcher = Gtk.StackSwitcher()
    stackswitcher.set_stack(stack)
    stackswitcher.set_halign(Gtk.Align.CENTER)
    box.pack_start(stackswitcher, False, False, 0)
    box.pack_start(stack, True, True, 0)

    scrolledwindow = Gtk.ScrolledWindow()
    scrolledwindow.set_hexpand(True)
    scrolledwindow.set_vexpand(True)
    stack.add_titled(scrolledwindow, "upgrades", "Upgrade progress")
    
    store = Gtk.ListStore(str, int)
    list = Gtk.TreeView(store)
    scrolledwindow.add(list)

    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn("Card", renderer, text=0)
    column.set_expand(True)
    column.set_sort_column_id(0)	
    list.append_column(column)

    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn("Progress", renderer, text=1)
    column.set_sort_column_id(1)	
    list.append_column(column)

    scrolledwindow = Gtk.ScrolledWindow()
    scrolledwindow.set_hexpand(True)
    scrolledwindow.set_vexpand(True)
    stack.add_titled(scrolledwindow, "dump", "Text Dump")
    
    textview = Gtk.TextView()
    textbuffer = textview.get_buffer()
    textbuffer.set_text("Hello World")
    scrolledwindow.add(textview)

    return Page(box, store, textbuffer)

  def on_menu_file_quit(self, widget):
    self.application.quit()

  def on_file_open(self, widget):
    dialog = Gtk.FileChooserDialog("Please choose a file", self,
                                   Gtk.FileChooserAction.OPEN,
                                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                   Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

    filter = Gtk.FileFilter()
    filter.set_name("Save Games")
    filter.add_pattern("*.zidata")
    dialog.add_filter(filter)

    filter = Gtk.FileFilter()
    filter.set_name("Any Files")
    filter.add_pattern("*")
    dialog.add_filter(filter)

    response = dialog.run()
    if response == Gtk.ResponseType.OK:
      self.load_file(dialog.get_filename())

    dialog.destroy()

  def load_file(self, filename):
    with open(filename, "rb") as f:
      f.seek(4)
      save = SaveFile()
      save.ParseFromString(f.read())

      self.magic.set_text(str(save.magic))
      self.activeprofile.set_value(save.active_profile)

      self.load_profile(self.profile0, save.profile[0])
      self.load_profile(self.profile1, save.profile[1])
      self.load_profile(self.profile2, save.profile[2])
      self.load_profile(self.profile3, save.profile[3])

      self.notebook.set_sensitive(True)

  def load_profile(self, page, profile):
    if profile.present:
      page.buffer.set_text(str(profile))
      page.box.set_sensitive(True)

      page.store.clear()
      for progress in profile.data.upgradeProgress:
        name = CardDescriptor.values_by_number[progress.card.data.id].name
        page.store.append([name, progress.progress])
    else:
      page.box.set_sensitive(False)

class EditorApp(Gtk.Application):
  def __init__(self):
    Gtk.Application.__init__(self,
                             application_id="apps.philipl.ironclad-tactics-editor",
                             flags=Gio.ApplicationFlags.HANDLES_OPEN)
    self.connect("activate", self.on_activate)
    self.connect("open", self.on_open)

  def on_activate(self, data=None):
    window = MainWindow(self)
    self.add_window(window)
    window.show_all()

  def on_open(self, app, files, hint, data=None):
    for file in files:
      window = MainWindow(self)
      app.add_window(window)
      window.load_file(file.get_path())
      window.show_all()

if __name__ == "__main__":
  app = EditorApp()
  app.run(sys.argv)
