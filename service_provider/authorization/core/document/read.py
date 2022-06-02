from authorization.models.document import Document
from leads.models.service import Service
from django.db.models import Q


def getDocumentByService(service):
    condition1 = Q(service=service)
    condition2 = Q(deleted_by__isnull=True)
    return Document.objects.filter(condition1 and condition2)


def getDocumentByUser(id):
    condition1 = Q(user=id)
    condition2 = Q(deleted_by__isnull=True)
    return Document.objects.filter(condition1 and condition2)


def getDocumentTypeToEnum(type):
    return Document.DocumentType[str(type).upper()]


def getDocumentFormatToEnum(format):
    return Document.DocumentFormat[str(format).upper()]


def getDocuentFormatFromEnum(format):
    return Document.DocumentFormat(format).name


def getDocuentTypeFromEnum(type):
    return Document.DocumentType(type).name


def getDocumentByID(document_id):
    condition1 = Q(id=document_id)
    condition2 = Q(deleted_by__isnull=True)
    return Document.objects.filter(condition1 & condition2)
