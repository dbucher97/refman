import bibtexparser
import os


class Database():

    def get_cache(path):
        cf = os.path.abspath(os.path.join(path, '.bib_cache'))
        if not os.path.exists(cf):
            Database(path).cache()
        return cf

    def __init__(self, path, master='master', observer=None):
        self._file = os.path.abspath(os.path.join(path, master + '.bib'))
        if not os.path.exists(self._file):
            open(self._file, 'w').close()
        self._db = None
        self._observer = observer
        self._cache_file = os.path.abspath(os.path.join(path, '.bib_cache'))
        self.load()

    def load(self):
        with open(self._file, 'r') as f:
            self._db = bibtexparser.load(f)

    def save(self):
        if self._observer is not None:
            self._observer.allow_modification(self._file)
        with open(self._file, 'w') as f:
            bibtexparser.dump(self._db, f)
        self.cache()

    def cache(self):
        with open(self._cache_file, 'w') as f:
            for e in self._db.entries:
                title = e.get('title')
                if title == None:
                    continue
                title = title.replace('\n', ' ')
                f.write(f'{e.get("ID")}:{title}\n')

    def changes(self):
        with open(self._file, 'r') as f:
            db = bibtexparser.load(f)
        changes_dict = {}
        for i, (e_new, e_old) in enumerate(zip(db.entries, self._db.entries)):
            for key, val_new in e_new.items():
                val_old = e_old.get(key)
                if val_old != val_new:
                    if i not in changes_dict:
                        changes_dict[i] = {}
                    changes_dict[i][key] = (val_new, val_old)
        return changes_dict

    def add(self, info):
        for e in self._db.entries:
            if info.get('ID') == e.get('ID'):
                return False
        self._db.entries.append(info.get_dict())
        self.save()
        self.load()
        return True

    def remove(self, pdf):
        pdf = os.path.abspath(pdf)
        es = []
        for i, e in enumerate(self._db.entries):
            if e.get('path') == pdf:
                es.append(e)
        for e in es:
            self._db.entries.remove(e)
        self.save()
        self.load()

    def get_file(self):
        return self._file

    def get(self, bid, key=None):
        for e in self._db.entries:
            if e.get('ID') == bid:
                if key is None:
                    return Info(info_dict=e)
                else:
                    return e.get(key)

    def __iter__(self):
        for e in self._db.entries:
            yield e

    def idx(self, key):
        return self._db.entries[key]

    def set(self, key, info):
        self._db.entries[key] = info.get_dict()
