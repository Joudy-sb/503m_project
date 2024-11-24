from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Create the limiter instance without attaching it to the app
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",  
)