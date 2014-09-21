Ironclad Tactics Editor
=======================

This program allows you to edit the save game files for Ironclad Tactics.

It's not 100% complete, but it allows you to do pretty much anything that
it's possible to do with the save games (which isn't as much as you'd think).

Python Dependencies
-------------------

* PyGObject
* protobuf

External Dependencies
---------------------

* make : To make stuff
* protoc : The Protobuf compiler

These will be available as system packages on any modern Linux distro.

Compiling the protobuf descriptor
---------------------------------

Before you can run the editor, you need to generate the python bindings for
the protobuf descriptor (The save game is a protobuf). To do this, run 'make'
in the source directory. 

Running on a non-Linux platform
-------------------------------

While this editor is completely crossplatform and should work on Windows
or OSX, the challenges involved in getting a working python environment
going, with PyGObject and GTK3 correctly installed, are large, and beyond
the scope of anything I can document here. If you can do it, congratulations.

Save game locations
-------------------

To find your save file, first identify the game's config directory,
depending on your OS:

* Windows: %USERPROFILE%\Documents\My Games\Ironclad Tactics
* OS X: ~/Library/Application Support/Ironclad Tactics/
* Linux: ~/.ironcladtactics/

In this location is a 'profiles' directory. In that directory is a directory
with a long number for its name, and inside that is your 'save.zidata' file.
This is what you need to upload to load in the editor. Obviously, you should
back up your save first, in case something goes wrong.

Using the Editor
----------------

The editor doesn't actually allow you to edit much right now - it's mostly
read-only. Primarily it lets you alter the number of skirmishes you've
won, so that you can unlock PvP cards.

Future Work
-----------

If someone wanted to add deeper editing capabilities, such as adding new
Mission Completion records, or increasing Upgrade progress, it would not be
hard to do so. Note that the Owned Card list is purely descriptive - it cannot
be used to give you cards for your decks. The cards you are allowed to use are
calculated based on mission completions, upgrade progress, and skirmish wins.

This means you cannot give yourself any of the special mission cards for use in
other missions. How sad.
