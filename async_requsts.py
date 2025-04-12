import asyncio
from more_itertools import chunked
from models import Session, init_orm, close_orm, SWapiPeople
import aiohttp

MAX_CONCURRENT_REQUEST = 5

async def get_people(person_id, session):
    try:
        async with session.get(f'https://swapi.dev/api/people/{person_id}/') as response:
            response.raise_for_status()  # Проверяем на ошибки
            return await response.json()
    except Exception as e:
        print(f"Error fetching person {person_id}: {e}")
        return None

async def insert_results(results_list_json):
    async with Session() as session:
        people = []
        for json_item in results_list_json:
            if json_item is None:
                continue
            person_id = int(json_item.get('url').split('/')[-2])  # Получаем ID из URL
            birth_year = json_item.get('birth_year')
            eye_color = json_item.get('eye_color')
            films_name = await get_films(json_item.get('films'))
            gender = json_item.get('gender')
            hair_color = json_item.get('hair_color')
            height = json_item.get('height')
            homeworld_name = await get_homeworld(json_item.get('homeworld'))
            mass = json_item.get('mass')
            name = json_item.get('name')
            skin_color = json_item.get('skin_color')
            species_name = await get_species(json_item.get('species'))
            starships_name = await get_starships(json_item.get('starships'))
            vehicles_name = await get_vehicles(json_item.get('vehicles'))
            people.append(SWapiPeople(
                id=person_id,
                birth_year=birth_year,
                eye_color=eye_color,
                films=films_name,
                gender=gender,
                hair_color=hair_color,
                height=height,
                homeworld=homeworld_name,
                mass=mass,
                name=name,
                skin_color=skin_color,
                species=species_name,
                starships=starships_name,
                vehicles=vehicles_name
            ))
        session.add_all(people)
        await session.commit()

async def get_films(films):
    titles = []
    async with aiohttp.ClientSession() as session:
        film_tasks = [session.get(film) for film in films]
        responses = await asyncio.gather(*film_tasks)
        for response in responses:
            try:
                film_data = await response.json()
                titles.append(film_data['title'])
            except Exception as e:
                print(f'Error getting film: {e}')
    return ', '.join(titles)

async def get_homeworld(homeworld):
    async with aiohttp.ClientSession() as session:
        async with session.get(homeworld) as response:
            homeworld_data = await response.json()
            return homeworld_data['name']

async def get_species(species):
    titles = []
    async with aiohttp.ClientSession() as session:
        species_tasks = [session.get(s) for s in species]
        responses = await asyncio.gather(*species_tasks)
        for response in responses:
            try:
                species_data = await response.json()
                titles.append(species_data['name'])
            except Exception as e:
                print(f'Error getting species: {e}')
    return ', '.join(titles)

async def get_starships(starships):
    titles = []
    async with aiohttp.ClientSession() as session:
        starship_tasks = [session.get(s) for s in starships]
        responses = await asyncio.gather(*starship_tasks)
        for response in responses:
            try:
                starship_data = await response.json()
                titles.append(starship_data['name'])
            except Exception as e:
                print(f'Error getting starship: {e}')
    return ', '.join(titles)

async def get_vehicles(vehicles):
    titles = []
    async with aiohttp.ClientSession() as session:
        vehicle_tasks = [session.get(v) for v in vehicles]
        responses = await asyncio.gather(*vehicle_tasks)
        for response in responses:
            try:
                vehicle_data = await response.json()
                titles.append(vehicle_data['name'])
            except Exception as e:
                print(f'Error getting vehicle: {e}')
    return ', '.join(titles)

async def main():
    await init_orm()
    async with aiohttp.ClientSession() as session:
        for i_chunk in chunked(range(1, 101), MAX_CONCURRENT_REQUEST):
            coros = [get_people(i, session) for i in i_chunk]
            results = await asyncio.gather(*coros)
            await insert_results(results)
    await close_orm()

# Запуск основного сценария
if __name__ == '__main__':
    asyncio.run(main())