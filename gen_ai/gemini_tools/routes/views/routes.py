from views.Router import Router, DataStrategyEnum
from views.search_view import SearchView
from views.info_view import InfoView

# from views.profile_view import ProfileView
# from views.settings_view import SettingsView
# from views.data_view import DataView

router = Router(DataStrategyEnum.STATE)

router.routes = {
    "/": SearchView,
    "/info_widget": InfoView,
    # "/profile": ProfileView,
    # "/settings": SettingsView,
    # "/data": DataView
}