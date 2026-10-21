"""
Authentication API testləri
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def _create(username='testuser', password='StrongPass123!', role='operator', **kwargs):
        return User.objects.create_user(
            username=username,
            password=password,
            email=f'{username}@test.com',
            role=role,
            **kwargs
        )
    return _create


@pytest.fixture
def auth_client(api_client, create_user):
    user = create_user()
    url = reverse('login')
    resp = api_client.post(url, {'username': 'testuser', 'password': 'StrongPass123!'})
    token = resp.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client, user


class TestRegistration:
    def test_register_success(self, api_client, db):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'Test',
            'role': 'operator',
        }
        resp = api_client.post(url, data)
        assert resp.status_code == status.HTTP_201_CREATED
        assert 'tokens' in resp.data
        assert 'access' in resp.data['tokens']
        assert User.objects.filter(username='newuser').exists()

    def test_register_password_mismatch(self, api_client, db):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'StrongPass123!',
            'password2': 'WrongPass456!',
            'first_name': 'Test',
        }
        resp = api_client.post(url, data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_username(self, api_client, create_user, db):
        create_user(username='duplicate')
        url = reverse('register')
        data = {
            'username': 'duplicate',
            'email': 'dup@test.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'Dup',
        }
        resp = api_client.post(url, data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


class TestLogin:
    def test_login_success(self, api_client, create_user, db):
        create_user()
        url = reverse('login')
        resp = api_client.post(url, {'username': 'testuser', 'password': 'StrongPass123!'})
        assert resp.status_code == status.HTTP_200_OK
        assert 'access' in resp.data
        assert 'refresh' in resp.data

    def test_login_wrong_password(self, api_client, create_user, db):
        create_user()
        url = reverse('login')
        resp = api_client.post(url, {'username': 'testuser', 'password': 'WrongPassword!'})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client, db):
        url = reverse('login')
        resp = api_client.post(url, {'username': 'ghost', 'password': 'any'})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestProfile:
    def test_get_profile_authenticated(self, auth_client, db):
        client, user = auth_client
        url = reverse('profile')
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['username'] == user.username
        assert resp.data['role'] == user.role

    def test_get_profile_unauthenticated(self, api_client, db):
        url = reverse('profile')
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, auth_client, db):
        client, user = auth_client
        url = reverse('profile')
        resp = client.patch(url, {'first_name': 'Updated', 'phone': '+994501234567'})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['first_name'] == 'Updated'
        assert resp.data['phone'] == '+994501234567'
