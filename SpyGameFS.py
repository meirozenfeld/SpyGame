from kivy.app import App
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import random
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
# Seed the random number generator with a unique value
cred = credentials.Certificate("spygame.json")

cred = credentials.Certificate("google-services.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


words_array = []

class SharedVariables:
    selected_table = None
    selected_table_for_words = None

class MainWindow(Screen):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.num_players = ''
        self.num_spies = ''
        self.game_time = ''
        Clock.schedule_once(self.populate_table_spinner)

    def on_enter(self, *args):
        Clock.schedule_once(self.populate_table_spinner)

    def populate_table_spinner(self, *args):
        self.ids.table_spinner.values = []

        collections = db.collections()
        table_names = [collection.id for collection in collections]

        # Ensure that the widget exists in the ids dictionary before accessing it
        if 'table_spinner' in self.ids:
            self.ids.table_spinner.values = table_names

            # Access the Spinner widget
            spinner_widget = self.ids.table_spinner

            # Bind the on_release event to a callback method
            spinner_widget.bind(on_release=self.update_spinner_text)

            # Bind the on_text event to a callback method
            spinner_widget.bind(text=self.on_spinner_select)

            # Set the maximum height of the dropdown in pixels
            spinner_widget.dropdown_cls.max_height = dp(150)

    def update_spinner_text(self, instance):
        # Callback method to update spinner text
        instance.text = 'Select words list for the game'

    def on_spinner_select(self, instance, value):
        # Callback method to store the selected table in the shared variable
        SharedVariables.selected_table = value

    def show_popup(self, message):
        content = BoxLayout(orientation='vertical', spacing=10)
        label = Label(text=message, font_size=70)  # Adjust font_size as needed
        button = Button(text='OK', size_hint=(0.4, None), height=70, pos_hint={'center_x': 0.5})
        button.bind(on_press=lambda btn: popup.dismiss())
        content.add_widget(label)
        content.add_widget(button)

        popup = Popup(content=content, title='Invalid Input', size_hint=(0.7, 0.4), auto_dismiss=True)
        popup.open()

    def check_list(self):
        if SharedVariables.selected_table and SharedVariables.selected_table != 'First - select words list for manage words' and SharedVariables.selected_table != 'Select words list for the game':
            self.save_data()
            app = App.get_running_app()
            app.root.current = "names"
        else:
            self.show_popup("You must to Select words list")


    def check_conditions(self):
        num_players = self.ids.num_players_input.text
        num_spies = self.ids.num_spies_input.text
        game_time = self.ids.game_time_input.text

        if (num_spies and num_players and game_time):
            num_players=int(num_players)
            num_spies=int(num_spies)
            game_time=int(game_time)
            if num_players < 3:
                self.show_popup("The number of players \nmust be at least 3")
            else:
                if (num_spies > num_players or num_spies < 1):
                    self.show_popup("The number of spies must be between 1 to " + str(num_players))
            if(game_time <= 0):
                self.show_popup("Game time must be a positive number")



    def save_data(self):
        self.num_players = int(self.ids.num_players_input.text)
        self.num_spies = int(self.ids.num_spies_input.text)
        self.game_time = int(self.ids.game_time_input.text)
        print("num_players" + str(self.num_players))
        print("num_spies" + str(self.num_spies))
        print("game_time" + str(self.game_time))

    def reset_data(self):
        self.num_players = ''
        self.num_spies = ''
        self.game_time = ''


class WordsOrLists(Screen):
    pass


class WordsWindow(Screen):
    def __init__(self, **kwargs):
        super(WordsWindow, self).__init__(**kwargs)
        Clock.schedule_once(self.populate_table_spinner)

    def on_enter(self, *args):
        Clock.schedule_once(self.populate_table_spinner)

    def populate_table_spinner(self, *args):
        collections = db.collections()
        table_names = [collection.id for collection in collections if collection.id != 'All Lists']

        # Ensure that the widget exists in the ids dictionary before accessing it
        if 'table_spinner_for_words' in self.ids:
            self.ids.table_spinner_for_words.values = table_names

            # Bind the on_release event to a callback method
            self.ids.table_spinner_for_words.bind(on_release=self.update_spinner_text)

            # Bind the on_text event to a callback method
            self.ids.table_spinner_for_words.bind(text=self.on_spinner_select)

    def update_spinner_text(self, instance):
        # Callback method to update spinner text
        instance.text = 'Select a list'

    def on_spinner_select(self, instance, value):
        # Callback method to store the selected table in the shared variable
        SharedVariables.selected_table_for_words = value

    def add_word_submit(self):
        if SharedVariables.selected_table_for_words and SharedVariables.selected_table_for_words != 'Select a list':
            entered_word = self.ids.word_input.text
            reverse_word = self.reverse_letters_in_words(entered_word)
            if entered_word:
                doc_ref = db.collection(SharedVariables.selected_table_for_words).document(f'{reverse_word}')
                existing_word = doc_ref.get()

                if existing_word.exists:
                    self.ids.word_label.text = f'{reverse_word} already exists in {SharedVariables.selected_table_for_words} list'
                else:
                    doc_ref.set({'word': reverse_word})
                    self.ids.word_label.text = f'{reverse_word} Added to {SharedVariables.selected_table_for_words} list'

                self.ids.word_input.text = ''  # Clear the TextInput
            else:
                self.select_word_popup()
        else:
            self.select_list_popup()

    def show_words(self):
        if SharedVariables.selected_table_for_words:
            doc_ref = db.collection(SharedVariables.selected_table_for_words)
            records = doc_ref.stream()
            words = []

            # Exclude documents with the name 'default' from the list
            for r in records:
                if r.id != 'default':
                    words.append(r.id)

            # Display the combined result
            self.ids.word_label.text = '\n'.join(words)
        else:
            self.select_list_popup()

    def show_all_list_words(self):
        collections = db.collections()
        all_words = []

        for collection in collections:
            collection_name = collection.id

            # Skip 'All Lists' collection
            if collection_name == 'All Lists':
                continue

            doc_ref = db.collection(collection_name)
            records = doc_ref.stream()

            # Skip documents named 'default'
            words = [f'{r.id}' for r in records if r.id != 'default']
            all_words.append(f"\nList: {collection_name}\nWords: {', '.join(words)}")

        self.ids.word_label.text = '\n'.join(all_words)

    def delete_word(self):
        if SharedVariables.selected_table_for_words:
            entered_word = self.ids.word_input.text
            reverse_word = self.reverse_letters_in_words(entered_word)
            if entered_word:
                doc_ref = db.collection(SharedVariables.selected_table_for_words).document(reverse_word)

                # Check if the document is named 'default'
                if reverse_word.lower() == 'default':
                    self.ids.word_label.text = f'Cannot delete document named "default"'
                else:
                    existing_word = doc_ref.get()

                    if existing_word.exists:
                        doc_ref.delete()
                        self.ids.word_label.text = f'{reverse_word} Deleted'
                    else:
                        self.ids.word_label.text = f'{reverse_word} does not exist in {SharedVariables.selected_table_for_words} list'

                    self.ids.word_input.text = ''  # Clear the TextInput
            else:
                self.select_word_popup()
        else:
            self.select_list_popup()

    def delete_all_words(self, instance):
        if SharedVariables.selected_table_for_words:
            doc_ref = db.collection(SharedVariables.selected_table_for_words)
            records = doc_ref.stream()

            # Check each document before deletion
            for r in records:
                if r.id.lower() != 'default':  # Skip deleting the document named 'default'
                    r.reference.delete()

            self.ids.word_label.text = f'All words deleted from {SharedVariables.selected_table_for_words} list'
            self.dismiss_popup()
        else:
            self.select_list_popup()

    def select_word_popup(self):
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text="Enter a word please"))

        # Add buttons to the content
        btn_layout = BoxLayout(spacing=10)
        yes_button = Button(text='Ok',size_hint=(0.4, None), height=70, on_release=lambda instance: self.dismiss_popup())

        btn_layout.add_widget(yes_button)

        content.add_widget(btn_layout)

        # Create a new instance of Popup each time
        popup_size = (1000, 600)
        self.popup = Popup(title='Invalid input', content=content, size_hint=(0.7, 0.4), auto_dismiss=True)
        self.popup.open()

    def select_list_popup(self):
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text="Select a list please"))

        # Add buttons to the content
        btn_layout = BoxLayout(spacing=10)
        yes_button = Button(text='Ok', size_hint=(0.4, None), height=70, on_release=lambda instance: self.dismiss_popup())

        btn_layout.add_widget(yes_button)

        content.add_widget(btn_layout)

        # Create a new instance of Popup each time
        popup_size = (1000, 600)
        self.popup = Popup(title='List is missing', content=content, size_hint=(0.7, 0.4), auto_dismiss=True)
        self.popup.open()

    def reverse_letters_in_words(self, text):
        # Split the text into words
        words = text.split()

        # Reverse the order of words
        reversed_words = reversed(words)

        # Reverse the letters in each word
        reversed_words_with_letters = [''.join(reversed(word)) for word in reversed_words]

        # Join the reversed words back into a single string
        reversed_text = ' '.join(reversed_words_with_letters)

        return reversed_text

    def delete_all_words_popup(self):
        if SharedVariables.selected_table_for_words:

            content = BoxLayout(orientation='vertical', spacing=10)
            content.add_widget(Label(text=f"Are you sure you want to \ndelete all words from {SharedVariables.selected_table_for_words} list?", font_size=60))

            # Add buttons to the content
            btn_layout = BoxLayout(spacing=10)
            yes_button = Button(text='Yes', size_hint=(0.4, None), height=70, on_release=self.delete_all_words)
            no_button = Button(text='No', size_hint=(0.4, None), height=70, on_release=lambda instance: self.dismiss_popup())

            btn_layout.add_widget(yes_button)
            btn_layout.add_widget(no_button)

            content.add_widget(btn_layout)

            # Create a new instance of Popup each time
            popup_size = (1000, 600)
            self.popup = Popup(title='Confirmation', content=content, size_hint=(0.8, 0.8))
            self.popup.open()
        else:
            self.select_list_popup()


    def dismiss_popup(self):
        self.popup.dismiss()


class ListsWindow(Screen):

    def add_list_submit(self):
        # Get the entered list from the TextInput
        entered_list = self.ids.list_input.text

        if entered_list:
            # Check if the list already exists
            collection_ref = db.collection(entered_list)
            existing_list = collection_ref.document('default').get()

            if existing_list.exists:
                self.ids.list_label.text = f'{entered_list} already exists'
            else:
                # Insert the list into Firestore with 'default' as the document name
                collection_ref.document('default').set({'word': ''})
                self.ids.list_label.text = f'{entered_list} Added'

            self.ids.list_input.text = ''  # Clear the TextInput
        else:
            self.select_list_popup()

    def show_lists(self):
        collections = db.collections()
        list1 = ''

        for collection in collections:
            # Check if the collection name is not 'All Lists'
            if collection.id != 'All Lists':
                list1 = f'{list1}\n{collection.id}'

        self.ids.list_label.text = list1

    def delete_list_confirm(self):
        entered_list = self.ids.list_input.text
        if entered_list:
            content = BoxLayout(orientation='vertical', spacing=10)

            label = Label(text="Enter password", size_hint_y=None, height=40)
            self.pass_input = TextInput(password=True, size_hint=(0.7, None), height=70,pos_hint={'center_x': 0.5})

            # Add buttons to the content
            btn_layout = BoxLayout(spacing=10, size_hint_y=None)
            ok_button = Button(text='Ok', background_color=(0, 0.5, 0, 1),size_hint=(0.7, 0.6),
                               on_release=lambda instance: self.check_pass_delete_list(self.pass_input.text))
            cancel_button = Button(text='Cancel',size_hint=(0.7, 0.6), on_release=lambda instance: self.dismiss_popup())

            btn_layout.add_widget(cancel_button)
            btn_layout.add_widget(ok_button)


            content.add_widget(label)
            content.add_widget(self.pass_input)
            content.add_widget(btn_layout)

            popup_size = (1000, 600)

            self.popup = Popup(title='Password Confirmation', content=content, size_hint=(0.7, 0.4), auto_dismiss=True)
            self.popup.open()
        else:
            self.select_list_popup()


    def delete_list(self):
        # Get the entered list from the TextInput
        entered_list = self.ids.list_input.text

        if entered_list:
            # Check if the list exists in the collection
            collection_ref = db.collection(entered_list)
            existing_list = collection_ref.get()

            if existing_list:
                # Delete the entire collection
                for document in existing_list:
                    document.reference.delete()
                self.ids.list_label.text = f'{entered_list} Deleted'
            else:
                self.ids.list_label.text = f'{entered_list} does not exist'

            self.ids.list_input.text = ''  # Clear the TextInput
        else:
            self.select_list_popup()

    def check_pass_delete_list(self, password):
        if password == '9941667':
            self.delete_list()
            self.dismiss_popup()
        else:
            self.popup.title = 'Invalid Password'

    def dismiss_popup(self):
        self.popup.dismiss()

    def delete_all_lists(self):
        collections = db.collections()

        # Iterate through each collection and delete it, except 'All Lists'
        for collection in collections:
            if collection.id != 'All Lists':
                for document in collection.get():
                    document.reference.delete()

        self.ids.list_label.text = 'All lists deleted'
        self.dismiss_popup()

    def delete_all_list_confirm(self):
        content = BoxLayout(orientation='vertical', spacing=10)

        label = Label(text="Enter password", size_hint_y=None, height=40)
        self.pass_input = TextInput(password=True, size_hint=(0.7, None), height=70, pos_hint={'center_x': 0.5})

        # Add buttons to the content
        btn_layout = BoxLayout(spacing=10, size_hint_y=None)
        ok_button = Button(text='Ok', background_color=(0, 0.5, 0, 1), size_hint=(0.7, 0.6),
                                   on_release=lambda instance: self.check_pass_delete_all_list(self.pass_input.text))
        cancel_button = Button(text='Cancel', size_hint=(0.7, 0.6), on_release=lambda instance: self.dismiss_popup())

        btn_layout.add_widget(cancel_button)
        btn_layout.add_widget(ok_button)


        content.add_widget(label)
        content.add_widget(self.pass_input)
        content.add_widget(btn_layout)

        popup_size = (400, 250)
        self.popup = Popup(title='Password Confirmation', content=content, size_hint=(0.7, 0.4), auto_dismiss=True)
        self.popup.open()

    def check_pass_delete_all_list(self, password):
        if password == '9941667':
            self.delete_all_lists()
            self.dismiss_popup()
        else:
            self.popup.title = 'Invalid Password'

    def select_list_popup(self):
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text="List name is missing", font_size=70))

        # Add buttons to the content
        btn_layout = BoxLayout(spacing=10)
        yes_button = Button(text='Ok',size_hint=(0.6, 0.5), on_release=lambda instance: self.dismiss_popup())

        btn_layout.add_widget(yes_button)
        content.add_widget(btn_layout)

        # Create a new instance of Popup each time
        popup_size = (300, 200)
        self.popup = Popup(title='Inavalid input', content=content, size_hint=(0.7, 0.5))
        self.popup.open()

class NamesWindow(Screen):

    num_players = NumericProperty(0)
    num_spies = NumericProperty(0)
    player_names = []  # List to store entered player names
    text_inputs = []  # List to store TextInput widgets
    text_inputs2_len = num_players
    text_inputs2 = []
    random_spies = []

    def on_enter(self):
        self.clear_widgets()
        main_window = self.manager.get_screen('main')
        self.num_players = main_window.num_players
        self.num_spies = main_window.num_spies

        self.random_spies = random.sample(range(self.num_players), self.num_spies)

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        names_label = Label(text='Enter player names (In English):', size_hint_y=None, font_size=25)

        scroll_view = ScrollView(do_scroll_x=False, do_scroll_y=True, size_hint_x=0.5, pos_hint = {'center_x': 0.5})
        grid_layout = GridLayout(cols=1, spacing=15, size_hint_y=None)

        for i in range(1, self.num_players + 1):
            text_input = TextInput(
                hint_text='Player ' + str(i) + ' Name',
                multiline=False,
                size_hint=(None, None),  # Set the desired size_hint for width
                height=130,
                width=1000,  # Set the desired width
                font_size=25
            )
            text_input.bind(text=self.on_text_changed)
            grid_layout.add_widget(text_input)
            self.text_inputs.append(text_input)

        grid_layout.bind(minimum_height=grid_layout.setter('height'))

        scroll_view.add_widget(grid_layout)
        layout.add_widget(names_label)
        layout.add_widget(scroll_view)

        # Center the grid_layout horizontally
        grid_layout.pos_hint = {'center_x': 0.5}

        start_game_button = Button(
            text='Start Game',
            size_hint_y=None,
            height=80,
            on_release=self.start_game,
            size_hint=(0.7, 0.27),  # Set size hints for width and height
            pos_hint={'center_x': 0.5},  # Set position hint for centering along x-axis
            disabled=True,  # Initially disabled

        )

        layout.add_widget(start_game_button)
        # Save a reference to the start_game_button for later access
        self.ids.start_game_button = start_game_button

        back_to_main = Button(
            text='Back',
            height=80,
            size_hint=(0.7, 0.27),  # Set size hints for width and height
            pos_hint={'center_x': 0.5},  # Set position hint for centering along x-axis
            on_release=self.back_main,

        )
        layout.add_widget(back_to_main)

        self.add_widget(layout)

    def back_main(self, *args):
        self.reset_data()
        app = App.get_running_app()
        app.root.current = "main"

    def start_game(self, *args):
        self.player_names = [text_input.text for text_input in self.text_inputs]
        for name in self.player_names:
            print("name: ", name)

        app = App.get_running_app()
        app.root.current = "game"


    def on_text_changed(self, instance, value):
        # Check if all TextInput widgets are filled to enable the button
        all_filled = all(text_input.text for text_input in self.text_inputs)
        start_game_button = self.ids.start_game_button
        start_game_button.disabled = not all_filled

    def create_scroll_names(self):
        main_window = self.manager.get_screen('main')
        print("num_players" + str(self.num_players))
        print("num_spies" + str(main_window.num_spies))
        print("game_time" + str(main_window.game_time))

    def reset_data(self):
        self.player_names = []  # List to store entered player names
        self.text_inputs = []  # List to store TextInput widgets
        self.random_spies = []



class GameWindow(Screen):
    def __init__(self, **kwargs):
        super(GameWindow, self).__init__(**kwargs)
        self.current_player_index = 0
        self.next_button = Button(text='Next Player', disabled=True)

    def on_enter(self):
        try:
            main_window = self.manager.get_screen('main')
            self.num_players = main_window.num_players
            self.num_spies = main_window.num_spies
            names_window = self.manager.get_screen('names')
            self.player_names = names_window.player_names
            self.random_spies = names_window.random_spies

            # Seed the random number generator with a unique value
            random.seed()
            words_array = []

            if SharedVariables.selected_table == 'All Lists':
                # Fetch all collections
                collections = db.collections()

                for collection in collections:
                    if collection.id != 'All Lists':
                        # Fetch all documents from each collection
                        documents = collection.get()
                        for doc in documents:
                            if doc.id != 'default':
                                words_array.append(doc.id)
                print ("word array All Lists: ", words_array)
            elif SharedVariables.selected_table:
                # Fetch all documents from the selected collection
                collection_ref = db.collection(SharedVariables.selected_table)
                documents = collection_ref.get()
                words_array = [doc.id for doc in documents if doc.id != 'default']
                print(f'word array from {SharedVariables.selected_table} : ', words_array)


            else:
                print("Selected table is not set.")

            print("*********LIST: ", SharedVariables.selected_table)
            random.seed()
            self.random_word = random.choice(words_array)
            self.update_layout()

        except Exception as e:
            import traceback
            traceback.print_exc()  # Print the traceback to console
            # logging.exception(f"Error in on_enter of GameWindow: {e}")

    def update_layout(self):
        try:
            self.clear_widgets()

            self.value_label = Label(text='', font_name='Arial', font_size=80)
            show_spy = Button(text="Show Spy", size_hint=(0.6, 0.4), pos_hint={'center_x': 0.5}, on_release=self.show_spy)

            if self.current_player_index < len(self.player_names):
                current_player_name = self.player_names[self.current_player_index]

                layout = BoxLayout(orientation='vertical', spacing=10)
                player_label = Label(text=current_player_name, font_size=80)
                if self.current_player_index < len(self.player_names) - 1:
                    self.next_button = Button(text='Next Player', size_hint=(0.6, 0.4), pos_hint={'center_x': 0.5}, on_release=self.next_player, disabled=True)
                else:
                    self.next_button = Button(text='Start Time', size_hint=(0.6, 0.4), pos_hint={'center_x': 0.5}, on_release=self.next_player, disabled=True)

                layout.add_widget(player_label)
                layout.add_widget(self.value_label)
                layout.add_widget(show_spy)
                layout.add_widget(self.next_button)

                self.add_widget(layout)
            else:
                # All players displayed, navigate to the next screen or perform other actions
                app = App.get_running_app()
                app.root.current = "time"
        except Exception as e:
            import traceback
            traceback.print_exc()  # Print the traceback to console
            # logging.exception(f"Error in update_layout of GameWindow: {e}")

    def next_player(self, *args):
        try:
            self.current_player_index += 1
            self.update_layout()
        except Exception as e:
            import traceback
            traceback.print_exc()  # Print the traceback to console
            # logging.exception(f"Error in next_player of GameWindow: {e}")

    def show_spy(self, instance):
        try:
            # Update the Label text when the button is clicked
            if self.current_player_index in self.random_spies:
                self.value_label.text = "לגרמ"
            else:
                self.value_label.text = self.random_word
            self.next_button.disabled = False
        except Exception as e:
            import traceback
            traceback.print_exc()  # Print the traceback to console
            # logging.exception(f"Error in show_spy of GameWindow: {e}")

    def reset_data(self):
        try:
            self.current_player_index = 0
            self.random_word = ''
        except Exception as e:
            import traceback
            traceback.print_exc()  # Print the traceback to console
            # logging.exception(f"Error in reset_data of GameWindow: {e}")

class TimeWindow(Screen):
    def on_enter(self):
        self.clear_widgets()

        main_window = self.manager.get_screen('main')
        self.num_players = main_window.num_players
        self.num_spies = main_window.num_spies
        self.game_time = main_window.game_time * 60

        # Initialize remaining time
        self.remaining_time = self.game_time

        # Create a Label to display the remaining time
        self.time_label = Label(
            text=str(self.format_time(self.remaining_time)),
            font_size=100,
            color=(0, 1, 0, 1),  # Set the color to green (RGB values and alpha)
            pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Center the label

        )

        # Create a Button to go to the next screen
        next_screen_button = Button(
            text="End game and show spies",
            on_release=self.next_screen,
            size_hint=(0.7, 0.2),  # Adjust the values as needed
            pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Center the button
        )

        # Add widgets to the layout
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.time_label)
        # Create an empty circle around the time_label

        layout.add_widget(next_screen_button)

        # Schedule the update_time function to be called every second
        Clock.schedule_interval(self.update_time, 1)

        # Set the layout as the TimeWindow content
        self.add_widget(layout)


    def update_time(self, dt):
        # Update the remaining time and update the label text
        if self.remaining_time == 7:
            sound = SoundLoader.load('sounds/end_sound.mp3')
            if sound:
                sound.play()

        self.remaining_time -= 1
        self.time_label.text = self.format_time(self.remaining_time)

        # Check if the time has reached 0
        if self.remaining_time == 0:
            # Stop the clock when the time is up
            Clock.unschedule(self.update_time)


    def format_time(self, seconds):
        # Format seconds into MM:SS
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes:02d}:{seconds:02d}"

    def next_screen(self, *args):
        # Go to the next screen
        app = App.get_running_app()
        app.root.current = "end"

    def reset_data(self):
        self.num_players = 0
        self.num_spies = 0
        self.game_time = 0
        self.remaining_time = 0
        self.time_label.text = ''
        Clock.unschedule(self.update_time)
        # Clock.schedule_interval(self.update_time, 1)

class EndGameWindow(Screen):
    def on_enter(self):
        self.clear_widgets()
        main_window = self.manager.get_screen('main')
        self.num_players = main_window.num_players
        self.num_spies = main_window.num_spies
        game_window = self.manager.get_screen('game')
        self.random_word = game_window.random_word
        names_window = self.manager.get_screen('names')
        self.player_names = names_window.player_names
        self.random_spies = names_window.random_spies
        self.spies = []

        layout = BoxLayout(orientation='vertical')
        self.spy_header = Label(text="The spies:", font_size=80, size_hint_y=None)
        layout.add_widget(self.spy_header)

        spy_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)

        i = 0
        for n in self.player_names:
            if i in self.random_spies:
                spy_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), spacing=8)
                image = Image(source='images/spy_icon3.png', size=(40, 40))  # Adjust the size accordingly
                spy_name = Label(text=n, font_size=80, color=(1, 0, 0, 1))
                spy_layout.add_widget(image)
                spy_layout.add_widget(spy_name)
                widget2 = Widget()
                spy_layout.add_widget(widget2)
                spy_box.add_widget(spy_layout)

                print("n spy: ", n)
            i += 1

        # Set the height of spy_box based on its children
        spy_box_height = sum(child.height for child in spy_box.children)
        spy_box.height = spy_box_height

        scroll_view = ScrollView(size_hint=(1, 0.8), pos_hint={'center_y': 0.5})
        scroll_view.add_widget(spy_box)
        layout.add_widget(scroll_view)

        self.widget = Widget(size_hint=(0.2, 0.1))
        self.word_header = Label(text=f"{self.random_word} :איה הלימה", font_name='Arial', font_size=80,
                                 size_hint_y=None)

        # layout.add_widget(self.widget)

        self.end_button = Button(
            text='New Game',
            on_release=self.new_game,
            size_hint=(0.8, None),  # Adjust the width
            height=100,  # Adjust the height
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        layout.add_widget(self.word_header)
        layout.add_widget(self.widget)
        layout.add_widget(self.end_button)

        self.add_widget(layout)
    def reset_data(self):
        self.spy_name=''
        self.spies = []
        self.spy_header=''
        self.random_word = " "

    def new_game(self, *args):
        # reset game
        main_window = self.manager.get_screen('main')
        main_window.reset_data()
        names_window = self.manager.get_screen('names')
        names_window.reset_data()
        game_window = self.manager.get_screen('game')
        game_window.reset_data()
        time_window = self.manager.get_screen('time')
        time_window.reset_data()
        self.reset_data()
        # Go to the main screen
        app = App.get_running_app()
        app.root.current = "main"


class WindowManager(ScreenManager):
    pass


# Building .kv file
kv = Builder.load_file("SpyGameFS.kv")


class SpyApp(App):
    def build(self):
        return kv


if __name__ == '__main__':
    SpyApp().run()