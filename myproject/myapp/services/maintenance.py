from myapp.models import MaintenancePayment
import logging
from datetime import datetime
# Initialize logger for this module
logger = logging.getLogger(__name__)


class MaintenanceService():
    
    @staticmethod
    def fetch_maintenance_records():
        """
        Fetch all maintenance payment records ordered by latest entries.

        Returns : QuerySet | None
            A list of ordered maintenance payment objects, or None if an error occurs.
        """
        try:
            return MaintenancePayment.objects.all().order_by('-payment_date')
        except Exception as e:
            logger.warning(f"Failed to fetch maintenance records: {e}")
            return None
        
    
    @staticmethod
    def filter_maintenance_records(flatno: str = "", ownername: str = "", start_date: str = "", end_date: str = ""):
        """
        Filter maintenance payment records using optional filter criteria.

        Parameters
        ----------
        flatno : str, optional
            Filter by flat number (partial match allowed).
        ownername : str, optional
            Filter by owner's first name (partial match allowed).
        start_date : str, optional
            Filter records with payment_date >= start_date (expected format: YYYY-MM-DD).
        end_date : str, optional
            Filter records with payment_date <= end_date (expected format: YYYY-MM-DD).

        Returns: QuerySet
            Filtered maintenance payment records ordered by latest payment date.
        """

        queryset = MaintenancePayment.objects.all()

        if flatno:
            queryset = queryset.filter(fid__flat_no__icontains=flatno)

        if ownername:
            queryset = queryset.filter(uid__first_name__icontains=ownername)

        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(payment_date__gte=start_date_obj)
            except ValueError:
                logger.warning("Invalid start_date format received.")

        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
                queryset = queryset.filter(payment_date__lte=end_date_obj)
            except ValueError:
                logger.warning("Invalid end_date format received.")

        return queryset.order_by('-payment_date')