# Photo share app
[![MIT License](https://img.shields.io/badge/license-MIT-green)](https://github.com/theneonwhale/frt-photo-share/blob/main/LICENSE.md)
![Version](https://img.shields.io/badge/version-v0.1.0-green)
--
Introducing a robust application that offers a secure and interactive platform for photo sharing. With features like JWT token-based authentication, three distinct user roles, and the ability to manage photos by viewing, downloading, and deleting them, users can easily organize their visual memories. Moreover, users can enhance their photos, add tags and descriptions, generate QR codes for easy sharing, engage in comments and ratings, while admins and moderators maintain control over user interactions and ratings.

## Prerequisites
Before you begin, ensure that you have the following prerequisites installed on your system:

- Python 3.10 or higher
- Poetry

## Installation
1. Clone the project repository:
```
git clone <repository_url>
```

2. Navigate to the project directory:
```
cd <project_directory>
```
3. Install the project dependencies using Poetry:
```
poetry install
```
Poetry will create a virtual environment and install the required packages specified in the pyproject.toml file.

## Launching
To launch the development server and start the FastAPI project, follow these steps:

1. Activate the project's virtual environment:
```
poetry shell
```
2. Run the following command to start the development server:
```
uvicorn main:app --reload
```
- ```main``` refers to the name of the main file where your FastAPI app instance is created.
- ```--reload``` enables auto-reloading of the server whenever code changes are detected (useful during development).
3. Once the server has started, you should see output similar to the following:

```
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```
Open your web browser and navigate to http://127.0.0.1:8000 to access the API.

4. Swager documentation could be found here: http://127.0.0.1:8000/docs

## Application features
- Authentication using JWT tokens, LogIn-LogOut mechanism.
- Three basic user roles (admin, user, moderator).
- Ability to view, download, delete photos.
- Ability to add up to 5 tags to a photo.
- Ability to edit the description of the photo.
- Ability to modify photos (Cloudinary service).
- Ability to create a link to the photo in the form of a QR code.
- Users can comment on each other's photos, edit their own comments.
- Admins and moderators can delete comments.
- View user profile - information about the user. Name, when registered, number of uploaded photos.
- Users can edit information about themselves and see information about themselves.
- The admin can make users inactive (ban) - users will not be able to enter the application.
- Users can give a rating to a photo from 1 to 5. The rating is calculated as the average of the ratings of all users. You can rate a photo only once for a user. You cannot rate your own photos.
- Admins and moderators can view and delete user ratings.

### Used technologies
- Python (programming language)
- FastAPI (web framework)
- Uvicorn (ASGI server)
- SQLAlchemy (database toolkit)
- Alembic (database migration tool)
- Pydantic (data validation and parsing)
- Jinja2 (template engine)
- python-multipart (support for multipart/form-data)
- python-jose (JSON Web Tokens implementation)
- Passlib (password hashing)
- libgravatar (Gravatar integration)
- fastapi-mail (email sending in FastAPI)
- Redis (in-memory data structure store)
- fastapi-limiter (request rate limiting)
- cloudinary (cloud-based image and video management)
- httpx (HTTP client)
- pytest (testing framework)
- fastapi-pagination (pagination support for FastAPI)
- aiofile (asyncio file operations)
- aiopath (asyncio file path manipulation)
- qrcode (QR code generation)
- psycopg2-binary (PostgreSQL database adapter)
- pytest-mock (pytest extension for mocking)
- Sphinx (documentation generator)
- pytest-cov (coverage reporting for pytest)

### Developers - Fast Rabbit Team
- [Andrii Kylymnyk](https://github.com/theneonwhale)
- [Denys Tantsiura](https://github.com/DenysTantsiura)
- [Anton Holovin](https://github.com/Unfeir)

#### License
This project is licensed under the MIT License.
