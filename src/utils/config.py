import toml


class Config:
    def __init__(self, path: str):
        try:
            self.config = toml.load(path)
        except FileNotFoundError as ex:
            print(f"Config file <{path}> not found: {ex}")
        except (TypeError, toml.TomlDecodeError) as ex:
            print(f"Config file is invalid: {ex}")

        for key in self.config:
            setattr(self, key, self.config[key])
