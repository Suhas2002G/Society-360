from myapp.models import Amenity, BookingAmenity
import logging

# Configure logger
logger = logging.getLogger(__name__)


class AmenityService():
    '''Service layer for Amenity-related business logic'''

    @staticmethod
    def create_amenity(amenity_name, description, rent, img):
        """
        Create and return a new Amenity instance.
        """
        logger.info("Creating amenity: %s", amenity_name)
        try:
            amenity = Amenity.objects.create(
                amenity=amenity_name,
                des=description,   # assuming model field is `des`
                rent=rent,
                img=img,
            )
            logger.debug("Amenity created with id=%s", amenity.id)
            return amenity
        except Exception:
            logger.exception("Failed to create amenity.")
            raise


    @staticmethod
    def list_amenities():
        """
        Return a queryset of all amenities.
        """
        logger.debug("Fetching all amenities.")
        return Amenity.objects.all()
    

    @staticmethod
    def get_amenity(aid):
        """
        Return a single amenity by id.
        """
        logger.debug("Fetching amenity with id=%s", aid)
        return Amenity.objects.get(id=aid)
    

    @staticmethod
    def delete_amenity(aid):
        """
        Delete an amenity by id and return number of deleted records.
        """
        logger.info("Deleting amenity with id=%s", aid)
        deleted_count, _ = Amenity.objects.filter(id=aid).delete()
        if deleted_count == 0:
            logger.warning("No amenity found to delete with id=%s", aid)
        else:
            logger.debug("Deleted %s amenity(ies) with id=%s", deleted_count, aid)
        return deleted_count
    

    @staticmethod
    def update_amenity(aid, amenity_name=None, description=None, rent=None, img=None):
        """
        Update an amenity and return the updated instance.
        """
        logger.info("Updating amenity with id=%s", aid)
        amenity = AmenityService.get_amenity(aid)

        if amenity_name is not None:
            amenity.amenity = amenity_name
        if description is not None:
            amenity.des = description   
        if rent is not None:
            amenity.rent = rent
        if img is not None:
            amenity.img = img

        amenity.save()
        logger.debug("Amenity with id=%s updated successfully.", aid)
        return amenity

    @staticmethod
    def list_bookings():
        """
        Return a queryset of all amenity bookings ordered by booking_date desc.
        """
        logger.debug("Fetching all amenity bookings.")
        return BookingAmenity.objects.all().order_by('-booking_date')