# TODO: don't insert header if one already exists

# STEPS WE ARE TRYING TO ACCOMPLISH:
# - go to beginning of file
# - get path of file relative to project
# - adjust path based on settings
# - determine if first line is already commented out
# - remove line and trailing line if it is
# - insert path into file as first line with a line after
# - move selection back to beginning of file
# - run toggle_comment command

import sublime
import sublime_plugin
import os

def get_setting(string, view = None):
  if view and view.settings().get(string):
    return view.settings().get(string)
  else:
    return sublime.load_settings('insert_file_path.sublime-settings').get(string)

class InsertFilePathCommand(sublime_plugin.TextCommand):

  def run(self, edit):
    view = self.view
    sel = view.sel()[0].a

    # Make sure this is a scope we want to insert paths into
    if not self.is_valid_scope(sel, view): return

    # Get the parsed path to the file
    path = self.get_path(view)

    if not path: return
    if self.has_valid_header_comment(path, view): return

    # Insert the text
    text = path + "\n\n"
    view.insert(edit, 0, text)

    # Comment out the inserted line
    # This allows us to get syntax-specific comments for FREE
    view.run_command("goto_line", { "line": 1 })
    view.run_command("toggle_comment")

  def get_path(self, view):
    path = view.file_name()
    project_path = ""

    relative_to = get_setting("ifp_relative_to_dir", view)

    for f in sublime.active_window().folders():
      if f in view.file_name():
        project_path = f

    project_path = os.path.join(project_path, relative_to) + os.sep
    relative_path = path[len(project_path):]

    print "relative_to: " + relative_to
    print "project_path: " + project_path
    print "relative_path: " + relative_path

    return relative_path

  # TODO: implement this
  def has_valid_header_comment(self, path, view):
    return False

  def is_valid_scope(self, sel, view):
    valid_scopes = get_setting("ifp_valid_scopes", view)
    print "scope: " + view.scope_name(sel)
    return any(scope in view.scope_name(sel) for scope in valid_scopes)

class InsertFilePathEventListener(sublime_plugin.EventListener):

  def on_pre_save(self, view):
    insert_on_save = get_setting("ifp_insert_on_save")
    if insert_on_save:
      view.run_command("insert_file_path")
