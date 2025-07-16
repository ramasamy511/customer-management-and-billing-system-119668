from setuptools import setup, find_packages

setup(
    name="customer_management_billing_backend",
    version="1.0.0",
    description="API backend for managing customers, invoices, payments, reporting, analytics, reminders, and data export.",
    author="Your Name",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi==0.115.12",
        "uvicorn==0.34.0",
        "SQLAlchemy==2.0.30",
        "PyMySQL==1.1.0",
        "python-dotenv==1.1.0",
        "email_validator==2.2.0",
        "Jinja2==3.1.6",
        "httpx==0.28.1",
        "pydantic==2.11.3",
        "python-multipart==0.0.20"
    ],
    entry_points={
        "console_scripts": [
            "run_backend_api=api.main:main"
        ]
    },
    python_requires=">=3.9",
)
