import enaml
from web.core.app import WebApplication

with enaml.imports():
    from index import Index


def main():
    # Must have at least one application
    app = WebApplication()

    # Generate index.html from index.enaml
    # See lxml docs on tostring
    options = {
        'pretty_print': True,
    }
    with open('index.html', 'w') as f:
        f.write(Index().render(render_options=options))

if __name__ == '__main__':
    main()
