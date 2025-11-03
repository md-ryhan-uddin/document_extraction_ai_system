"""
Cancellation manager for document processing.
Allows cancelling long-running document processing operations.
"""
import threading
import logging

logger = logging.getLogger(__name__)


class CancellationManager:
    """
    Thread-safe manager for tracking document processing cancellations.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._cancelled_docs = set()
                    cls._instance._cancel_lock = threading.Lock()
        return cls._instance

    def request_cancellation(self, document_id: int):
        """
        Request cancellation of document processing.

        Args:
            document_id: ID of the document to cancel
        """
        with self._cancel_lock:
            self._cancelled_docs.add(document_id)
            print(f"[CANCELLATION_MANAGER] Added {document_id} to cancelled set. Set is now: {self._cancelled_docs}")
            logger.info(f"Cancellation requested for document {document_id}")

    def is_cancelled(self, document_id: int) -> bool:
        """
        Check if cancellation has been requested for a document.

        Args:
            document_id: ID of the document to check

        Returns:
            bool: True if cancellation was requested
        """
        with self._cancel_lock:
            result = document_id in self._cancelled_docs
            print(f"[CANCELLATION_MANAGER] Checking if {document_id} is cancelled. Set: {self._cancelled_docs}, Result: {result}")
            return result

    def clear_cancellation(self, document_id: int):
        """
        Clear cancellation status for a document.

        Args:
            document_id: ID of the document
        """
        with self._cancel_lock:
            self._cancelled_docs.discard(document_id)
            print(f"[CANCELLATION_MANAGER] Cleared {document_id} from cancelled set. Set is now: {self._cancelled_docs}")
            logger.info(f"Cancellation cleared for document {document_id}")

    def reset(self):
        """Clear all cancellation requests."""
        with self._cancel_lock:
            self._cancelled_docs.clear()


# Singleton instance
cancellation_manager = CancellationManager()
