from rest_framework import serializers
from leads.models.service_category import ServiceCategory


class ServiceCategorySerlizer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    subCategory = serializers.SerializerMethodField()

    class Meta:
        model = ServiceCategory
        fields = ['id', 'subCategory', 'category']

    def get_category(self, object):
        if object.parent_id:
            object.category = ServiceCategory.objects.filter(
                id=object.parent_id.id).first().name
            return object.category
        else:
            return ""

    def get_subCategory(self, object):
        return object.name
