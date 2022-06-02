from authorization.models.configuration import Configuration


def delete_configuration(consfiguration_id, userId):
    try:
        Configuration.objects.get(
            pk=consfiguration_id,
            deleted_by=None).delete(userId)
        return True
    except Configuration.DoesNotExist:
        return False
