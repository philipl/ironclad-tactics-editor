#!/usr/bin/env python

from gi.repository import Gtk, Gio
from save_pb2 import SaveFile
from save_pb2 import _SAVEFILE_CARDID as CardDescriptor
from save_pb2 import _SAVEFILE_PROFILE_DATA_MISSIONCOMPLETION_OBJECTIVE as ObjectiveDescriptor
from save_pb2 import _SAVEFILE_CUTSCENEID as CutsceneDescriptor
import struct
import sys

class MainWindow(Gtk.ApplicationWindow):
  def __init__(self, application):
    Gtk.Window.__init__(self, title="Ironclad Tactics Editor",
                        type=Gtk.WindowType.TOPLEVEL)
    self.application = application

    self.set_default_size(800, 600)

    self.build_menu()
    self.build_window()

    self.filename = None

  def build_menu(self):
    action = Gio.SimpleAction.new("open", None)
    action.connect("activate", self.on_file_open)
    self.add_action(action)

    action = Gio.SimpleAction.new("save", None)
    action.connect("activate", self.on_file_save)
    self.add_action(action)

    action = Gio.SimpleAction.new("saveas", None)
    self.add_action(action)

  def build_window(self):
    grid = Gtk.Grid()
    self.add(grid)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

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
    unknown14, instructions  = self.build_general(stack)
    upgradestore = self.build_upgrade(stack)
    missionstore = self.build_missions(stack)
    ownedstore = self.build_owned(stack)
    unusedstore = self.build_unused(stack)
    scenestore = self.build_cutscene(stack)
    totalDecks, selectedDeck, secondDeck, \
    deckstore, decks = self.build_decks(stack)
    #textbuffer = self.build_dump(stack)

    return { 'box': box,
             'magic': magic,
             'wins': wins,
             'ties': ties,
             'loses': loses,
             'completed': completed,
             'unknown14': unknown14,
             'instructions': instructions,
             'upgradestore': upgradestore,
             'missionstore': missionstore,
             'ownedstore': ownedstore,
             'unusedstore': unusedstore,
             'scenestore': scenestore,
             'totalDecks': totalDecks,
             'selectedDeck': selectedDeck,
             'secondDeck': secondDeck,
             'deckstore': deckstore,
             'decks': decks,
             #'buffer': textbuffer,
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
    label.set_markup("<b>Hide Instruction Card:</b>")
    label.set_justify(Gtk.Justification.RIGHT)
    label.set_hexpand(False)
    label.set_halign(Gtk.Align.END)
    label.set_margin_right(6)
    grid.attach(label, 0, 5, 1, 1)

    instructions = Gtk.CheckButton()
    grid.attach(instructions, 1, 5, 1, 1)

    return magic, \
           wins, ties, loses, \
           completed, \
           unknown14, instructions

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

  def build_decks(self, stack):
    # Decks
    grid = Gtk.Grid()
    stack.add_titled(grid, "decks", "Decks")

    label = Gtk.Label()
    label.set_markup("<b>Selected Deck:</b>")
    label.set_justify(Gtk.Justification.RIGHT)
    label.set_hexpand(False)
    label.set_halign(Gtk.Align.END)
    label.set_margin_right(6)
    grid.attach(label, 0, 0, 1, 1)

    selected = Gtk.Entry()
    selected.set_editable(False)
    selected.set_sensitive(False)
    selected.set_hexpand(True)
    selected.set_margin_right(6)
    grid.attach(selected, 1, 0, 1, 1)

    label = Gtk.Label()
    label.set_markup("<b>Second Deck:</b>")
    label.set_justify(Gtk.Justification.RIGHT)
    label.set_hexpand(False)
    label.set_halign(Gtk.Align.END)
    label.set_margin_right(6)
    grid.attach(label, 2, 0, 1, 1)

    secondDeck = Gtk.Entry()
    secondDeck.set_editable(False)
    secondDeck.set_sensitive(False)
    secondDeck.set_hexpand(True)
    secondDeck.set_margin_right(6)
    grid.attach(secondDeck, 3, 0, 1, 1)

    label = Gtk.Label()
    label.set_markup("<b>Number of decks ever created:</b>")
    label.set_justify(Gtk.Justification.RIGHT)
    label.set_hexpand(False)
    label.set_halign(Gtk.Align.END)
    label.set_margin_right(6)
    grid.attach(label, 4, 0, 1, 1)

    totalDecks = Gtk.Entry()
    totalDecks.set_editable(False)
    totalDecks.set_sensitive(False)
    totalDecks.set_hexpand(True)
    grid.attach(totalDecks, 5, 0, 1, 1)

    scrolledwindow = Gtk.ScrolledWindow()
    scrolledwindow.set_hexpand(True)
    scrolledwindow.set_vexpand(True)
    scrolledwindow.set_margin_top(6)
    scrolledwindow.set_margin_left(6)
    scrolledwindow.set_margin_right(6)
    scrolledwindow.set_margin_bottom(6)
    grid.attach(scrolledwindow, 0, 1, 2, 1)
    
    deckstore = Gtk.ListStore(str, int)
    list = Gtk.TreeView(deckstore)
    scrolledwindow.add(list)

    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn("Deck", renderer, text=0)
    column.set_expand(True)
    column.set_sort_column_id(0)	
    list.append_column(column)

    scrolledwindow = Gtk.ScrolledWindow()
    scrolledwindow.set_hexpand(True)
    scrolledwindow.set_vexpand(True)
    scrolledwindow.set_margin_top(6)
    scrolledwindow.set_margin_left(6)
    scrolledwindow.set_margin_right(6)
    scrolledwindow.set_margin_bottom(6)
    grid.attach(scrolledwindow, 2, 1, 4, 1)
    
    cardstore = Gtk.ListStore(str)
    cardlist = Gtk.TreeView(cardstore)
    scrolledwindow.add(cardlist)

    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn("Card", renderer, text=0)
    column.set_expand(True)
    column.set_sort_column_id(0)	
    cardlist.append_column(column)

    decks = {}

    list.get_selection().connect("changed", self.on_deck_selected, cardstore, decks)

    return totalDecks, selected, secondDeck, deckstore, decks

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

  def on_deck_selected(self, selection, cardstore, decks):
    if not 'decks' in decks:
      return

    decks = decks['decks']

    deckstore, i = selection.get_selected()
    if i is None:
      return

    index = deckstore[i][1]

    for deck in decks:
      if deck.index == index:
        cardstore.clear()
        for card in deck.data.card:
          name = CardDescriptor.values_by_number[card.data.id].name
          cardstore.append([name])

  def on_file_open(self, action, data=None):
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
    self.filename = filename

  def load_profile(self, page, profile):
    if profile.present:
      #page['buffer'].set_text(str(profile))
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
      if profile.data.unknown14[0].present:
        page['unknown14'].set_value(profile.data.unknown14[0].unknown)
      page['instructions'].set_active(profile.data.hideInstructionCard)

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
        name = CutsceneDescriptor.values_by_number[scene.data.id].name
        page['scenestore'].append([name])

      page['totalDecks'].set_text(str(profile.data.numberOfDecksEverCreated))
      if profile.data.selectedDeck[0].present:
        page['selectedDeck'].set_text(str(profile.data.selectedDeck[0].selected))
      if profile.data.secondDeck[0].present:
        page['secondDeck'].set_text(str(profile.data.secondDeck[0].selected))

      page['deckstore'].clear()
      for deck in profile.data.deck:
        name = deck.data.name
        page['deckstore'].append([name, deck.index])

      page['decks']['decks'] = profile.data.deck

    else:
      page['box'].set_sensitive(False)

  def on_file_save(self, action, data=None):
    self.save_file(self.filename)

  def save_file(self, filename):
    save = SaveFile()

    save.magic = int(self.magic.get_text())
    save.active_profile = int(self.activeprofile.get_value())

    self.save_profile(self.profile0, save.profile.add())
    self.save_profile(self.profile1, save.profile.add())
    self.save_profile(self.profile2, save.profile.add())
    self.save_profile(self.profile3, save.profile.add())

    with open(filename + ".test", "wb") as f:
      data = save.SerializeToString()
      f.write(struct.pack('I', len(data)))
      f.write(data)

  def save_profile(self, page, profile):
    if page['box'].get_sensitive():
      profile.present = True
      profile.data.magic = int(page['magic'].get_text())

      loses = int(page['loses'].get_value())
      if loses != 0:
        result = profile.data.skirmish.add()
        result.result = SaveFile.Profile.Data.SkirmishResults.LOSS
        result.count = loses
      ties = int(page['ties'].get_value())
      if ties != 0:
        result = profile.data.skirmish.add()
        result.result = SaveFile.Profile.Data.SkirmishResults.TIED
        result.count = ties
      wins = int(page['wins'].get_value())
      if wins != 0:
        result = profile.data.skirmish.add()
        result.result = SaveFile.Profile.Data.SkirmishResults.WIN
        result.count = wins

      completed = page['completed'].get_active()
      if completed:
        profile.data.completedCampaign = True

      unknown14 = int(page['unknown14'].get_value())
      field = profile.data.unknown14.add()
      if unknown14 != 0:
        field.present = True
        field.unknown = unknown14

      hideInstructionCard = page['instructions'].get_active()
      if hideInstructionCard:
        profile.data.hideInstructionCard = True

      for row in page['upgradestore']:
        progress = profile.data.upgradeProgress.add()
        progress.card.data.id = CardDescriptor.values_by_name[row[0]].number
        progress.progress = row[1]

      for row in page['missionstore']:
        mission = profile.data.missionCompletion.add()
        mission.mission.data.id = int(row[0])
        obj = ObjectiveDescriptor.values_by_name[row[1]].number
        if obj != 0:
          mission.objective = obj

      for row in page['ownedstore']:
        card = profile.data.ownedCard.add()
        card.data.id = CardDescriptor.values_by_name[row[0]].number

      for row in page['unusedstore']:
        card = profile.data.unusedCard.add()
        card.data.id = CardDescriptor.values_by_name[row[0]].number

      for row in page['scenestore']:
        scene = profile.data.watchedCutscene.add()
        scene.data.id = CutsceneDescriptor.values_by_name[row[0]].number

      profile.data.numberOfDecksEverCreated = int(page['totalDecks'].get_text())

      selected = page['selectedDeck'].get_text()
      s = profile.data.selectedDeck.add()
      if selected != "":
        s.present = True
        index = int(selected)
        if index != 0:
          s.selected = index

      secondDeck = page['secondDeck'].get_text()
      s = profile.data.secondDeck.add()
      if secondDeck != "":
        s.present = True
        index = int(secondDeck)
        if index != 0:
          s.selected = index

      profile.data.deck.extend(page['decks']['decks'])

class EditorApp(Gtk.Application):
  def __init__(self):
    Gtk.Application.__init__(self,
                             application_id="apps.philipl.ironclad-tactics-editor",
                             flags=Gio.ApplicationFlags.HANDLES_OPEN)
    self.connect("startup", self.on_startup)
    self.connect("activate", self.on_activate)
    self.connect("open", self.on_open)

  def build_menu(self):
    filemenu = Gio.Menu()
    filemenu.append("Open", "win.open")
    filemenu.append("Save", "win.save")
    filemenu.append("Save As", "win.saveas")
    filemenu.append("Quit", "app.quit")

    menu = Gio.Menu()
    menu.append_submenu("File", filemenu)

    return menu

  def on_startup(self, data=None):
    action = Gio.SimpleAction.new("quit", None)
    action.connect("activate", lambda action, data: self.quit())
    self.add_action(action)

    self.set_menubar(self.build_menu())

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
