from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://factory_app:change_this_password@db:5432/factory_booking"
    app_title: str = "Factory Test Room Reservation"
    admin_key: str = "change-this-admin-key"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
