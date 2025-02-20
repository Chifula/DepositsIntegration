import json

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.translation import gettext_lazy as _

def format_request_data(request_data):
    """ Format request data to a list """

    # Convert the string to a list using json.loads()
    result_list = json.loads(request_data)

    # Use list comprehension to remove commas and quotes
    whitespace_list = [item.strip('",') for item in result_list]
    new_list = [item.strip() for item in whitespace_list]

    return new_list
class CustomPaginator(Paginator):
    """ Custom paginator class that overrides validate_number function """

    def validate_number(self, number):
        """Validate the given 1-based page number."""
        try:
            if isinstance(number, float) and not number.is_integer():
                raise ValueError
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger(_("That page number is not an integer"))
        if number < 0:  # Override this line to allow when page number is equal to 1
            raise EmptyPage(_("That page number is less than 1"))
        if number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                pass
            else:
                raise EmptyPage(_("That page contains no results"))
        return number