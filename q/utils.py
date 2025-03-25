from django.utils.timezone import now
from django.utils import timezone

def check_quiz_status(start_time, end_time):
    """
    Checks if the quiz is active, upcoming, or expired based on the current time.

    Returns:
        - "active" if the quiz is currently running.
        - "upcoming" if the quiz has not started yet.
        - "expired" if the quiz has ended.
    """
    current_time = now()

    print("Current time: ", current_time)

    current_time = timezone.localtime(current_time)

    print("Current time: ", current_time)

    if start_time is None:
        # If start_time is None, consider the quiz as started
        if end_time is None:
            # If both start_time and end_time are None, the quiz is available
            return "active"
        elif end_time > current_time:
            return "active"
        else:
            return "expired"

    if start_time > current_time:
        return "upcoming"
    elif start_time <= current_time <= end_time:
        return "active"
    else:
        return "expired"
