from discord_connections.datatypes import Metadata, MetadataField, MetadataType


class ShikimoriMetadata(Metadata):
    platform_name = 'My Cool Name'
    anime_finished = MetadataField(MetadataType.INT_GTE, 'аниме просмотрено', 'или больше аниме просмотрено')
