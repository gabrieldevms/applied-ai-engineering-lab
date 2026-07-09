from dataclasses import dataclass


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int = 2

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be greater than or equal to 1")
