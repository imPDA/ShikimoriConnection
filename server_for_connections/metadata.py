from discord_connections.datatypes import Metadata, MetadataField, MetadataType


class ShikimoriMetadata(Metadata):
    platform_name = 'shikimori.one'
    anime_finished = MetadataField(MetadataType.INT_GTE, 'аниме просмотрено', 'или больше аниме просмотрено')
    watch_time = MetadataField(MetadataType.INT_GTE, 'дней аниме', 'или больше дней аниме')
