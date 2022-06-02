from transactions.models.review import Review
from django.db.models import Q


def getReviewsByUser(user):
    condition1 = Q(user=user)
    condition2 = Q(deleted_by=None)
    return Review.objects.filter(condition1 & condition2)