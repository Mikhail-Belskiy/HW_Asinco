import json
from aiohttp import web
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from models import init_orm, close_orm, Advert, Session

@web.middleware
async def session_middleware(request, handler):
    async with Session() as session:
        request['session'] = session
        response = await handler(request)
        return response

async def orm_context(app):
    print('start')
    await init_orm()
    yield
    await close_orm()
    print('finish')

def generate_error(err_cls, message: str | dict | list):
    message = json.dumps({'error': message})
    return err_cls(text=message, content_type='application/json')

class AdvertsView(web.View):
    @property
    def session(self):
        return self.request['session']

    async def get(self):
        result = await self.session.execute(select(Advert))
        adverts = result.scalars().all()
        return web.json_response([
            {
                'id': adv.id,
                'title': adv.title,
                'description': adv.description,
                'owner_id': adv.owner_id,
                'date': adv.registration_time.isoformat()
            } for adv in adverts
        ])

    async def post(self):
        json_data = await self.request.json()
        advert = Advert(
            title=json_data['title'],
            description=json_data['description'],
            owner_id=json_data['owner_id']
        )
        self.session.add(advert)
        try:
            await self.session.commit()
            await self.session.refresh(advert)
        except IntegrityError:
            raise generate_error(web.HTTPConflict, 'advert already exists')
        return web.json_response({
            'id': advert.id,
            'title': advert.title,
            'description': advert.description,
            'owner_id': advert.owner_id,
            'date': advert.registration_time.isoformat()
        })

class UserView(web.View):
    @property
    def session(self):
        return self.request['session']

    @property
    def id(self):
        return int(self.request.match_info['id'])

    async def get_current_advert(self):
        advert = await self.session.get(Advert, self.id)
        if advert is None:
            raise generate_error(web.HTTPNotFound, 'not found')
        return advert

    async def get(self):
        advert = await self.get_current_advert()
        return web.json_response({
            'id': advert.id,
            'title': advert.title,
            'description': advert.description,
            'owner_id': advert.owner_id,
            'date': advert.registration_time.isoformat()
        })

    async def patch(self):
        advert = await self.get_current_advert()
        json_data = await self.request.json()
        if 'title' in json_data:
            advert.title = json_data['title']
        if 'description' in json_data:
            advert.description = json_data['description']
        try:
            await self.session.commit()
            await self.session.refresh(advert)
        except Exception:
            raise generate_error(web.HTTPBadRequest, 'could not update advert')
        return web.json_response({
            'id': advert.id,
            'title': advert.title,
            'description': advert.description,
            'owner_id': advert.owner_id,
            'date': advert.registration_time.isoformat()
        })

    async def delete(self):
        advert = await self.get_current_advert()
        await self.session.delete(advert)
        await self.session.commit()
        return web.json_response({'status': 'complete'})

app = web.Application(middlewares=[session_middleware])
app.cleanup_ctx.append(orm_context)

app.add_routes([
    web.get('/api/v1/adverts', AdvertsView),
    web.post('/api/v1/adverts', AdvertsView),
    web.get('/api/v1/adverts/{id:[0-9]+}', UserView),
    web.patch('/api/v1/adverts/{id:[0-9]+}', UserView),
    web.delete('/api/v1/adverts/{id:[0-9]+}', UserView)
])

if __name__ == '__main__':
    web.run_app(app)