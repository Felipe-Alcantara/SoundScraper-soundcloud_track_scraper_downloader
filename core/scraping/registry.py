"""
registry.py — Mapeamento único das 7 opções de coleta do SoundScraper.

Concentra num só lugar o que antes estava espalhado entre scraper_service.py e
browser_handler.py (collection_map, choice_names, sufixos de URL, seletores CSS).
Adicionar/alterar uma opção passa a ser uma mudança local e auditável.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ChoiceSpec:
    """Especificação de uma opção do menu de coleta."""
    key: str                 # '1'..'7'
    name: str                # nome humano (PT-BR)
    url_suffix: str          # sufixo anexado à URL do perfil (Selenium / navegação)
    collection_type: str     # tipo na API v2 ('tracks', 'toptracks', 'reposts', 'likes', ...)
    is_set: bool = False     # True para álbum/playlist (a URL já é o link do set)


# Mapa canônico das opções. 'toptracks'/'tracks' refletem as rotas da API v2.
CHOICES: dict[str, ChoiceSpec] = {
    "1": ChoiceSpec("1", "Todas as Faixas", "", "tracks"),
    "2": ChoiceSpec("2", "Faixas Populares", "/popular-tracks", "toptracks"),
    "3": ChoiceSpec("3", "Faixas", "/tracks", "tracks"),
    "4": ChoiceSpec("4", "Álbuns", "", "", is_set=True),
    "5": ChoiceSpec("5", "Playlists", "", "", is_set=True),
    "6": ChoiceSpec("6", "Republicações", "/reposts", "reposts"),
    "7": ChoiceSpec("7", "Curtidas", "/likes", "likes"),
}

DEFAULT_CHOICE = "3"

# Seletor CSS para coleta via Selenium, por categoria.
CSS_SELECTOR_SET = "li.trackList__item a.trackItem__trackTitle"   # álbuns/playlists
CSS_SELECTOR_PROFILE = "a.soundTitle__title"                       # faixas de perfil


def get_choice(key: str) -> ChoiceSpec:
    """
    Retorna a ChoiceSpec da opção. Opção desconhecida → erro claro
    (em vez de silenciosamente cair em um padrão).
    """
    try:
        return CHOICES[key]
    except KeyError as exc:
        known = ", ".join(sorted(CHOICES))
        raise ValueError(f"Opção de coleta desconhecida: {key!r}. Opções: {known}") from exc


def css_selector_for(spec: ChoiceSpec) -> str:
    """Seletor CSS de coleta (Selenium) adequado à opção."""
    return CSS_SELECTOR_SET if spec.is_set else CSS_SELECTOR_PROFILE
