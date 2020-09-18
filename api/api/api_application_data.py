from api.security import Security
from core_lib.application_data import repositories

security = Security(user_repository=repositories.user_repository)
