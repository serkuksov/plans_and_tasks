from rest_framework import serializers

from accounts.models import UserDeteil


class UserDeteilSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    division = serializers.StringRelatedField()

    def get_full_name(self, userdetail):
        return f'{userdetail.user.last_name} {userdetail.user.first_name} {userdetail.second_name}'

    def get_email(self, userdetail):
        return userdetail.user.email

    class Meta:
        model = UserDeteil
        fields = (
            'id',
            'user',
            'full_name',
            'email',
            'phone_number',
            'is_manager',
            'division',
        )
