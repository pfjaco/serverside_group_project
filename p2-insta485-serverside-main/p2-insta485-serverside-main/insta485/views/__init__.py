"""Views, one for each Insta485 page."""
from insta485.views.index import show_index, get_file
from insta485.views.user import show_user
from insta485.views.followers import show_followers
from insta485.views.following import show_following
from insta485.views.explore import show_explore
from insta485.views.posts import show_post
from insta485.views.account_handling import login_user
from insta485.views.account_handling import display_create_account_page
from insta485.views.account_handling import display_edit_account_form
from insta485.views.account_handling import display_change_password
from insta485.views.account_handling import is_logged_in
from insta485.views.likes import post_like_unlike
from insta485.views.comment_handling import handle_comments
from insta485.views.following_handling import handle_following_operations
from insta485.views.post_handling import handle_post
