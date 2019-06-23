from django.core.cache import cache
from django.test import TestCase
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
from rest_framework.test import APIClient as Client


class GetBackendsAnonymousTest(TestCase):
    fixtures = ['ad_mediation_data.json', ]
    client = Client()

    def setUp(self):
        cache.clear()

    def test_retrieve_active_backends(self):
        resp = self.client.get('/mediation/backends/')
        self.assertEqual(len(resp.data), 2)

    def test_retrieve_all_backends(self):
        resp = self.client.get('/mediation/backends/show_all/')
        self.assertEqual(len(resp.data), 3)

    def test_update_backends(self):
        resp = self.client.get('/mediation/backends/1/')
        self.assertEqual(resp.data['name'], "Backend 1")
        resp = self.client.post('/mediation/backends/', {})
        self.assertEqual(resp.status_code, HTTP_401_UNAUTHORIZED)
        resp = self.client.put('/mediation/backends/', {})
        self.assertEqual(resp.status_code, HTTP_401_UNAUTHORIZED)


class BulkUpdateBackendsTest(TestCase):
    fixtures = ['user_data.json', 'ad_mediation_data.json']
    client = Client()
    client_anon = Client()

    def setUp(self):
        cache.clear()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.login_user()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    @classmethod
    def login_user(cls):
        resp = cls.client.post('/api-token-auth/', data={"username": "admin", "password": "admin"})
        cls.client.credentials(HTTP_AUTHORIZATION='Token ' + resp.data["token"])

    def test_bulk_activation_wrong_input(self):
        BulkUpdateBackendsTest.setUpTestData()
        client = BulkUpdateBackendsTest.client
        resp = client.post('/mediation/backends/bulk_activate/', {})
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)
        resp = client.post('/mediation/backends/bulk_activate/', {'id_list': '1'})
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)
        resp = client.post('/mediation/backends/bulk_activate/', {'id_list': 'ABC'})
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)
        resp = client.post('/mediation/backends/bulk_activate/', {'id_list': '[1, "a"]'})
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_bulk_activation(self):
        client = BulkUpdateBackendsTest.client
        resp = client.get('/mediation/backends/')
        self.assertEqual(len(resp.data), 2)
        resp = self.client_anon.get('/mediation/backends/')
        self.assertEqual(len(resp.data), 2)
        self.assertEqual(resp.data[0]['id'], 1)
        self.assertEqual(resp.data[1]['id'], 2)

        # activate 2 & 3 instead of 1 & 2
        client.post('/mediation/backends/bulk_activate/', {'id_list': '[3, 2]'})
        resp = client.get('/mediation/backends/')
        self.assertEqual(len(resp.data), 2)
        resp = self.client_anon.get('/mediation/backends/')
        self.assertEqual(len(resp.data), 2)
        self.assertEqual(resp.data[0]['id'], 3)
        self.assertEqual(resp.data[1]['id'], 2)

        # activate backends that do not exist (will disable all other backends; this is a documented behaviour.)
        client.post('/mediation/backends/bulk_activate/', {'id_list': '[4, 5]'})
        resp = client.get('/mediation/backends/')
        self.assertEqual(len(resp.data), 0)

    def test_bulk_activation_options(self):
        resp = self.client.options('/mediation/backends/bulk_activate/')
        self.assertEqual(resp.data['actions']['POST']['id_list']['type'], 'list<int>')

    def test_single_activation(self):
        client = BulkUpdateBackendsTest.client
        resp = self.client_anon.get('/mediation/backends/')
        self.assertEqual(len(resp.data), 2)
        self.assertEqual(resp.data[0]['id'], 1)
        self.assertEqual(resp.data[1]['id'], 2)

        client.patch('/mediation/backends/1/', {'is_active': 'false'})
        resp = self.client_anon.get('/mediation/backends/')
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['id'], 2)
