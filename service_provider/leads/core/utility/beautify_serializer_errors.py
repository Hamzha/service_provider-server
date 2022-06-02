def beautify_serializer_errors(serializerErrors):
    error = []
    for key, value in serializerErrors.items():
        newValue=value[0].replace("This Field", key)
        newValue=value[0].replace("this field", key)
        error.append(newValue)
    return error
