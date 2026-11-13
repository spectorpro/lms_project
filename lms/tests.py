from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from lms.models import Course, Lesson, Subscription

User = get_user_model()


class LessonCRUDTestCase(APITestCase):

    def setUp(self):
        # Три пользователя: владелец, чужак, модератор
        self.owner = User.objects.create_user(email="owner@mail.ru", password="Qwerty123")
        self.other = User.objects.create_user(email="other@mail.ru", password="Qwerty123")
        self.moderator = User.objects.create_user(email="mod@mail.ru", password="Qwerty123")

        # Добавляем модератора в группу "moderators" (создаём, если её нет)
        group, _ = Group.objects.get_or_create(name="moderators")
        self.moderator.groups.add(group)

        self.course = Course.objects.create(
            title="Курс 1", description="Тест", owner=self.owner
        )
        self.lesson = Lesson.objects.create(
            title="Урок 1", description="Тест",
            course=self.course, owner=self.owner,
        )

        self.list_url = reverse("lms:lesson-list")
        self.create_url = reverse("lms:lesson-create")
        self.detail_url = reverse("lms:lesson-retrieve", args=[self.lesson.pk])
        self.update_url = reverse("lms:lesson-update", args=[self.lesson.pk])
        self.delete_url = reverse("lms:lesson-delete", args=[self.lesson.pk])

    def test_list_authenticated(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.json())  # ответ приходит уже с пагинацией

    def test_list_unauthenticated(self):
        response = self.client.get(self.list_url)
        self.assertIn(response.status_code, (401, 403))

    def test_create_lesson_with_youtube_url(self):
        self.client.force_authenticate(user=self.owner)
        data = {
            "title": "Урок 2", "description": "Ок",
            "course": self.course.pk,
            "video_url": "https://youtube.com/watch?v=abc",
        }
        response = self.client.post(self.create_url, data)  # POST на create, не на list
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_create_lesson_with_foreign_url(self):
        self.client.force_authenticate(user=self.owner)
        data = {
            "title": "Урок 3", "description": "Плохая ссылка",
            "course": self.course.pk,
            "video_url": "https://example.com/video",
        }
        response = self.client.post(self.create_url, data)  # POST на create, не на list
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Lesson.objects.count(), 1)  # урок не создан

    def test_moderator_can_update(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.patch(self.update_url, {"title": "Правка модератора"})  # ← было detail_url
        self.assertEqual(response.status_code, 200)


    def test_moderator_can_update(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.patch(self.update_url, {"title": "Правка модератора"})
        self.assertEqual(response.status_code, 200)

    def test_stranger_cannot_update(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.patch(self.update_url, {"title": "Взлом"})  # ← было detail_url
        self.assertIn(response.status_code, (403, 404))

    def test_owner_can_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.delete_url)  # ← было detail_url
        self.assertEqual(response.status_code, 204)

    def test_stranger_cannot_delete(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.delete(self.delete_url)  # ← было detail_url
        self.assertIn(response.status_code, (403, 404))



class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@mail.ru", password="Qwerty123")
        self.course = Course.objects.create(
            title="Курс A", description="d", owner=self.user
        )
        self.url = reverse("lms:subscription-toggle")

    def test_subscribe(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"course_id": self.course.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe(self):
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"course_id": self.course.pk})
        self.assertEqual(response.json()["message"], "подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_toggle_twice_removes(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self.url, {"course_id": self.course.pk})
        response = self.client.post(self.url, {"course_id": self.course.pk})
        self.assertEqual(response.json()["message"], "подписка удалена")
        self.assertEqual(Subscription.objects.count(), 0)


    def test_is_subscribed_true_in_course(self):
        self.client.force_authenticate(user=self.user)
        Subscription.objects.create(user=self.user, course=self.course)
        url = reverse("lms:courses-detail", args=[self.course.pk])
        response = self.client.get(url)
        print("ОТВЕТ:", response.json())
        self.assertEqual(response.json()["is_subscribed"], True)

    def test_is_subscribed_false_in_course(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:courses-detail", args=[self.course.pk])  # то же исправление
        response = self.client.get(url)
        self.assertEqual(response.json()["is_subscribed"], False)

    def test_toggle_twice_removes(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self.url, {"course_id": self.course.pk})
        response = self.client.post(self.url, {"course_id": self.course.pk})
        self.assertEqual(response.json()["message"], "подписка удалена")
        self.assertEqual(Subscription.objects.count(), 0)


class PaginationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="p@mail.ru", password="Qwerty123")
        course = Course.objects.create(title="Курс", description="d", owner=self.user)
        for i in range(15):
            Lesson.objects.create(
                title=f"Урок {i}", description="d",
                course=course, owner=self.user,
            )

    def test_page_size(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("lms:lesson-list") + "?page_size=5")  # было lesson-list-create
        self.assertEqual(len(response.json()["results"]), 5)

    def test_max_page_size_cap(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("lms:lesson-list") + "?page_size=100")  # то же исправление
        self.assertEqual(len(response.json()["results"]), 15)
