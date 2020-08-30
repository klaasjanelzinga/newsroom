from aiohttp import ClientSession

from api.security import Security
from core_lib.application_data import user_repository

security = Security(user_repository)
client_session = ClientSession()
