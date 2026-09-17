from beanie import Document

class ItemInventario(Document):

    tipo_alimento: str
    cantidad_disponible: int

    class Settings:

        name = "bodega_central"

