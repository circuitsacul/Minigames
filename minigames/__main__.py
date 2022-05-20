import sys

from .bot import Minigames


def usage() -> None:
    print("Usage: ./run.sh python [--migrations]")
    exit(1)


def main() -> None:
    if len(sys.argv) > 1:
        if sys.argv[1] == "--migrations":
            bot = Minigames()
            bot.database.create_migrations()
            print("Migrations created.")
            exit(0)
        else:
            usage()
    bot = Minigames()
    bot.run()


if __name__ == "__main__":
    main()
