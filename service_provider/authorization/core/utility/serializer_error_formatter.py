import system_returns_code



def serializerErrorFormatter(serializer):
    error = []
    for key, value in serializer.errors.items():
        error.append(value[0])
    content = {'statusCode': system_returns_code.BAD_REQUEST,
               'exceptionString': error,
               'data': {}}
    return content


def serializerListErrorFormatter(serializer):
    error = []
    for obj in serializer.errors:
        for key, value in obj.items():
            error.append(value[0])
    content = {'statusCode': system_returns_code.BAD_REQUEST,
            'exceptionString': error,
            'data': {}}
    return content
