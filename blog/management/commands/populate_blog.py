from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Post, Comment
from django.utils.text import slugify
from django.utils.timezone import make_aware
from faker import Faker
import random

fake = Faker()

class Command(BaseCommand):
    help = 'Populate the database with fake blog data'

    def handle(self, *args, **kwargs):
        users = []

        # ✅ Create 20 users
        for i in range(20):
            username = fake.unique.user_name()
            email = fake.unique.email()
            password = 'test1234'
            user = User.objects.create_user(username=username, email=email, password=password)
            users.append(user)
        self.stdout.write(self.style.SUCCESS('✅ Created 20 users'))

        # ✅ Create 1000 posts
        for _ in range(1000):
            title = fake.sentence(nb_words=6)
            slug = slugify(title + "-" + fake.unique.lexify(text='????'))
            body = fake.paragraph(nb_sentences=20)
            author = random.choice(users)
            status = random.choice(['DF', 'PB'])  # DF = Draft, PB = Published

            publish_time = make_aware(fake.date_time_between(start_date='-2y', end_date='now'))

            post = Post.objects.create(
                title=title,
                slug=slug,
                body=body,
                author=author,
                status=status,
                publish=publish_time
            )

            # ✅ Add 1–5 comments to published posts
            if post.status == 'PB':
                for _ in range(random.randint(1, 5)):
                    Comment.objects.create(
                        post=post,
                        name=fake.name(),
                        email=fake.email(),
                        body=fake.text(max_nb_chars=300),
                        active=True
                    )

        self.stdout.write(self.style.SUCCESS('✅ Created 1000 posts with random comments'))
