from enum import Enum


class SessionDeletionRequestStatus(str, Enum):
    PENDING = "pending"

    PROCESSING = "processing"

    COMPLETED = "completed"

    FAILED = "failed"

    PARTIALLY_FAILED = "partially_failed"
