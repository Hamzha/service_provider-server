from authorization.models.document import Document
from leads.models.service import Service


def saveDocuemnt(url, type, format, service):
    Document.objects.create(
        url=url, type=type, format=format, service=service
    )


def getEnumFromDocuemntType(type):
    return Document.DocumentType[str(type).upper()]


def getDocumentTypeFromEnum(type):
    return Document.DocumentType(type).name


def getEnumFromDocuemntFormat(format):
    return Document.DocumentFormat[str(format).upper()]


def getDocumentFormatFromEnum(format):
    return Document.DocumentFormat(format).name


def getServiceFromID(service_ID):
    return Service.objects.filter(id=service_ID).first()
