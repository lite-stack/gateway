import os
from logging import DEBUG, getLogger, basicConfig, FileHandler, Formatter, Logger

from pydantic_settings import BaseSettings

base_dir = os.path.dirname(os.path.abspath(__file__))

'''LOGGING CONFIG'''
log_format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
log_dir = base_dir + '/logs'


def create_logger(level: str):
    level_upper = level.upper()
    file_handler = FileHandler(f'{log_dir}/{level_upper}.log')
    file_handler.setFormatter(Formatter(log_format))
    logger = getLogger(f'{level}_logger')
    logger.setLevel(level_upper)
    logger.addHandler(file_handler)


# GENERAL LOGS (ALL)
getLogger().setLevel(DEBUG)
basicConfig(filename=log_dir + '/GENERAL.log', level=DEBUG, format=log_format)
# ERROR LOGS
create_logger('error')
# INFO LOGS
create_logger('info')

'''END LOGGING CONFIG'''


class Settings(BaseSettings):
    db_engine: str = 'postgres'
    db_port: str = '5432'

    db_host: str = 'localhost'
    db_user: str = 'root'
    db_password: str = 'admin'
    db_schema: str = 'academy'

    error_logger: Logger = getLogger('error_logger')
    info_logger: Logger = getLogger('info_logger')

    secret_key: str = 'str'

    cloud_name: str = 'name'

    mail_username: str = 'username'
    mail_password: str = 'password'
    mail_port: int = 587
    mail_server: str = 'server'
    mail_from: str = 'from@test.com'
    mail_from_name: str = 'from_name'

    class Config:
        env_file = '.env'


app_description = '''
Openstack gateway
'''

APP_CONFIG = dict(
    title='FastAPI Template',
    version='0.0.1',
    description=app_description,
    openapi_tags=[
        #     {
        #         'name': 'courses',
        #         'description': 'Operations with courses.',
        #         'externalDocs': {
        #             'description': 'Courses external docs',
        #             'url': 'https://fastapi.tiangolo.com/',
        #         },
        #     },
    ]
)
