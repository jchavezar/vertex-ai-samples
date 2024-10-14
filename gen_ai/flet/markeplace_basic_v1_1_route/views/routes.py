from views.Router import Router, DataStrategyEnum
from views.search_view import SearchView
from views.info_view import InfoView
from views.logo_view import LogoView
from views.recommendations_view import RecommendationsView

router = Router(DataStrategyEnum.STATE)

router.routes = {
    "/": SearchView,
    "/logo_widget": LogoView,
    "/info_widget": InfoView,
    "/recommendations_widget": RecommendationsView,
    # "/profile": ProfileView,
    # "/settings": SettingsView,
    # "/data": DataView
}