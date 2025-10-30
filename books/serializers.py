from rest_framework import serilizers


class BookSerializer(serilizers.ModelSerializer):
    class Meta:
        fields = '__all__'