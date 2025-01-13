from fastapi import FastAPI

from routes.AppRoute import router as route
from utils.ServerManager import ServerManager

app = FastAPI(
    title="Project Watch API",
    description="API for managing PW users.",
    version="1.0.0"
)

server_manager = ServerManager()


@app.on_event("startup")
async def startup_event():
    try:
        print(f"Please select from the following {server_manager.config.schema_list()}")
        default_database = "project_watch"

        if default_database:
            server_manager._init_once()

            # Check if the schema exists before setting it
            if server_manager.config.schema_exists(default_database):
                server_manager.set_schema(default_database)
                print(f"Default database set to: {default_database}")
            else:
                raise RuntimeError(f"The specified database '{default_database}' does not exist.")
        else:
            raise RuntimeError("No default database specified.")

    except Exception as e:
        print(f"Failed to set default database: {e}")
        exit(1)  # Exit the application after a failed attempt


@app.on_event("shutdown")
async def shutdown_event():
    # Close any active database sessions
    server_manager.close_session()
    print("Database sessions closed successfully.")


app.include_router(route)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=4000)
