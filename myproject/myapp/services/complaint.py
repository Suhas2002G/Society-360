from typing import Iterable
from django.db.models import QuerySet
from myapp.models import Complaint


class ComplaintService:
    """
    Service layer responsible for business logic related to Complaint objects.
    """

    @staticmethod
    def fetch_complaints(user_id: int) -> QuerySet[Complaint]:
        """
        Retrieve all complaints filed by a specific user, ordered from latest to oldest.

        Args:
            user_id (int): The ID of the user whose complaints should be fetched.

        Returns:
            QuerySet[Complaint]: A queryset of Complaint objects filtered by the given user,
                                 ordered by creation timestamp (descending).
        """
        return Complaint.objects.filter(uid=user_id).order_by("-created_at")