from leads.models.rating import Rating


def create_rating(validated_data):
    rating = Rating(**validated_data)
    rating.save()
    return rating


def delete_rating(rating_id, user_id):
    try:
        Rating.objects.get(
            id=rating_id,
            deleted_by=None,
            created_by=user_id).delete(user_id)
        return True
    except Rating.DoesNotExist:
        return False
