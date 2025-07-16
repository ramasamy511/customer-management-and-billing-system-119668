# Backend FastAPI - Deployment & Packaging

## Packaging as Python Package (Wheel/sdist)
- Install in dev: `pip install -e .`
- Build distributable (wheel/sdist):  
  ```
  python setup.py sdist bdist_wheel
  ```
  Distributable files will be created in `dist/` folder.

## Running with Uvicorn (Local/dev)
- From root:
  ```
  pip install -r requirements.txt
  uvicorn api.main:app --host 0.0.0.0 --port 8000
  ```

## Running with Docker
- Build image:
  ```
  docker build -t customer-backend-api .
  ```
- Run container:
  ```
  docker run --env-file ../.env -p 8000:8000 customer-backend-api
  ```
  Adjust `--env-file` as needed to pass SMTP, DB, and other environment variables per README.md instructions.

## Environment Variables
See the main `README.md` for details on environment variables needed for SMTP, WhatsApp integration, and DB connection.
