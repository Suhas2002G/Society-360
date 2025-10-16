


from myapp.models import Notice


class NoticeSection:
    def __init__(self):
        pass 


    @staticmethod
    def fetch_latest_notices(self, limit):
        """
        Provide latest nth notices
        """
        try:
            notices = Notice.objects.order_by('-created_at')[:limit]
            return notices 
        except:
            pass

    