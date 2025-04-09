import asyncio
from http.client import responses
import datetime
import pprint
from more_itertools import chunked
from requests import session

from models import Session, init_orm, close_orm, SWapiPeople
import aiohttp
MAX_CONCURRENT_REQUEST = 5

async def get_people (person_id, session):
        response = await session.get(f'https://swapi.py4e.com/api/people/{person_id}/')
        json = await response.json()
        return json

# async def insert_results(results_list_json):
#     async with Session() as session:
#         people = [SWapiPeople(json=result) for result in results_list_json]
#         session.add_all(people)
#         await session.commit()

async def insert_results(results_list_json):
    async with Session() as session:
        people = []
        for json_item in results_list_json:
            person_id = json_item.get('id')
            birth_year = json_item.get('birth_year')
            eye_color = json_item.get('eye_color')
            # films = json_item.get('films')
            gender = json_item.get('gender')
            hair_color = json_item.get('hair_color')
            height = json_item.get('height')
            homeworld_name = await get_homeworld(json_item.get('homeworld'))
            mass = json_item.get('mass')
            name = json_item.get('name')
            skin_color = json_item.get('skin_color')
            species_name = await get_species (json_item.get('species'))
            # starships = json_item.get('starships')
            # vehicles = json_item.get('vehicles')
            people.append((SWapiPeople(id=person_id,
                                       birth_year=birth_year,
                                       eye_color=eye_color,
                                       # films=films,
                                       gender=gender,
                                       hair_color=hair_color,
                                       height=height,
                                       homeworld=homeworld_name,
                                       mass=mass,
                                       name=name,
                                       skin_color=skin_color,
                                       species=species_name)))
                                       # starships=starships,
                                       # vehicles=vehicles)))
        session.add_all(people)
        await session.commit()

async def get_homeworld(homeworld):
    async with aiohttp.ClientSession() as session:
        async with session.get(homeworld) as response:
            homeworld_data = await response.json()
            print(homeworld_data['name'])
    return homeworld_data['name']

async def get_species(species):
    titles = []
    async with aiohttp.ClientSession() as session:
        for data in species:
            # print(data)
            async with session.get(data) as response:
                species_data = await response.json()
                # print(species_data)
                titles.append(species_data['name'])
                # print(''.join(titles))
    return ''.join(titles)

async def get_starships(starships):
    pass

async def get_vehicles(vehicles):
    pass

async def main():
    await init_orm()
    async with aiohttp.ClientSession() as session:
        for i_chunk in chunked(range(1, 101), MAX_CONCURRENT_REQUEST):
            coros = [get_people(i, session) for i in i_chunk]
            results = await asyncio.gather(*coros)
            tasks = asyncio.create_task(insert_results(results))
            # pprint.pprint(results)
    tasks = asyncio.all_tasks()
    curent_task = asyncio.current_task()
    tasks.remove(curent_task)
    await asyncio.gather(*tasks)
    await close_orm()
asyncio.run(main())