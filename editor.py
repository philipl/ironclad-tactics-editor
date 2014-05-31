#!/usr/bin/env python

from gi.repository import Gtk, Gio
from save_pb2 import SaveFile
from save_pb2 import _SAVEFILE_CARDID as CardDescriptor
from save_pb2 import _SAVEFILE_PROFILE_DATA_MISSIONCOMPLETION_OBJECTIVE as ObjectiveDescriptor
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
  def __init__(self, box, upgradestore, ownedstore, unusedstore, buffer):
    self.box = box
    self.upgradestore = upgradestore
    self.ownedstore = ownedstore
    self.unusedstore = unusedstore
    self.buffer = buffer

class MainWindow(Gtk.ApplicationWindow):
  def __init__(self, application):
    Gtk.Window.__init__(self, title="Ironclad Tactics Editor",
                        type=Gtk.WindowType.TOPLEVEL)
    self.application = application

    self.set_default_size(800, 600)

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
    # Add notebook page
    label = Gtk.Label(title)

    box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
    notebook.append_page(box, label)

    # Primary contents is a stack
    stack = Gtk.Stack()
    stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
    stack.set_transition_duration(250)

    stackswitcher = Gtk.StackSwitcher()
    stackswitcher.set_stack(stack)
    stackswitcher.set_halign(Gtk.Align.CENTER)
    box.pack_start(stackswitcher, False, False, 0)
    box.pack_start(stack, True, True, 0)

    magic, wins, ties, loses, completed, \
    unknown14, unknown15, unknown21  = self.build_general(stack)
    upgradestore = self.build_upgrade(stack)
    missionstore = self.build_missions(stack)
    ownedstore = self.build_owned(stack)
    unusedstore = self.build_unused(stack)
    scenestore = self.build_cutscene(stack)
    textbuffer = self.build_dump(stack)

    return { 'box': box,
             'magic': magic,
             'wins': wins,
             'ties': ties,
             'loses': loses,
             'completed': completed,
             'unknown14': unknown14,
             'unknown15': unknown15,
             'unknown21': unknown21,
             'upgradestore': upgradestore,
             'missionstore': missionstore,
             'ownedstore': ownedstore,
             'unusedstore': unusedstore,
             'scenestore': scenestore,
             'buffer': textbuffer,
           }

  def build_general(self, stack):
    # General Stuff
    grid = Gtk.Grid()
    stack.add_titled(grid, "general", "General")

    label = Gtk.Label()
    label.set_markup("<b>Magic:</b>")
    label.set_justify(Gtk.Justification.RIGHT)
    label.set_hexpand(False)
    label.set_halign(Gtk.Align.END)
    label.set_margin_right(6)
    grid.attach(label, 0, 0, 1, 1)

    magic = Gtk.Entry()
    magic.set_editable(False)
    magic.set_sensitive(False)
    magic.set_hexpand(True)
    grid.attach(magic, 1, 0, 1, 1)

    label = Gtk.Label()
    label.set_markup("<b>Skirmish Wins:</b>")
    label.set_justify(Gtk.Justification.RIGHT)
    label.set_hexpand(False)
    label.set_halign(Gtk.Align.END)
    label.set_margin_right(6)
    grid.attach(label, 0, 1, 1, 1)

    wins = Gtk.SpinButton.new_with_range(0, 1000000, 1)
    wins.set_hexpand(True)
    wins.set_halign(Gtk.Align.START)
    grid.attach(wins, 1, 1, 1, 1)

    label = Gtk.Label()
    label.set_markup("<b>Skirmish Ties:</b>")
    label.set_justify(Gtk.Justification.RIGHT)
    label.set_hexpand(False)
    label.set_halign(Gtk.Align.END)
    label.set_margin_right(6)
    grid.attach(label, 0, 2, 1, 1)

    ties = Gtk.SpinButton.new_with_range(0, 1000000, 1)
    ties.set_hexpand(True)
    ties.set_halign(Gtk.Align.START)
    grid.attach(ties, 1, 2, 1, 1)

    label = Gtk.Label()
    label.set_markup("<b>Skirmish Loses:</b>")
    label.set_justify(Gtk.Justification.RIGHT)
    label.set_hexpand(False)
    label.set_halign(Gtk.Align.END)
    label.set_margin_right(6)
    grid.attach(label, 0, 3, 1, 1)

    loses = Gtk.SpinButton.new_with_range(0, 1000000, 1)
    loses.set_hexpand(True)
    loses.set_halign(Gtk.Align.START)
    grid.attach(loses, 1, 3, 1, 1)

    label = Gtk.Label()
    label.set_markup("<b>Completed Campaign:</b>")
    label.set_justify(Gtk.Justification.RIGHT)
    label.set_hexpand(False)
    label.set_halign(Gtk.Align.END)
    label.set_margin_right(6)
    grid.attach(label, 0, 4, 1, 1)

    completed = Gtk.CheckButton()
    grid.attach(completed, 1, 4, 1, 1)

    separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
    separator.set_margin_left(6)
    separator.set_margin_right(6)
    grid.attach(separator, 2, 0, 1, 5)

    label = Gtk.Label()
    label.set_markup("<b>Unknown14:</b>")
    label.set_justify(Gtk.Justification.RIGHT)
    label.set_hexpand(False)
    label.set_halign(Gtk.Align.END)
    label.set_margin_right(6)
    grid.attach(label, 3, 1, 1, 1)

    unknown14 = Gtk.SpinButton.new_with_range(0, 1000000, 1)
    unknown14.set_hexpand(True)
    unknown14.set_halign(Gtk.Align.START)
    grid.attach(unknown14, 4, 1, 1, 1)

    label = Gtk.Label()
    label.set_markup("<b>Unknown15:</b>")
    label.set_justify(Gtk.Justification.RIGHT)
    label.set_hexpand(False)
    label.set_halign(Gtk.Align.END)
    label.set_margin_right(6)
    grid.attach(label, 3, 2, 1, 1)

    unknown15 = Gtk.CheckButton()
    grid.attach(unknown15, 4, 2, 1, 1)

    label = Gtk.Label()
    label.set_markup("<b>Unknown21:</b>")
    label.set_justify(Gtk.Justification.RIGHT)
    label.set_hexpand(False)
    label.set_halign(Gtk.Align.END)
    label.set_margin_right(6)
    grid.attach(label, 3, 3, 1, 1)

    unknown21 = Gtk.SpinButton.new_with_range(0, 1000000, 1)
    unknown21.set_hexpand(False)
    unknown21.set_halign(Gtk.Align.START)
    grid.attach(unknown21, 4, 3, 1, 1)

    return magic, \
           wins, ties, loses, \
           completed, \
           unknown14, unknown15, unknown21

  def build_upgrade(self, stack):
    # Upgrade Progress List
    scrolledwindow = Gtk.ScrolledWindow()
    scrolledwindow.set_hexpand(True)
    scrolledwindow.set_vexpand(True)
    stack.add_titled(scrolledwindow, "upgrades", "Upgrade progress")
    
    upgradestore = Gtk.ListStore(str, int)
    list = Gtk.TreeView(upgradestore)
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

    return upgradestore

  def build_missions(self, stack):
    # Mission Completion List
    scrolledwindow = Gtk.ScrolledWindow()
    scrolledwindow.set_hexpand(True)
    scrolledwindow.set_vexpand(True)
    stack.add_titled(scrolledwindow, "missions", "Mission Completion")
    
    missionstore = Gtk.ListStore(str, str)
    list = Gtk.TreeView(missionstore)
    scrolledwindow.add(list)

    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn("Mission", renderer, text=0)
    column.set_expand(True)
    column.set_sort_column_id(0)	
    list.append_column(column)

    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn("Objective", renderer, text=1)
    column.set_sort_column_id(1)	
    list.append_column(column)

    return missionstore

  def build_owned(self, stack):
    # Owned Card List
    scrolledwindow = Gtk.ScrolledWindow()
    scrolledwindow.set_hexpand(True)
    scrolledwindow.set_vexpand(True)
    stack.add_titled(scrolledwindow, "owned", "Owned Cards")
    
    ownedstore = Gtk.ListStore(str)
    list = Gtk.TreeView(ownedstore)
    scrolledwindow.add(list)

    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn("Card", renderer, text=0)
    column.set_expand(True)
    column.set_sort_column_id(0)	
    list.append_column(column)

    return ownedstore

  def build_unused(self, stack):
    # Unused Card List
    scrolledwindow = Gtk.ScrolledWindow()
    scrolledwindow.set_hexpand(True)
    scrolledwindow.set_vexpand(True)
    stack.add_titled(scrolledwindow, "unused", "Unused Cards")
    
    unusedstore = Gtk.ListStore(str)
    list = Gtk.TreeView(unusedstore)
    scrolledwindow.add(list)

    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn("Card", renderer, text=0)
    column.set_expand(True)
    column.set_sort_column_id(0)	
    list.append_column(column)

    return unusedstore

  def build_cutscene(self, stack):
    # Watched Cutscenes
    scrolledwindow = Gtk.ScrolledWindow()
    scrolledwindow.set_hexpand(True)
    scrolledwindow.set_vexpand(True)
    stack.add_titled(scrolledwindow, "cutscene", "Watched Cutscenes")
    
    scenestore = Gtk.ListStore(str)
    list = Gtk.TreeView(scenestore)
    scrolledwindow.add(list)

    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn("Cutscene", renderer, text=0)
    column.set_expand(True)
    column.set_sort_column_id(0)	
    list.append_column(column)

    return scenestore

  def build_dump(self, stack):
    # Text Dump
    scrolledwindow = Gtk.ScrolledWindow()
    scrolledwindow.set_hexpand(True)
    scrolledwindow.set_vexpand(True)
    stack.add_titled(scrolledwindow, "dump", "Text Dump")
    
    textview = Gtk.TextView()
    textbuffer = textview.get_buffer()
    textbuffer.set_text("Hello World")
    scrolledwindow.add(textview)

    return textbuffer

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
      page['buffer'].set_text(str(profile))
      page['box'].set_sensitive(True)

      page['magic'].set_text(str(profile.data.magic))
      for result in profile.data.skirmish:
        if result.result == SaveFile.Profile.Data.SkirmishResults.LOSS:
          page['loses'].set_value(result.count)
        elif result.result == SaveFile.Profile.Data.SkirmishResults.TIED:
          page['ties'].set_value(result.count)
        elif result.result == SaveFile.Profile.Data.SkirmishResults.WIN:
          page['wins'].set_value(result.count)
      page['completed'].set_active(profile.data.completedCampaign)
      if profile.data.unknown14.present:
        page['unknown14'].set_value(profile.data.unknown14.unknown)
      page['unknown15'].set_active(profile.data.unknown15)
      if profile.data.unknown21.present:
        page['unknown21'].set_value(profile.data.unknown21.unknown)

      page['upgradestore'].clear()
      for progress in profile.data.upgradeProgress:
        name = CardDescriptor.values_by_number[progress.card.data.id].name
        page['upgradestore'].append([name, progress.progress])

      page['missionstore'].clear()
      for mission in profile.data.missionCompletion:
        name = str(mission.mission.data.id)
        objective = ObjectiveDescriptor.values_by_number[mission.objective].name
        page['missionstore'].append([name, objective])

      page['ownedstore'].clear()
      for card in profile.data.ownedCard:
        name = CardDescriptor.values_by_number[card.data.id].name
        page['ownedstore'].append([name])

      page['unusedstore'].clear()
      for card in profile.data.unusedCard:
        name = CardDescriptor.values_by_number[card.data.id].name
        page['unusedstore'].append([name])
      page['scenestore'].clear()
      for scene in profile.data.watchedCutscene:
        name = str(scene.data.id)
        page['scenestore'].append([name])
    else:
      page['box'].set_sensitive(False)

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
