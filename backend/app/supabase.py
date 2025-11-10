from functools import lru_cache

from supabase import Client, create_client

from .settings import Settings


@lru_cache(maxsize=1)
def get_supabase_client(settings: Settings | None = None) -> Client:
    """
    Lazily instantiate a Supabase client.

    Parameters
    ----------
    settings:
        Optional Settings instance; if omitted the global application settings are used.
    """
    if settings is None:
        from .settings import get_settings

        settings = get_settings()

    return create_client(
        settings.supabase_url, settings.supabase_service_role_key or settings.supabase_anon_key.get_secret_value()
    )

