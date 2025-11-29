from myapp.models import Notice


class NoticeSection:
    """
    Service layer responsible for retrieving Notice objects.
    """

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


    