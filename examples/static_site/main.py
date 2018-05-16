import enaml
from web.impl.lxml_app import LxmlApplication

def main():
    # Must have at least one application
    app = LxmlApplication()

    # Generate index.html from index.enaml
    with enaml.imports():
        from pages import Index

        with open('index.html', 'w') as f:
            f.write(Index().render())

if __name__ == '__main__':
    main()
