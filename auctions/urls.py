from django.urls import path

from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listings/<int:listing_id>", views.listing, name="listing"),
    path("listings/<int:listing_id>/add-to-watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("listings/<int:listing_id>/remove-from-watchlist", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("listings/<int:listing_id>/place-bid", views.place_bid, name="place_bid"),
    path("listings/<int:listing_id>/close-listing", views.close_listing, name="close_listing"),
    path("listings/<int:listing_id>/comment", views.comment, name="comment"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category, name="category"),
]