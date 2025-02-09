import toml


class Config:
    def __init__(self, path: str = "config.toml"):
        self.config_path = f"./config/{path}"
        self.config = self.load_config()

    def load_config(self):
        try:
            return toml.load(self.config_path)
        except FileNotFoundError as ex:
            print(f"Config file <{self.config_path}> not found: {ex}")
        except (TypeError, toml.TomlDecodeError) as ex:
            print(f"Config file is invalid: {ex}")

    def get_section(self, section):
        if section in self.config:
            return ConfigSection(self.config[section])
        else:
            raise KeyError(
                f"Section '{section}' not found in config '{self.config_path}'."
            )


class ConfigSection:
    def __init__(self, values: dict):
        for key, value in values.items():
            setattr(self, key, value)
