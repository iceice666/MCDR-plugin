

from mcdreforged.minecraft.rtext import RTextBase


class metadata:
    PLUGIN_METADATA = {}

    def __init__(self,
                 id="my_plugin",
                 author="Myself",
                 version="1.0.0",
                 link="",
                 name: str or RTextBase = "My Plugin",
                 prefix="prefix",
                 description: str or RTextBase = "A MCDR plugin",
                 dependencies: dict = {}
                 ):

        self.PLUGIN_METADATA = {}
        self.PLUGIN_METADATA["id"] = id
        self.PLUGIN_METADATA["author"] = author
        self.PLUGIN_METADATA["link"]=link
        self.PLUGIN_METADATA["version"] = version
        self.PLUGIN_METADATA["name"] = name
        self.PLUGIN_METADATA["prefix"] = prefix
        self.PLUGIN_METADATA["description"] = description
        self.PLUGIN_METADATA["dependencies"] = dependencies

    def set_value(self, key, value):
        self.PLUGIN_METADATA[key] = value

    def get_value(self, key):
        return self.PLUGIN_METADATA[key]

    def get_settings(self):
        return {
            'id': self.PLUGIN_METADATA["id"],
            'version': self.PLUGIN_METADATA["version"],
            'name': self.PLUGIN_METADATA["name"],
            'description': self.PLUGIN_METADATA["description"],
            'author': self.PLUGIN_METADATA["author"],
            'link': self.PLUGIN_METADATA["link"],
            'dependencies': self.PLUGIN_METADATA["dependencies"]
        }

    def get_dict(self):
        return self.PLUGIN_METADATA


class help_msg:
    template = [""]

    def add_msg(self, msg:str):
        self.template.append(msg)

    def get_value(self):
        return "\n".join(self.template)


class info_msg:
    template = [""]

    def add_msg(self, msg):
        self.template.append(msg)

    def get_value(self):
        return "\n".join(self.template)
