import sublime
import sublime_plugin
import fnmatch
from .scheduler import *
from .highlight_manager import *

SETTINGS = [
    "regex",
    "enabled",
    "on_load",
    "on_modify",
    "disable_pattern",
    "max_file_size",
    "whitelist_folders",
    "delay"
]

class PersistentRegexHighlightViewCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super(PersistentRegexHighlightViewCommand, self).__init__(*args, **kwargs)
        self.timer = Timer()

    def run(self, edit, settings={}):
        view = self.view
        filename = view.file_name()

        #print ("Running for %s" % view.id())

        if len(settings) == 0:
            settings = get_settings(view)

        if view.settings().get('is_widget'):
            return

        def delayed_run():
            #print("Delayed run")
            max_file_size = settings.get("max_file_size", 0)
            if  max_file_size > 0 and view.size() > max_file_size:
                #print("File too big: %s" % view.size()) 
                self.view.set_status("highlighter", "Not highlighting, file too big")
                return

            highlight_manager = HighlightManager(view, settings)

            highlight_manager.remove_highlight()

            disable_pattern = settings.get("disable_pattern")

            pattern_enable = True
            #print("Do running")

            for pattern in disable_pattern:
                if filename is None:
                    continue

                if fnmatch.fnmatch(filename, pattern):
                    pattern_enable = False
                    break

            if settings.get("enabled") and pattern_enable:
                #print("Aaaand run!")
                highlight_manager.highlight()

        time = settings.get("delay", 0)
        self.timer.schedule(time, delayed_run)
        self.view.set_status("highlighter", "Highlighting scheduled")

class PersistentRegexHighlightAllViewsCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        windows = sublime.windows()

        for window in windows:
            views = window.views()
            for view in views:
                view.run_command("persistent_regex_highlight_view")


class RemovePersistentRegexHighlightViewCommand(sublime_plugin.TextCommand):
    def run(self, edit, settings={}):
        view = self.view
        if (len(settings) == 0):
            settings = get_settings(view)

        highlight_manager = HighlightManager(view, settings)
        highlight_manager.remove_highlight()


class RemovePersistentRegexHighlightAllViewsCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        windows = sublime.windows()

        for window in windows:
            views = window.views()
            for view in views:
                view.run_command("remove_persistent_regex_highlight_view")


class PersistentRegexHighlightEvents(sublime_plugin.EventListener):

    def on_load(self, view):
        settings = get_settings(view)
        if settings.get("on_load"):
            self.try_run_command(view, settings)

    def on_modified(self, view):
        settings = get_settings(view)
        if settings.get("on_modify"):
            self.try_run_command(view, settings)

    def try_run_command(self, view, settings):
        if len(settings.get("whitelist_folders")) > 0:
            filename = _normalize_to_sublime_path(view.file_name())
            for folder in settings.get("whitelist_folders"):
                folder = _normalize_to_sublime_path(folder)
                common = os.path.commonprefix([folder, filename])
                if common == folder:
                    view.run_command("persistent_regex_highlight_view",
                                     {"settings": settings})
                    break
        else:
            view.run_command("persistent_regex_highlight_view",
                             {"settings": settings})

    def _normalize_to_sublime_path(path):
        path = os.path.normpath(path)
        path = re.sub(r"^([a-zA-Z]):", "/\\1", path)
        path = re.sub(r"\\", "/", path)
        return path


def get_settings(view):
    plugin_name = "PersistentRegexHighlight"
    settings = sublime.load_settings("%s.sublime-settings" % plugin_name)
    project_settings = view.settings().get(plugin_name, {})
    local_settings = {}

    for setting in SETTINGS:
        local_settings[setting] = settings.get(setting)

    for key in project_settings:
        if key in SETTINGS:
            local_settings[key] = project_settings[key]
        else:
            print("PersistentRegexHighlight: Invalid key '" + key +
                  "' in project settings.")

    return local_settings
