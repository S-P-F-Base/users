"""
table timed_limit X:1
uid для того чтобы колизии доджить
id -> credentials.id
char_slot int
weight_bytes int
expired int timestemp
status str возможно имеет смысл локально хранить как инт, но зная себя я забуду при отдавании поменять инт на стринги и буду очень много орать

table db_char X:1
uid для того чтобы колизии доджить
id -> credentials.id
name str
discord_url str
char_type str аналогично timed_limit.status. Хотелось бы инт, но я сам себе злобный буратино и себе срать не хочу
content_ids json blob просто лист айдишек стима, по котором и будет расчёт даты
game_db_id int будующее связка для игровой бд как только у меня руки дотянутся. Пока всё null
"""

from .access_db import AccessDB
from .credentials_db import CredentialsDB
from .perma_limit_db import PermaLimitDB
