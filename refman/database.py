import bibtexparser
from .info import Info
import os

def get_cache(path):
    cf = os.path.abspath(os.path.join(path, '.bib_cache'))
    if not os.path.exists(cf):
        Database(path).cache()
    return cf

class Database():

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
        for e in self:
            for k in e.keys():
                if type(e[k]) == str:
                    e[k] = e[k].replace('\n', ' ')

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
                if type(val_new) == str:
                    val_new = val_new.replace('\n', ' ')
                val_old = e_old.get(key)
                if val_old != val_new:
                    if i not in changes_dict:
                        changes_dict[i] = {}
                    changes_dict[i][key] = (val_new, val_old)
            delkeys = [k for k in e_old.keys() if k not in e_new.keys()]
            if i not in changes_dict and len(delkeys) > 0:
                changes_dict[i] = {}
            for k in delkeys:
                changes_dict[i][k] = (None, e_old[k])
        print(changes_dict)
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
        for e in self._db.entries:
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

    def refetch(self):
        for e in self._db.entries:
            if 'doi' in e:
                info = Info(info_dict=e)
                print(e["ID"])
                rename = info.refetch()
                if(rename):
                    op = info.get('path')
                    info.rename_pdf()
                    np = info.get('path')
                    if op != np:
                        os.rename(op, np)
                print()

    def update_pdfs(self):
        for e in self._db.entries:
            if 'doi' in e and 'path' in e:
                print(e["ID"])
                os.system(f'scihubpdf {e["doi"]} {e["path"]}')
