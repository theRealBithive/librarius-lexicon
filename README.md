# librarius-lexicon

This **Django-based application**, packaged as a **Docker container**, simplifies the process of getting your audiobooks ready for [Audiobookshelf](https://www.audiobookshelf.org/). Simply place your audiobook files into a designated input folder, and the tool will automatically process them, clarify metadata through a web interface, and then neatly organize them into your Audiobookshelf library.

-----

## ✨ What It Does

Librarius Lexicon streamlines your workflow:

1.  **Input & Detection**: You drop your audiobook files into a specified **input folder**. While manual uploads are possible, the primary design encourages using the input folder, perhaps in conjunction with a torrent client or similar download tool.
2.  **Metadata Collection**: The tool intelligently **collects metadata based on the filename**.
3.  **Clarification Interface**: If the metadata isn't perfectly clear or needs confirmation, a **web interface** will prompt you for clarification. This ensures your audiobooks are correctly identified.
4.  **Audiobookshelf Formatting**: Once confirmed, the files are **arranged into the specific format required by Audiobookshelf** and then **copied to your designated output folder**, making them immediately available in your Audiobookshelf library.

-----

## ⚠️ Important Disclaimer

This project is solely designed for **reorganizing existing audiobook files**. It **does not assist in acquiring audiobooks**. For obtaining audiobook material, please refer to dedicated tools like [Readarr](https://readarr.com/) or [LazyLibrarian](https://lazylibrarian.gitlab.io/).

-----

## 🚀 Getting Started

Getting this tool up and running is straightforward. You'll just need Docker and to point the container to your input and output directories.

### Prerequisites

  * **Docker**: Ensure Docker is installed on your system. You can download it from [Docker Desktop](https://www.docker.com/products/docker-desktop).

### Installation & Setup

1.  **Clone the Repository**:
    First, get a copy of the project files to your local machine:

    ```bash
    git clone https://github.com/your-username/audiobook-organizer.git
    cd audiobook-organizer
    ```

    *(Remember to replace `your-username` with the actual GitHub path once available.)*

2.  **Configure Docker Compose**:
    The easiest way to run the application is using `docker-compose`. Create a `docker-compose.yml` file in the root of the cloned directory with the following content:

    ```yaml
    services:
      librarius-lexicon:
        build: .
        container_name: librarius-lexicon
        ports:
          - "8000:8000" # Map host port 8000 to container port 8000
        volumes:
          # --- IMPORTANT: CHANGE THESE PATHS ---
          - /path/to/your/audiobook/downloads:/app/input  # **Your local folder for new audiobooks**
          - /path/to/your/audiobookshelf/library:/app/output # **Your Audiobookshelf library folder**
          # -------------------------------------
        environment:
          PYTHONUNBUFFERED: 1 # Ensures Python output is immediately visible in logs
    ```

    **Crucially, replace `/path/to/your/audiobook/downloads` with the absolute path to the folder where you place new audiobooks, and `/path/to/your/audiobookshelf/library` with the absolute path to the folder Audiobookshelf reads its books from.**

3.  **Build and Run the Container**:
    Once your `docker-compose.yml` is configured, start the application:

    ```bash
    docker-compose up --build -d
    ```

    This command will build the Docker image (if it's your first time or if changes occurred), create the container, and run it in the background (`-d`).

### Usage

1.  **Access the Web Interface**:
    Open your web browser and go to `http://localhost:8000`. This is where you'll interact with the application.

2.  **Add Audiobooks to Input Folder**:
    Place your raw audiobook files into the **input folder** you configured (e.g., `/path/to/your/audiobook/downloads`). The application continuously monitors this folder for new content.

3.  **Review and Clarify**:
    Check the web interface (`http://localhost:8000`). If the tool needs more information to correctly identify an audiobook, it will present a simple form for you to provide clarification.

4.  **Automatic Organization**:
    After you confirm the details, the tool will automatically process the files, move them to the **output folder** (your Audiobookshelf library), and organize them into the correct directory structure.

-----

## 🤝 Contributing

This is an open-source project, and contributions are highly welcome\! If you have ideas for features, bug fixes, or improvements, please:

1.  Fork the repository.
2.  Create a new branch for your changes (`git checkout -b feature/my-new-feature`).
3.  Commit your modifications (`git commit -m 'Descriptive commit message'`).
4.  Push your branch (`git push origin feature/my-new-feature`).
5.  Open a Pull Request describing your changes.

-----


## Docker Setup

### Production Deployment

To build and run the production Docker image:

```bash
# Build the production image
docker build -t librarius-lexicon:prod .

# Run the container
docker run -p 8000:8000 librarius-lexicon:prod
```

### Development Environment

For local development, we use Docker Compose to manage the development environment:

```bash
# Start the development environment
docker-compose up

# Run tests
docker-compose run test

# Stop the development environment
docker-compose down
```

The development environment includes:
- Hot-reloading enabled Django development server
- All development dependencies installed
- Volume mounting for instant code changes
- Separate test environment for running tests

### Testing

Tests can be run in two ways:

1. Using Docker Compose (recommended):
```bash
docker-compose run test
```

2. Directly in the development container:
```bash
docker-compose exec web pytest
```

### Environment Variables

The following environment variables can be configured:

- `DJANGO_SETTINGS_MODULE`: Django settings module to use
- `DEBUG`: Enable/disable debug mode (1/0)
- `PYTHONUNBUFFERED`: Ensure Python output is sent straight to terminal
- `PYTHONDONTWRITEBYTECODE`: Prevent Python from writing .pyc files


## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file in the repository for more details.