from dataclasses import dataclass


@dataclass(frozen=True)
class MetaConfig:
    """
    Immutable metadata configuration for test context.

    Stores static information about who or what is executing the tests.
    Useful for Allure report metadata like executor name, build info, etc.
    """

    test_executor: str

    @classmethod
    def load_config(cls) -> "MetaConfig":
        """
        Load test metadata configuration.

        Returns:
            MetaConfig: An object containing test executor info.
        """
        test_executor = "Jacky"
        return cls(test_executor)


# global singleton
META_CONFIG = MetaConfig.load_config()