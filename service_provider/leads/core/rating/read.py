from leads.models.rating import Rating
from django.db.models import Q
from leads.models.lead import Lead

# Get rating for specific job_id
def get_all_ratings_by_job_id(job_id):
    return Rating.objects.filter(deleted_by=None, job__id=job_id)

# Get all reating that is created by the user
def get_all_ratings_by_user_id(user_id):
    ratings_queryset = Rating.objects.filter(
        created_by=user_id, deleted_by=None)
    return ratings_queryset

# Get specific rating that is created by the user
def get_rating(rating_id, user_id):
    try:
        rating = Rating.objects.get(
            id=rating_id,
            deleted_by=None,
            created_by=user_id)
        return rating
    except Rating.DoesNotExist:
        return False

# Get specific rating
def get_rating(rating_id):
    try:
        rating = Rating.objects.get(
            id=rating_id,
            deleted_by=None,)
        return rating
    except Rating.DoesNotExist:
        return False

# Get rating given to the user
def get_all_rating_against_user(user_id):
    ratings_queryset = Rating.objects.filter(
        user=user_id, deleted_by=None)
    return ratings_queryset

# Get average rating of particular user
def get_average_rating(user_id):
    ratings = get_all_rating_against_user(user_id)
    number_of_rating = len(ratings)
    if number_of_rating == 0:
        return 0
    total_rating = 0
    for rating in ratings:
        average_rating = (rating.reliability+rating.courtesy +
                          rating.professionalism+rating.job_performance)/4
        total_rating = total_rating+average_rating
    return total_rating/number_of_rating

# Get average rating of particular user with total rating and no_of_review
def get_average_rating_and_no_of_review(user_id):
    ratings = get_all_rating_against_user(user_id)
    number_of_rating = len(ratings)
    if number_of_rating == 0:
        return {'total_rating': 0, 'no_of_reviews': 0}
    total_rating = 0
    for rating in ratings:
        average_rating = (rating.reliability+rating.courtesy +
                          rating.professionalism+rating.job_performance)/4
        total_rating = total_rating+average_rating
    return {'total_rating': total_rating/number_of_rating, 'no_of_reviews': number_of_rating}

def get_new_user_rating(prev_rating,prev_no_of_review,new_rating):
    prev_total_rating=prev_rating*prev_no_of_review
    average_new_rating = (new_rating.reliability+new_rating.courtesy +
                          new_rating.professionalism+new_rating.job_performance)/4
    new_total_rating=(prev_total_rating + average_new_rating)/(prev_no_of_review+1)
    return new_total_rating
    
