from django.contrib.auth.models import User
from django.urls import reverse
from pytest_drf import APIViewTest, AsUser, Returns200, UsesGetMethod
from pytest_lambda import lambda_fixture

alice = lambda_fixture(
    lambda: User.objects.create(
        username='alice',
        first_name='Alice',
        last_name='Innchains',
        email='alice@ali.ce',
    ))

class TestAboutMe(
    APIViewTest,
    UsesGetMethod,
    Returns200,
    AsUser('alice'),
):
    url = lambda_fixture(lambda: reverse('about-me'))

    def test_it_returns_profile(self, json):
        expected = {
            'username': 'alice',
            'first_name': 'Alice',
            'last_name': 'Innchains',
            'email': 'alice@ali.ce',
        }
        actual = json
        assert expected == actual
