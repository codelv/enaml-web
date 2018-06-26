import pytest
from pprint import pprint
from atom.api import *
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFS
from web.core.db import Model
from web.apps.web_app import WebApplication
from utils import faker

class User(Model):
    name = Unicode()
    email = Unicode()
    active = Bool()


class Image(Model):
    name = Unicode()
    path = Unicode()


class Page(Model):
    title = Unicode()
    status = Enum('preview', 'live')
    body = Unicode()
    author = Instance(User)
    images = List(Image)
    related = List(ForwardInstance(lambda: Page))
    
    
class Comment(Model):
    page = Instance(Page)
    author = Instance(User)
    status = Enum('pending', 'approved')
    body = Unicode()
    reply_to = ForwardInstance(lambda: Comment)
    
    
@pytest.yield_fixture()
def app(event_loop):
    client = AsyncIOMotorClient(io_loop=event_loop)
    app = WebApplication.instance() or WebApplication()
    db = client.enaml_web_test_db
    app.database = db
    yield app


@pytest.mark.asyncio
async def test_simple_save_restore_delete(app):
    await User.objects.drop()
    
    # Save
    user = User(name=faker.name(), email=faker.email(), active=True)
    await user.save()
    assert user._id is not None
    
    # Restore
    state = await User.objects.find_one({'name': user.name})
    assert state
    
    u = await User.restore(state)
    assert u._id == user._id 
    assert u.name == user.name
    assert u.email == user.email
    assert u.active == user.active
    
    # Delete
    await user.delete()
    state = await User.objects.find_one({"name": user.name})
    assert not state


@pytest.mark.asyncio
async def test_nested_save_restore(app):
    await Image.objects.drop()
    await User.objects.drop()
    await Page.objects.drop()
    await Comment.objects.drop()
    
    authors = [
        User(name=faker.name(), active=True) for i in range(2)
    ]
    for a in authors:
        await a.save()
        
    images = [
        Image(name=faker.job(), path=faker.image_url()) for i in range(10)
    ]
    
    # Only save the first few, it should serialize the others
    for i in range(3):
        await images[i].save()
    
    pages = [
        Page(title=faker.catch_phrase(), body=faker.text(), author=author,
             images=[faker.random.choice(images) for j in range(faker.random.randint(0, 2))],
             status=faker.random.choice(Page.status.items))
        for i in range(4) for author in authors
    ]
    for p in pages:
        await p.save()
        
        # Generate comments
        comments = []
        for i in range(faker.random.randint(1, 10)):
            commentor = User(name=faker.name())
            await commentor.save()
            comment = Comment(author=commentor, page=p,
                              status=faker.random.choice(Comment.status.items),
                              reply_to=faker.random.choice([None]+comments),
                              body=faker.text())
            comments.append(comment)
            await comment.save()
    
    for p in pages:
        # Find in db
        state = await Page.objects.find_one({'author._id': p.author._id,
                                             'title': p.title})
        assert state, f'Couldnt find page by {p.title} by {p.author.name}'
        r = await Page.restore(state)
        assert p._id == r._id
        assert p.author._id == r.author._id
        assert p.title == r.title
        assert p.body == r.body
        for img_1, img_2 in zip(p.images, r.images):
            assert img_1.path == img_2.path
        
        async for state in Comment.objects.find({'page._id': p._id}):
            comment = await Comment.restore(state)
            assert comment.page._id == p._id
            async for state in Comment.objects.find({'reply_to._id': 
                                                         comment._id}):
                reply = await Comment.restore(state)
                assert reply.page._id == p._id
        

@pytest.mark.asyncio
async def test_circular(app):
    # Test that a circular reference is properly stored as a reference
    # and doesn't create an infinite loop
    await Page.objects.drop()
    
    p = Page(title=faker.catch_phrase(), body=faker.text())
    related_page = Page(title=faker.catch_phrase(), body=faker.text(), 
                        related=[p])
    
    # Create a circular reference
    p.related = [related_page]
    await p.save()
    
    # Make sure it restores properly
    state = await Page.objects.find_one({'_id': p._id})
    pprint(state)
    r = await Page.restore(state)
    assert r.title == p.title
    assert r.related[0].title == related_page.title
    assert r.related[0].related[0] == r
