from enum import Enum


class CreateConfigurationRequestEnvItem(str, Enum):
    DEV = "dev"
    PROD = "prod"
    STAGING = "staging"

    def __str__(self) -> str:
        return str(self.value)
