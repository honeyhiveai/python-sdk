from enum import Enum


class UpdateConfigurationRequestEnvItem(str, Enum):
    DEV = "dev"
    PROD = "prod"
    STAGING = "staging"

    def __str__(self) -> str:
        return str(self.value)
