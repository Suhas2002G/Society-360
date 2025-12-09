from myapp.models import Notice


class NoticeSection:
    """
    Service layer responsible for retrieving Notice objects.
    """

    @staticmethod
    def create_notice(title: str, category: str, description: str, priority: str = 'None') -> Notice:
        """
        Create a new notice and save it in the database.
        """
        notice = Notice.objects.create(
            title=title,
            category=category,
            des=description,
            priority=priority,
        )
        return notice
    

    @staticmethod
    def fetch_latest_notices(limit=None):
        """
        Provide latest nth notices
        """
        if limit:
            notices = Notice.objects.order_by('-created_at')[:limit]
        else:
            notices = Notice.objects.order_by('-created_at')
        return notices 


    
    @staticmethod
    def delete_notice_by_id(notice_id: int) -> int:
        """
        Delete a notice by its primary key.

        Args:
            notice_id (int): ID of the notice to delete.

        Returns:
            int: Number of Notice objects deleted (0 if none found, 1 if deleted).
        """
        deleted_count, _ = Notice.objects.filter(id=notice_id).delete()
        return deleted_count