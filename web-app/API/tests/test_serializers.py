from API.serializers import UserDeteilSerializer
from API.tests.test_view import ViewBaseTestCase
from accounts.models import UserDeteil


class SerializersTestCase(ViewBaseTestCase):
    """Тестирование сериализаторов"""
    def test_user_detail_serializer(self):
        queryset = UserDeteil.objects.all()
        serializer_data = UserDeteilSerializer(queryset, many=True).data

        self.assertEqual(serializer_data[0]['id'], self.user_1.userdeteil.id)
        self.assertEqual(serializer_data[0]['user'], str(self.user_1))
        self.assertEqual(serializer_data[0]['full_name'], 'b  second_name')
        self.assertEqual(serializer_data[0]['email'], self.user_1.email)
        self.assertEqual(serializer_data[0]['phone_number'], self.user_1.userdeteil.phone_number)
        self.assertFalse(serializer_data[0]['is_manager'])
        self.assertEqual(serializer_data[0]['division'], self.user_1.userdeteil.division.name)

        self.assertEqual(serializer_data[1]['id'], self.user_2.userdeteil.id)
        self.assertEqual(serializer_data[1]['user'], str(self.user_2))
        self.assertEqual(serializer_data[1]['full_name'], 'a  second_name_2')
        self.assertEqual(serializer_data[1]['email'], self.user_2.email)
        self.assertEqual(serializer_data[1]['phone_number'], self.user_2.userdeteil.phone_number)
        self.assertTrue(serializer_data[1]['is_manager'])
        self.assertEqual(serializer_data[1]['division'], self.user_2.userdeteil.division.name)
