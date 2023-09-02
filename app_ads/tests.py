from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from app_users.models import CustomUser


class BaseTestCase(APITestCase):
    """
    Базовые настройки тест-кейса.
    Создание пользователей.
    Создание клиента для каждого пользователя.
    Аутентификация пользователей.
    """

    USERS_DATA = [
        {"email": "ivan@mail.ru", "password": "qwerty123!"},
        {"email": "max@mail.ru", "password": "qwerty123!"},
    ]

    URL = "/api/ads/"

    ADS_DATA = [
        {"title": "Продам ноутбук", "price": 50000, "description": "Хороший ноутбук"},
        {
            "title": "Продам машину",
            "price": 300000,
            "description": "Отличное состояние",
        },
    ]

    @staticmethod
    def create_authenticated_client(user_data):
        client = APIClient()
        login = client.post(
            "/api/token/",
            {"email": user_data["email"], "password": user_data["password"]},
        )
        access_token = login.json().get("access")
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        return client

    def setUp(self):
        self.user_1 = CustomUser.objects.create_user(
            email="ivan@mail.ru",
            password="qwerty123!",
            first_name="Ivan",
            last_name="Ivanov",
            phone="+7(921)123-45-67",
            role="user",
        )
        self.user_2 = CustomUser.objects.create_user(
            email="max@mail.ru",
            password="qwerty123!",
            first_name="Max",
            last_name="Maximov",
            phone="+7(921)890-12-34",
            role="admin",
        )
        self.user_clients = []
        for user_data in self.USERS_DATA:
            client = self.create_authenticated_client(user_data)
            self.user_clients.append(client)


class AdCreateAPITestCase(BaseTestCase):
    """Создание объявления"""

    def test_unauthorized_user_cannot_create_ad(self):
        """Неавторизованный пользователь не может создать привычку"""
        data = {
            "title": "Продам ноутбук",
            "price": "50000",
            "description": "Хороший ноутбук",
        }
        client = APIClient()
        response = client.post(self.URL, data)
        response_data = response.json()

        self.assertEqual(
            response_data.get("detail"), "Учетные данные не были предоставлены."
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_success_create_ad(self):
        """Успешное создание объявлений обычным пользователем и админом"""
        for i, client in enumerate(self.user_clients):
            ad_data = self.ADS_DATA[i]
            response = client.post(self.URL, ad_data)
            response_data = response.json()

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(response_data.get("pk"))
            self.assertEqual(response_data.get("title"), ad_data.get("title"))
            self.assertEqual(response_data.get("price"), ad_data.get("price"))
            self.assertEqual(
                response_data.get("description"), ad_data.get("description")
            )

        all_ads = APIClient().get(self.URL).json().get("results")
        self.assertEqual(len(all_ads), 2)


class AdReadAPITestCase(BaseTestCase):
    """Чтение объявления"""

    def setUp(self):
        super().setUp()

        self.ad_ids = []

        for i, client in enumerate(self.user_clients):
            ad_data = self.ADS_DATA[i]
            response = client.post(self.URL, ad_data)
            response_data = response.json()
            self.ad_ids.append(response_data.get("pk"))

    def test_admin_user_can_read_ads(self):
        """
        Админ и обычный пользователь видят свои объявления и объявления друг друга по ID.
        """

        for client in self.user_clients:
            for ad_id in self.ad_ids:
                response = client.get(f"{self.URL}{ad_id}/")
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                index = self.ad_ids.index(ad_id)
                original_ad_data = self.ADS_DATA[index]

                response_data = response.json()
                self.assertEqual(response_data.get("pk"), ad_id)
                self.assertEqual(
                    response_data.get("title"), original_ad_data.get("title")
                )
                self.assertEqual(
                    response_data.get("price"), original_ad_data.get("price")
                )
                self.assertEqual(
                    response_data.get("description"),
                    original_ad_data.get("description"),
                )

    def test_unauthorized_user_can_not_read_ads(self):
        """
        Неавторизованный пользователь не видит объявления по ID.
        """

        client = APIClient()
        for ad_id in self.ad_ids:
            response = client.get(f"{self.URL}{ad_id}/")
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_admin_can_read_list_of_ads(self):
        """
        Админ и обычный пользователь видят список всех объявлений.
        """

        for client in self.user_clients:
            response = client.get(self.URL)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response_data = response.json()
            results_from_response = response_data.get("results")

            ad_ids_from_response = [ad.get("pk") for ad in results_from_response]
            self.assertTrue(all(ad_id in ad_ids_from_response for ad_id in self.ad_ids))

            for ad in results_from_response:
                ad_id = ad.get("pk")

                index = self.ad_ids.index(ad_id)
                original_ad_data = self.ADS_DATA[index]

                self.assertEqual(ad.get("title"), original_ad_data.get("title"))
                self.assertEqual(ad.get("price"), original_ad_data.get("price"))
                self.assertEqual(
                    ad.get("description"), original_ad_data.get("description")
                )

    def test_unauthorized_user_can_read_of_list_ads(self):
        """
        Неавторизованный пользователь видит список объявлений.
        """

        client = APIClient()
        response = client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        results_from_response = response_data.get("results")

        ad_ids_from_response = [ad.get("pk") for ad in results_from_response]
        self.assertTrue(all(ad_id in ad_ids_from_response for ad_id in self.ad_ids))

        for ad in results_from_response:
            ad_id = ad.get("pk")

            index = self.ad_ids.index(ad_id)
            original_ad_data = self.ADS_DATA[index]

            self.assertEqual(ad.get("title"), original_ad_data.get("title"))
            self.assertEqual(ad.get("price"), original_ad_data.get("price"))
            self.assertEqual(ad.get("description"), original_ad_data.get("description"))

    def test_user_can_read_own_ads(self):
        """
        Авторизованные пользователи могут видеть свои объявления
        """

        for i, client in enumerate(self.user_clients):
            response = client.get(self.URL + "me/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response_data = response.json()
            results_from_response = response_data.get("results")

            own_ads = [self.ad_ids[i]]

            ad_ids_from_response = [ad.get("pk") for ad in results_from_response]
            self.assertTrue(all(ad_id in own_ads for ad_id in ad_ids_from_response))

            for ad in results_from_response:
                ad_id = ad.get("pk")

                index = self.ad_ids.index(ad_id)
                original_ad_data = self.ADS_DATA[index]

                self.assertEqual(ad.get("title"), original_ad_data.get("title"))
                self.assertEqual(ad.get("price"), original_ad_data.get("price"))
                self.assertEqual(
                    ad.get("description"), original_ad_data.get("description")
                )


class AdPartialUpdateAPITestCase(BaseTestCase):
    """Частичное обновление объявлений"""

    def setUp(self):
        super().setUp()

        self.ad_ids = []

        for i, client in enumerate(self.user_clients):
            ad_data = self.ADS_DATA[i]
            response = client.post(self.URL, ad_data)
            response_data = response.json()
            self.ad_ids.append(response_data.get("pk"))

    def test_unauthorized_user_cannot_update_ads(self):
        """Неавторизованный пользователь не может обновлять объявления"""

        client = APIClient()
        for ad_id in self.ad_ids:
            response = client.patch(f"{self.URL}{ad_id}/", {"title": "New title"})
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_update_own_ads(self):
        """Обычный пользователь может обновлять только свои объявления"""

        for i, client in enumerate(self.user_clients):
            ad_id = self.ad_ids[i]
            response = client.patch(f"{self.URL}{ad_id}/", {"title": "New title"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response_data = response.json()
            self.assertEqual(response_data.get("title"), "New title")

    def test_user_cannot_update_others_ads(self):
        """Обычный пользователь не может обновлять чужие объявления"""

        client = self.user_clients[0]
        ad_id = self.ad_ids[1]

        response = client.patch(f"{self.URL}{ad_id}/", {"title": "New title"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_all_ads(self):
        """Админ может обновлять все объявления"""

        admin_client = self.user_clients[1]

        for ad_id in self.ad_ids:
            response = admin_client.patch(f"{self.URL}{ad_id}/", {"title": "New title"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response_data = response.json()
            self.assertEqual(response_data.get("title"), "New title")


class AdDeleteAPITestCase(BaseTestCase):
    """Удаление объявлений"""

    def setUp(self):
        super().setUp()

        self.ad_ids = []

        for i, client in enumerate(self.user_clients):
            ad_data = self.ADS_DATA[i]
            response = client.post(self.URL, ad_data)
            response_data = response.json()
            self.ad_ids.append(response_data.get("pk"))

    def test_unauthorized_user_cannot_delete_ads(self):
        """Неавторизованный пользователь не может удалять объявления"""

        client = APIClient()
        for ad_id in self.ad_ids:
            response = client.delete(f"{self.URL}{ad_id}/")
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_delete_own_ads(self):
        """Обычный пользователь может удалять только свои объявления"""

        for i, client in enumerate(self.user_clients):
            ad_id = self.ad_ids[i]
            response = client.delete(f"{self.URL}{ad_id}/")
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = APIClient().get(f"{self.URL}")
        self.assertEqual(len(response.json()["results"]), 0)

    def test_user_cannot_delete_others_ads(self):
        """Обычный пользователь не может удалять чужие объявления"""

        client = self.user_clients[0]
        ad_id = self.ad_ids[1]

        response = client.delete(f"{self.URL}{ad_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_all_ads(self):
        """Админ может удалять все объявления"""

        admin_client = self.user_clients[1]

        for ad_id in self.ad_ids:
            response = admin_client.delete(f"{self.URL}{ad_id}/")
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

            response = admin_client.get(f"{self.URL}")
            self.assertTrue(
                ad_id not in [ad["pk"] for ad in response.json()["results"]]
            )

        response = APIClient().get(f"{self.URL}")
        self.assertEqual(len(response.json()["results"]), 0)


class ReviewCreateAPITestCase(BaseTestCase):
    """Создание комментария"""

    COMMENT_DATA = {"text": "Отличное объявление!"}

    def setUp(self):
        super().setUp()

        self.ad_ids = []

        self.user_details = [
            {"first_name": self.user_1.first_name, "last_name": self.user_1.last_name},
            {"first_name": self.user_2.first_name, "last_name": self.user_2.last_name},
        ]

        for i, client in enumerate(self.user_clients):
            ad_data = self.ADS_DATA[i]
            response = client.post(self.URL, ad_data)
            response_data = response.json()
            self.ad_ids.append(response_data.get("pk"))

        self.comment_urls = [f"{self.URL}{ad_id}/comments/" for ad_id in self.ad_ids]

    def test_unauthorized_user_cannot_create_comment(self):
        """Неавторизованный пользователь не может создать комментарий."""

        client = APIClient()
        for url in self.comment_urls:
            response = client.post(url, self.COMMENT_DATA)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_users_can_cross_comment(self):
        """Авторизованные пользователи и админ могут комментировать свои и чужие объявления."""

        for i, client in enumerate(self.user_clients):
            for j, url in enumerate(self.comment_urls):
                response = client.post(url, self.COMMENT_DATA)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)

                response_data = response.json()
                self.assertEqual(response_data.get("text"), self.COMMENT_DATA["text"])
                self.assertEqual(response_data.get("ad_id"), self.ad_ids[j])
                self.assertEqual(
                    response_data.get("author_first_name"),
                    self.user_details[i]["first_name"],
                )
                self.assertEqual(
                    response_data.get("author_last_name"),
                    self.user_details[i]["last_name"],
                )
                self.assertIsNotNone(response_data.get("pk"))
                self.assertIsNotNone(response_data.get("created_at"))


class ReviewReadAPITestCase(BaseTestCase):
    """Чтение комментариев"""

    COMMENT_DATA = {"text": "Отличное объявление!"}

    def setUp(self):
        super().setUp()

        self.ad_ids = []
        self.comment_ids = []

        for i, client in enumerate(self.user_clients):
            ad_data = self.ADS_DATA[i]
            response = client.post(self.URL, ad_data)
            response_data = response.json()
            self.ad_ids.append(response_data.get("pk"))

            comment_url = f"{self.URL}{self.ad_ids[i]}/comments/"
            comment_response = client.post(comment_url, self.COMMENT_DATA)
            comment_response_data = comment_response.json()
            self.comment_ids.append(comment_response_data.get("pk"))

        self.comment_urls = [f"{self.URL}{ad_id}/comments/" for ad_id in self.ad_ids]

    def test_unauthorized_user_cannot_read_comments(self):
        """Неавторизованный пользователь не может читать комментарии."""

        client = APIClient()
        for url in self.comment_urls:
            response = client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_users_can_read_comments(self):
        """Авторизованные пользователи могут читать комментарии."""

        for client in self.user_clients:
            for url in self.comment_urls:
                response = client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                response_data = response.json().get("results")
                self.assertNotEqual(len(response_data), 0)

                first_comment = response_data[0]
                self.assertIsNotNone(first_comment.get("text"))
                self.assertIsNotNone(first_comment.get("author_id"))
                self.assertIsNotNone(first_comment.get("created_at"))
                self.assertIsNotNone(first_comment.get("author_first_name"))
                self.assertIsNotNone(first_comment.get("author_last_name"))
                self.assertIsNotNone(first_comment.get("ad_id"))

    def test_unauthorized_user_cannot_read_comment_by_id(self):
        """Неавторизованный пользователь не может читать комментарий по ID."""

        client = APIClient()
        for ad_id, comment_id in zip(self.ad_ids, self.comment_ids):
            url = f"{self.URL}{ad_id}/comments/{comment_id}/"
            response = client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized_users_can_read_comment_by_id(self):
        """Авторизованные пользователи могут читать комментарий по ID."""

        for client in self.user_clients:
            for ad_id, comment_id in zip(self.ad_ids, self.comment_ids):
                url = f"{self.URL}{ad_id}/comments/{comment_id}/"
                response = client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                response_data = response.json()
                self.assertEqual(response_data.get("pk"), comment_id)
                self.assertEqual(response_data.get("ad_id"), ad_id)
                self.assertIsNotNone(response_data.get("text"))
                self.assertIsNotNone(response_data.get("author_id"))
                self.assertIsNotNone(response_data.get("created_at"))
                self.assertIsNotNone(response_data.get("author_first_name"))
                self.assertIsNotNone(response_data.get("author_last_name"))


class ReviewUpdateAPITestCase(BaseTestCase):
    """Обновление комментариев"""

    COMMENT_DATA = {"text": "Отличное объявление!"}

    UPDATE_COMMENT_DATA = {"text": "Обновленный комментарий"}

    def setUp(self):
        super().setUp()

        self.ad_ids = []
        self.comment_ids = []

        for i, client in enumerate(self.user_clients):
            ad_data = self.ADS_DATA[i]
            response = client.post(self.URL, ad_data)
            response_data = response.json()
            self.ad_ids.append(response_data.get("pk"))

            comment_url = f"{self.URL}{self.ad_ids[i]}/comments/"
            comment_response = client.post(comment_url, self.COMMENT_DATA)
            comment_response_data = comment_response.json()
            self.comment_ids.append(comment_response_data.get("pk"))

        self.comment_urls = [f"{self.URL}{ad_id}/comments/" for ad_id in self.ad_ids]

    def test_unauthorized_user_cannot_update_comment(self):
        """Неавторизованный пользователь не может обновить комментарий."""

        client = APIClient()
        for ad_id, comment_id in zip(self.ad_ids, self.comment_ids):
            url = f"{self.URL}{ad_id}/comments/{comment_id}/"
            response = client.patch(url, self.UPDATE_COMMENT_DATA)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def update_comment(self, client, ad_id, comment_id, data):
        url = f"{self.URL}{ad_id}/comments/{comment_id}/"
        return client.patch(url, data)

    def test_regular_user_can_update_own_comment(self):
        """Обычный пользователь может обновить только свои комментарии."""
        client = self.user_clients[0]
        ad_id, comment_id = self.ad_ids[0], self.comment_ids[0]

        response = self.update_comment(
            client, ad_id, comment_id, self.UPDATE_COMMENT_DATA
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("text"), self.UPDATE_COMMENT_DATA["text"])

    def test_regular_user_cannot_update_others_comments(self):
        """Обычный пользователь не может обновить комментарии других."""
        client = self.user_clients[0]
        ad_id, comment_id = self.ad_ids[1], self.comment_ids[1]

        response = self.update_comment(
            client, ad_id, comment_id, self.UPDATE_COMMENT_DATA
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_any_comment(self):
        """Администратор может обновить любой комментарий."""

        admin_client = self.user_clients[1]
        for ad_id, comment_id in zip(self.ad_ids, self.comment_ids):
            response = self.update_comment(
                admin_client, ad_id, comment_id, self.UPDATE_COMMENT_DATA
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response_data = response.json()
            self.assertEqual(
                response_data.get("text"), self.UPDATE_COMMENT_DATA["text"]
            )


class ReviewDeleteAPITestCase(BaseTestCase):
    """Удаление комментариев"""

    COMMENT_DATA = {"text": "Отличное объявление!"}

    def setUp(self):
        super().setUp()

        self.ad_ids = []
        self.comment_ids = []

        for i, client in enumerate(self.user_clients):
            ad_data = self.ADS_DATA[i]
            response = client.post(self.URL, ad_data)
            response_data = response.json()
            self.ad_ids.append(response_data.get("pk"))

            comment_url = f"{self.URL}{self.ad_ids[i]}/comments/"
            comment_response = client.post(comment_url, self.COMMENT_DATA)
            comment_response_data = comment_response.json()
            self.comment_ids.append(comment_response_data.get("pk"))

        self.comment_urls = [f"{self.URL}{ad_id}/comments/" for ad_id in self.ad_ids]

    def delete_comment(self, client, ad_id, comment_id):
        url = f"{self.URL}{ad_id}/comments/{comment_id}/"
        return client.delete(url)

    def test_unauthorized_user_cannot_delete_comment(self):
        """Неавторизованный пользователь не может удалить комментарий."""

        client = APIClient()
        for ad_id, comment_id in zip(self.ad_ids, self.comment_ids):
            response = self.delete_comment(client, ad_id, comment_id)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_can_delete_own_comment(self):
        """Обычный пользователь может удалить только свои комментарии."""

        client = self.user_clients[0]
        ad_id, comment_id = self.ad_ids[0], self.comment_ids[0]

        response = self.delete_comment(client, ad_id, comment_id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_regular_user_cannot_delete_others_comments(self):
        """Обычный пользователь не может удалить комментарии других."""

        client = self.user_clients[0]
        ad_id, comment_id = self.ad_ids[1], self.comment_ids[1]

        response = self.delete_comment(client, ad_id, comment_id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_any_comment(self):
        """Администратор может удалить любой комментарий."""

        admin_client = self.user_clients[1]
        for ad_id, comment_id in zip(self.ad_ids, self.comment_ids):
            response = self.delete_comment(admin_client, ad_id, comment_id)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
