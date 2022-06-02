from authorization.models.configuration import Configuration

def get_configuration(configuration_id):
    try:
        configuration = Configuration.objects.get(
            pk=configuration_id, deleted_by=None)
        return configuration
    except Configuration.DoesNotExist:
        return False

def get_all_configuration():
    return Configuration.objects.filter(deleted_by=None)
