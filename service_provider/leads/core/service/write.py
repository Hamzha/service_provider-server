from leads.models.service import Service


def delete_service(service_id, user_id):
    try:
        Service.delete(Service.objects.filter(id=service_id).first(), user_id)
        return True
    except:
        return False


def update_service(params, service_id):
    try:
        Service.objects.filter(id=service_id).update(**params)
        return True
    except:
        return False
