import enaml
from web.apps.web_app import WebApplication

with enaml.imports():
    from index import Index


def main():
    # Must have at least one application
    app = WebApplication()

    # Generate index.html from index.enaml
    with open('index.html', 'wb') as f:
        f.write(Index().render())

if __name__ == '__main__':
    main()
