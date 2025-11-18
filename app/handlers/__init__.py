# Drop all the routers right here

from .start import start_router
from .watch import watch_router

# NOTE: If you have blocking router, please drop it at the end of the other routers.
# If you don't do so the process will block all further routers

routers = [
    start_router,
    watch_router,
]