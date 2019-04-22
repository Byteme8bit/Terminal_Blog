__author__ = "byteme8bit"

# Module imports
import pymongo
from time import strftime
from os import listdir, fsencode, fsdecode, rename
from sys import argv


# File/program imports


class Post(object):
    """
    An instance of Post() contains the pertinent information for a 'post'. Includes: Title, Author, Content, Date/Time.
    """

    def __init__(self, title=None, author=None, content=None, time_start=None):
        """
        Initialize a post to be published to database. Saved to local disk if program error or exit before publish
        complete.
        :param title: Title of the post
        :param author: Author to be credited
        :param content: Body of the post
        :param time_start: Time the post was written.
        """

        self.title = title if title is not None else input('\nPost Title?: ')
        self.author = author if author is not None else input('\nAuthor?: ')
        self.content = content if content is not None else input('\nWhat do you want to say?: ')
        self.time_started = time_start if time_start is not None else strftime('%m-%d-%Y_%H:%M:%S')
        self.published = False

    def __repr__(self):
        """
        Displays more human-readable version of an instance of Post() to be displayed in terminal.
        :return:
        """

        return f"\n{self.title}\n" \
            f"\n{self.content}\n" \
            f"Written by {self.author} at {self.time_started}"

    def __str__(self):
        """
        Displays more program-readable version of an instance of Post() to be saved to cache.
        Can be used later to rebuild a new instance of Post() and then publish.
        :return:
        """

        return f"{self.title}\n" \
            f"{self.author}\n" \
            f"{self.time_started}\n" \
            f"{self.content}\n"


class Program:
    """
    An instance of Program() contains the necessary information to connect to and interact with a MongoDB database in
    order to be used as a modest terminal blog post of sorts. Asks for Title and Content from user and logs an Author
    name and the time/date was written. This information is contained in the attributes of a separate class, Post().
    """

    def __init__(self):
        """
        Initialize an instance of Program() which connects to a pre-configured MongoDB database, either local or cloud.
        Displays the existing collections in the connected database to allow connecting to current collection or
        creating a new one.
        """

        print('\n\n\n\n-[ Press Ctrl + C to end the program. ]-\n')

        try:
            # Local database
            self.database_uri = "mongodb://127.0.0.1:27017"

            # Cloud database
            # self.database_uri = "mongodb+srv://

            # Database info
            self.client = pymongo.MongoClient(self.database_uri)
            self.database = self.client['terminal_blog']

            # Shows the currently connected database
            print(f'\nOpening database: {self.database.name}')

            # Builds a sorted list of existing collections in current database
            self.database_collections = sorted(self.database.list_collection_names())

            # Iterates over the sorted list and prints out the name of each collection.
            print(f'\nCurrent collections in {self.database.name}:')
            for collection in self.database_collections:
                print(f"'{collection}'\n")

            # Empty variable to initalize
            collection_name = ''

            # Initializer variable to start below loop
            confirm = 'n'
            while confirm == 'n':
                collection_name = input('\nType the name of the collection you wish to connect to. '
                                        '(To create new entry just type non-existent name): ')

                # Has user confirm if new collection should be created
                if collection_name not in self.database_collections:
                    print(f'\n"{collection_name}" does not exist yet. Do you want to create a new collection? (Y / N)')
                    confirm = input('Answer: ').lower().rstrip()

                    # Validates user input
                    while confirm not in 'yn':
                        print('\nSelect valid response. Y or N')
                        confirm = input('Answer: ').lower().rstrip()

                else:
                    break

            # Shows the currently connected collection
            words = 'Opening', 'Creating'
            print(f'\n{words[0] if confirm == "n" else words[1]} collection: {collection_name}')

            self.collection = self.database[collection_name]

            # Program "cache"
            self.cache_loc = '.\\cached_posts\\'
            self.post_cache = []

        except Exception as e:
            self.log_error(e)

    def __del__(self):
        """
        Defines what tasks should be done when clean up of Program() is called.
        :return:
        """
        self.save_cache()
        print('\nProgram exiting.\n')

    def run(self):
        """
        'Normal' operation. Asks for a number of posts to add and then initializes Post() one by one until quota met.
        :return:
        """
        for i in range(int(input('\nHow many posts would you like to add?: '))):
            try:
                self.publish(Post())

            except Exception as e:
                self.log_error(e)

    def cache_to_db(self):
        """
        Defines the processing of cached posts stored in the cache_loc. Iterates over each files and then each post
        within. Rebuilds Post(), presents repr(post) to user in terminal, asks to publish.
        :return:
        """

        # Iterate over the cache_loc folder and add each file to a list.
        try:
            files = [fsdecode(file) for file in listdir(fsencode(self.cache_loc))]

        except Exception as e:
            self.log_error(e)

        print('\nStart of iteration through cached files:\n')

        # Iterate over each file
        try:
            for item in files:

                # Open the file, grab the lines of text
                lines = [line.rstrip() for line in open(fsencode(self.cache_loc + item))]

                # Count the posts in the file
                post_count = len(lines) // 4
                print(f'\n{item} contains {post_count} posts:\n')

                # Iterate over the imported lines
                for i in range(0, len(lines), 4):

                    # Rebuild Post using the imported text
                    new_post = Post(title=lines[i],
                                    author=lines[i + 1],
                                    time_start=lines[i + 2],
                                    content=lines[i + 3])

                    self.publish(new_post)

                # Moves the processed file from cache_loc to archive folder, any unpublished posts are added to new
                # cache
                print(f'Moving {item} from {self.cache_loc} to .\\archive\\')
                rename(fsencode(self.cache_loc + item), fsencode('.\\archive\\' + item))

            print('\nFinished iterating through all posts in all files')

        except Exception as e:
            self.log_error(e)

    def publish(self, post):
        """
        Defines the process to publish a Post()
        :param post: a Post() instance
        :return:
        """

        # Add post to cache
        self.post_cache.append(post)

        # Present post to user in terminal
        print(repr(post))

        # Ask to publish
        publish_check = input('\nDo you want to publish this post to the database? (Y/N): ').lower().strip()
        print()

        # Validates user input
        pos_ans = 'yn'
        while publish_check not in pos_ans:
            print('\nSelect a valid answer.\n')
            publish_check = input('\nDo you want to publish this post to the database? (Y/N): ').lower().strip()
            print()

        # If user wants to publish
        if publish_check == 'y':
            try:
                # Insert a new row containing a dictionary item using post attributes.
                self.collection.insert_one({'Title': post.title,
                                            'Author': post.author,
                                            'Date': post.time_started,
                                            'Post': post.content})

                post.published = True

                # Remove post from cache if successful
                self.post_cache.remove(post)

                print('\nPost has been published.\n')

            except Exception as e:
                self.log_error(e)

            finally:
                pass

        # If user does not want to publish
        else:
            print('You chose not to publish the post.\n')
            post.published = False

    def save_cache(self):
        """
        Defines the process to save the post_cache to local disk.
        :return:
        """
        try:
            if self.post_cache:
                print('Saving cached posts to local disk...\n')

                # Creates a file with current date and time to ensure unique file name
                cache_file = f'{strftime("%m_%d_%Y_%H%M%S")}.dat'

                # Create/open the file
                with open(fsencode(self.cache_loc + cache_file), 'a') as cache:

                    # Iterate over the posts in the post_cache
                    for post in self.post_cache:

                        # Write the program readable version to cache
                        cache.write(str(post))

                # Log date, time and number of posts cached.
                total_posts = len(self.post_cache)
                a = 'post', 'posts'
                with open('.\\logs\\log.txt', 'a') as log:
                    log.write(f"{strftime('%m-%d-%Y %H:%M:%S')} | "
                              f'{total_posts} total {a[0] if total_posts == 1 else a[1]} created but not published.\n')

        # In testing, this error was received if the post_cache was empty. This prevents ugly error and processes
        # cleanly.
        except AttributeError:
            print(f'\nProgram cache empty. Nothing to save.\n')

    def log_error(self, error):
        # Print error to terminal cleanly
        print(error)

        # Open log file and write the error, date and time to file
        with open(f'.\\logs\\{strftime("%m_%d")}_error_log.txt', 'a') as log:
            log.write(f"Error: {strftime('%m-%d-%Y %H:%M:%S')} | {error}\n")

        quit(20)


if __name__ == "__main__":
    while True:
        try:
            if argv[1] in ['normal', 'norm', 'n', 'run']:
                Program().run()

            elif argv[1] in ['publish cache', 'publish', 'pc']:
                Program().cache_to_db()

            else:
                print(f'\n"{argv[1]}" is an unrecognized argument.')

        except KeyboardInterrupt:
            print('\n\nUser ended session. Ending tasks...\n')
            quit(99)
