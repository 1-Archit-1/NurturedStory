from django.test import TestCase


class SmokeTest(TestCase):
    def test_home_page_loads(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
