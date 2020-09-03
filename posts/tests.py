import tempfile
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from posts.models import Group, Post, User, Follow


class TestContent(TestCase):
    def create_post_for_tests(self):
        self.authorized_client.post(
            reverse('new_post'),
            {
                'text': "Кто ходит в гости по утрам, тот поступает мудро",
                'author': self.user,
                'group': self.group.pk
                }
            )

    def setUp(self):
        self.authorized_client = Client()
        self.unauthorized_client = Client()
        self.user = User.objects.create(
            username='arthur', password='12345', email='artkam@yandex.ru'
            )
        self.user.save()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='test_group', slug='testgroup')

    def assert_post_to_url(self, url, base):
        response = self.authorized_client.get(url)
        paginator = response.context.get('page')
        if paginator is not None:
            post = response.context['page'][0]
        else:
            post = response.context['post']
        self.assertEqual(post.text, base.text)
        self.assertEqual(post.author, base.author)
        self.assertEqual(post.group, base.group)
        self.assertEqual(post.image, base.image)

    def vision_on_page(self, base):
        index_url = reverse('index')
        profile_url = reverse('profile',
                              kwargs={'username': self.user.username}
                             )
        post_url = reverse(
            'post',
            kwargs={'username': self.user.username, 'post_id': base.id}
            )
        group_posts_url = reverse('group_posts',
                                  kwargs={'slug': self.group.slug}
                                 )
        if base.group == self.group:
            for url in [index_url, profile_url, post_url, group_posts_url]:
                with self.subTest(url=url):
                    self.assert_post_to_url(url, base)
        else:
            for url in [index_url, profile_url, post_url]:
                with self.subTest(url=url):
                    self.assert_post_to_url(url, base)

    def create_author_and_subscribe_user(self):
        author = User.objects.create(
            username='Gvinivera', password='12345', email='GvinLansel@yandex.ru'
            )
        self.authorized_client.get(reverse('profile_follow', kwargs={'username':author.username}))

    def create_author_post(self):
        author = User.objects.get(username='Gvinivera')
        Post.objects.create(
            text='Stand up and fight!',
            author=author,
            group=self.group
        )
# Next functions are tests
    def test_profile_page_exists_for_registered_user(self):
        resp = self.authorized_client.get(
            reverse('profile', kwargs={
                'username': self.user.username
                })
            )
        self.assertEqual(resp.status_code, 200)

    def test_new_post_page_exists_for_registered_user(self):
        self.create_post_for_tests()  # create post
        self.assertEqual(Post.objects.count(), 1)

    def test_unauthorized_user_cannot_create_post(self):
        count_posts1 = Post.objects.count()
        resp = self.unauthorized_client.post(
            reverse('new_post'),
            {
                'text': "Кто ходит в гости по утрам, тот поступает мудро",
                'author': self.user,
                'group': self.group.pk
            }
            )
        count_posts2 = Post.objects.count()
        login_url = reverse('login')
        new_post_url = reverse('new_post')
        target_url = f'{login_url}?next={new_post_url}'
        self.assertRedirects(
            resp, target_url,
            status_code=302, target_status_code=200
            )
        self.assertEqual(count_posts1, count_posts2)

    def test_post_visible_on_page(self):
        Post.objects.create(
            text='Кто ходит в гости по утрам, тот поступает мудро',
            author=self.user,
            group=self.group
                        )
        base = Post.objects.first()
        self.vision_on_page(base)

    def test_checking_get_part_edit_form(self):
        self.create_post_for_tests()
        base = Post.objects.first()
        resp = self.authorized_client.get(reverse(
            'post_edit',
            kwargs={'username': self.user.username, 'post_id': base.id}
            ))
        self.assertEqual(resp.status_code, 200)

    def test_checking_post_part_edit_form(self):
        self.create_post_for_tests()
        base = Post.objects.first()
        base.text = 'Это ж-ж-ж-ж неспроста'
        group2 = Group.objects.create(title='test_group2', slug='testgroup2')
        self.authorized_client.post(
            reverse(
                'post_edit', kwargs={
                    'username': self.user.username,
                    'post_id': base.id
                    }
                ),
            {
                'text': base.text,
                'author': base.author,
                'group': group2.pk
                }
            )
        new_base = Post.objects.first()
        self.vision_on_page(new_base)
        response = self.authorized_client.get(
            reverse('group_posts',
                    kwargs={'slug': group2.slug}
                    ))
        self.assertContains(response, new_base.text)
        response = self.authorized_client.get(
            reverse('group_posts',
                    kwargs={'slug': self.group.slug}
                    ))
        self.assertNotContains(response, new_base.text)

    def test_page_not_found(self):
        response = self.client.get('/flkhefhaefhlahlkdhwlkkd/')
        self.assertEqual(response.status_code, 404)

    def test_image_can_be_on_page(self):
        img = Image.new('RGB', (60, 30), color='black')        
        self.authorized_client.post(
            reverse('new_post'),
            {
                'text': "Кто ходит в гости по утрам, тот поступает мудро",
                'author': self.user.username,
                'group': self.group.pk,
                'image': img
            },
            follow=True
            )
        base = Post.objects.first()
        self.vision_on_page(base)

    def test_protect_from_not_img_file(self):
        count_posts1 = Post.objects.count()
        img = tempfile.TemporaryFile()
        self.authorized_client.post(
            reverse('new_post'),
            {
                'text': "Кто ходит в гости по утрам, тот поступает мудро",
                'author': self.user.username,
                'group': self.group.pk,
                'image': img
            },
            follow=True
            )
        count_posts2 = Post.objects.count()
        self.assertEqual(count_posts1, count_posts2)

    def test_cache_index_page(self):
        self.create_post_for_tests()
        post1 = Post.objects.first()
        response1 = self.authorized_client.get(reverse('index'))
        self.assertContains(response1, post1.text)
        post2 = Post.objects.create(
            text='На то оно и утро',
            author=self.user,
            group=self.group
        )
        response2 = self.authorized_client.get(reverse('index'))
        self.assertNotContains(response2, post2.text)
        cache.clear()  # we can also use time.sleep(20), but it's too long
        response3 = self.authorized_client.get(reverse('index'))
        self.assertContains(response3, post2.text)

    def test_authorized_user_can_subscribe_and_delete_subscribings(self):
        count_1 = Follow.objects.count()
        self.create_author_and_subscribe_user()
        count_2 = Follow.objects.count()
        self.assertNotEqual(count_1, count_2)
        author = User.objects.get(username='Gvinivera')
        self.authorized_client.get(reverse(
            'profile_unfollow',
            kwargs={'username': author.username}
        ))
        count_3 = Follow.objects.count()
        self.assertEqual(count_1, count_3)

    def test_new_authors_post_visible_for_followers(self):
        self.create_author_and_subscribe_user()
        self.create_author_post()
        base = Post.objects.get(author__username='Gvinivera')
        response = self.authorized_client.get(reverse('follow_index'))
        self.assertContains(response, base.text)
        cache.clear()
        self.authorized_client.get(reverse(
            'profile_unfollow',
            kwargs={'username': base.author.username}
        ))
        response = self.authorized_client.get(reverse('follow_index'))
        self.assertNotContains(response, base.text)

    def test_authorized_user_can_add_comments(self):
        post = Post.objects.create(
            text='На то оно и утро',
            author=self.user,
            group=self.group
        )
        self.authorized_client.post(
            reverse(
                    'add_comment',
                    kwargs={
                    'username': self.user.username,
                    'post_id': post.pk
                }),
            {'text':'Это ж-ж-ж-ж неспроста'}
            )
        response = self.authorized_client.get(reverse(
            'post',
        kwargs={'username': self.user.username, 'post_id':post.pk}
        ))
        self.assertContains(response, 'Это ж-ж-ж-ж неспроста')
