import pdf2doi
import os
import bibtexparser
import re
import datetime


class Info():

    def __init__(self, pdf_file='', info_dict=None):
        if info_dict is not None:
            self.info_dict = info_dict
            pdf_file = self.info_dict.get('path')
        else:
            self.info_dict = {}
        if not pdf_file:
            raise Exception('Cannot innit Info without pdf_file')
        self.pdf_file = os.path.abspath(pdf_file)

    def basic_dict(self):
        return {'path': self.pdf_file,
                'ID': os.path.splitext(os.path.basename(self.pdf_file))[0]
                        .replace(' ', ''),
                'ENTRYTYPE': 'article',
                'todo': 'yes',
                'year': f'{datetime.datetime.now().year}'}

    def retrieve(self):
        res = pdf2doi.pdf2doi(
            self.pdf_file, webvalidation=False, verbose=True)
        print(res)
        s = None
        if res['identifier_type'] == 'DOI':
            print("Start doi2bib")
            s = os.popen(f'refdoi2bib "{res["identifier"]}"').read()
        elif res['identifier_type'] == 'arxiv ID':
            print("Start arxiv2bib")
            s = os.popen(f'arxiv2bib "{res["identifier"]}"').read()
        s = s.strip()
        if s is None or s == '':
            self.info_dict = self.basic_dict()
            return False
        x = bibtexparser.loads(s)
        if len(x.entries) == 0:
            self.info_dict = self.basic_dict()
            return False
        self.info_dict = x.entries[0]
        self.info_dict['path'] = self.pdf_file
        if 'abstract' in self.info_dict:
            del self.info_dict['abstract']
        self.fixID()
        return True

    def refetch(self):
        if 'doi' in self.info_dict:
            s = os.popen(f'refdoi2bib "{self.info_dict["doi"]}"').read()
            s = s.strip()
            if s is None or s == '':
                return False
            x = bibtexparser.loads(s).entries[0]
            n_updated = 0
            updated_names = False
            for k in x.keys():
                if k == "ID":
                    continue
                if k in self.info_dict.keys():
                    if not self.info_dict[k] == x[k]:
                        print(f"  UPD {k}:\t '{self.info_dict[k]}' -> '{x[k]}'")
                        self.info_dict[k] = x[k]
                        n_updated+=1
                        if k == "author" or k == "year":
                            updated_names = True
                else:
                    if k != "abstract":
                        print(f"  NEW {k}:\t '{x[k]}'")
                        self.info_dict[k] = x[k]
                        n_updated+=1
            if updated_names:
                self.fixID()
            return updated_names

    def fixID(self):
        if not 'author' in self.info_dict or not 'year' in self.info_dict:
            return
        astr = self.info_dict['author']
        name = re.search(r'\s([^\s]+)(\sand|$)', astr).groups()[0]
        key = name + self.info_dict['year']
        self.info_dict["ID"] = key


    def get(self, s):
        return self.info_dict.get(s)

    def get_dict(self):
        return self.info_dict

    def rename_pdf(self):
        if not self.info_dict:
            return None
        new_file = os.path.join(os.path.dirname(self.pdf_file),
                                self.info_dict['ID'] + '.pdf')
        if new_file == self.pdf_file:
            return None
        else:
            self.pdf_file = new_file
            self.info_dict['path'] = self.pdf_file
            return self.pdf_file

    def handle_changes(self, changes):
        for k, (vn, vo) in changes.items():
            if vo is None:
                print('None ->', vn)
            else:
                print(self.info_dict[k], '->', vn)
            if k != 'path':
                if vn is None:
                    del self.info_dict[k]
                else:
                    self.info_dict[k] = vn
        if 'todo' in self.info_dict:
            failed = False
            if 'doi' in self.info_dict:
                s = os.popen(f'refdoi2bib "{self.info_dict["doi"]}"').read()
                if s == '':
                    del self.info_dict['doi']
                    failed = True
                else:
                    x = bibtexparser.loads(s)
                    self.info_dict = x.entries[0]
            elif 'arxiv' in self.info_dict:
                s = os.popen(f'refdoi2bib "{self.info_dict["arxiv"]}"').read()
                if s == '':
                    del self.info_dict['arxiv']
                    failed = True
                else:
                    x = bibtexparser.loads(s)
                    self.info_dict = x.entries[0]
            elif 'ISBN' in self.info_dict:
                pass
            else:
                failed = True
            if not failed:
                self.info_dict['path'] = self.pdf_file
                if 'todo' in self.info_dict:
                    del self.info_dict['todo']
        self.fixID()
        print(self.info_dict['path'])
        return True
