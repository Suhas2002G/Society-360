from typing import Iterable
from django.db.models import QuerySet
from django.contrib.auth.models import User
from myapp.models import Complaint, Notice


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
    


    @staticmethod
    def create_complaint(title: str, category: str, description: str, user: User) -> Complaint:
        """
        Create and save a new complaint.

        Args:
            title (str): Complaint title.
            category (str): Complaint category.
            description (str): Detailed description of the complaint.
            user (User): Django `User` instance submitting the complaint.

        Returns:
            Complaint: The newly created Complaint object.

        Raises:
            ValueError: If required fields are missing.
            Exception: For unexpected database errors.
        """
        if not title or not category or not description:
            raise ValueError("All fields are required to create a complaint.")

        complaint = Complaint.objects.create(
            title=title,
            category=category,
            description=description,
            uid=user
        )
        return complaint


