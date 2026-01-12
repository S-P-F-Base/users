"""
table perma_limit 1:1
id -> credentials.id int
char_slot int
lore_char_slot int
weight_bytes int

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

table access 1:1
id -> credentials.id
version int для миграции онли. Возможно даже не особо нужно если быть честным
access json blob
"""

from .credentials_db import CredentialsDB
