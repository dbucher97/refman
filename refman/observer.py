from watchgod import watch, Change
import os
from notifypy import Notify

from .database import Database
from .info import Info


def is_pdf(filename):
    try:
        return os.path.splitext(filename)[1] == '.pdf'
    except IndexError:
        return False


class Observer():

    def __init__(self, my_dir, allow_renaming=False):
        self.dir = my_dir
        self.allow_renaming = allow_renaming
        self._db = Database(my_dir, observer=self)
        self._allowed_renames = []
        self._allowed_modifications = []
        self._notify = Notify(default_notification_application_name="RefMan")

    def start(self):
        for changes in watch(self.dir):
            print(changes)
            move_from, move_to = None, None
            modified = False
            for change, path in changes:
                basename = os.path.basename(path)
                if change == Change.added:
                    move_to = (basename, path)
                elif change == Change.deleted:
                    move_from = (basename, path)
                elif change == Change.modified:
                    if not os.path.basename(path).startswith('.'):
                        modified = path
            if not modified and (move_from is not None or move_to is not None):
                if move_from is None:
                    self._handle_add(move_to[1])
                elif move_to is None:
                    self._handle_delete(move_from[1])
                elif move_to[0] != move_from[0]:
                    self._handle_rename(move_from[1], move_to[1])
                else:
                    self._handle_move(move_from[1], move_to[1])
            if modified:
                self._handle_modified(modified)

    def _rename_info(self, filename, info):
        rename = info.rename_pdf()
        if rename:
            self.allow_rename(rename)
            os.rename(filename, rename)

    def _handle_add(self, filename):
        if(is_pdf(filename)):
            info = Info(filename)
            self._notify.title = "New PDF detected."
            if info.retrieve():
                self._rename_info(filename, info)
                self._notify.message = f'{info.get("ID")} added: "{info.get("title")}"'
            else:
                self._notify.message = 'Automatic metadata retrieval failed,' + \
                    ' manual action required!'
            if self._db.add(info):
                self._notify.send()

    def _handle_delete(self, filename):
        if(is_pdf(filename)):
            self._db.remove(filename)

    def _handle_rename(self, filename_from, filename_to):
        if filename_to in self._allowed_renames:
            self._allowed_renames.remove(filename_to)
            return

        if not self.allow_renaming:
            os.rename(filename_to, filename_from)
            self._allowed_renames.append(filename_from)

    def _handle_move(self, filename_from, filename_to):
        for e in self._db:
            if e.get('path') == filename_from:
                e['path'] = filename_to
                break
        self._db.save()

    def _handle_modified(self, filename):
        filename = os.path.abspath(filename)

        if filename in self._allowed_modifications:
            self._allowed_modifications.remove(filename)
            return

        if filename == self._db.get_file():
            changes = self._db.changes()

            for key, val in changes.items():
                info = Info(info_dict=self._db.idx(key))
                filename = info.get('path')
                if info.handle_changes(val):
                    self._rename_info(filename, info)

                    self._notify.title = 'Handeled Changes'
                    self._notify.message = info.get('title')
                    self._notify.send()

                self._db.set(key, info)


        self._db.save()

    def allow_rename(self, filename_to):
        self._allowed_renames.append(filename_to)

    def allow_modification(self, filename):
        self._allowed_modifications.append(os.path.abspath(filename))
