import fs
import fs.path
import fs.errors
from jinja2 import BaseLoader, TemplateNotFound


class FSLoader(BaseLoader):

    def __init__(self, template_fs, encoding='utf-8', use_syspath=False, fs_filter=None):
        self.filesystem = fs.open_fs(template_fs)
        self.use_syspath = use_syspath
        self.encoding = encoding
        self.fs_filter = fs_filter

    def get_source(self, environment, template):
        if not self.filesystem.isfile(template):
            raise TemplateNotFound(template)
        reload = lambda: False
        try:
            with self.filesystem.open(template, encoding=self.encoding) as input_file:
                source = input_file.read()
            if self.use_syspath:
                if self.filesystem.hassyspath(template):
                    return source, self.filesystem.getsyspath(template), reload
                elif self.filesystem.hasurl(template):
                    return source, self.filesystem.geturl(template), reload
            return source, template, reload
        except OSError:
            raise TemplateNotFound(template)

    def list_templates(self):
        found = set()
        for file in self.filesystem.walk.files(filter=self.fs_filter):
            found.add(fs.path.relpath(file))
        return sorted(found)
