from kivy.app import App
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.text import LabelBase
import random

# Seed the random number generator with a unique value
random.seed()
file_path = 'words.txt'
words_array = []

# Open the file in read mode with explicit encoding
with open(file_path, 'r', encoding='utf-8') as file:
    # Iterate through each line in the file
    for line in file:
        words_array.append(line.strip())

words_array = [word[::-1] for word in words_array]
# Output the array
print("Data Array:")
for data in words_array:
    print(data)

# # Choose a random value from the words_array
# random_word = random.choice(words_array)
#
# # Output the random word
# print("Random Word:", random_word)


class MainWindow(Screen):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.num_players = ''
        self.num_spies = ''
        self.game_time = ''


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

class NamesWindow(Screen):

    num_players = NumericProperty(0)
    num_spies = NumericProperty(0)
    player_names = []  # List to store entered player names
    text_inputs = []  # List to store TextInput widgets
    random_spies = []

    def on_enter(self):
        self.clear_widgets()
        main_window = self.manager.get_screen('main')
        self.num_players = main_window.num_players
        self.num_spies = main_window.num_spies

        self.random_spies = random.sample(range(self.num_players ), self.num_spies)

        print("random", self.random_spies)

        layout = BoxLayout(orientation='vertical', spacing=8, padding=10)
        names_label = Label(text='Enter player names')

        # Create a ScrollView
        scroll_view = ScrollView(do_scroll_x=False, do_scroll_y=True)

        # Create a GridLayout inside ScrollView for TextInputs
        grid_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)

        # Add TextInputs to GridLayout
        for i in range(1, self.num_players + 1):
            text_input = TextInput(
                hint_text='Player ' + str(i) + ' Name',
                multiline=False,
                size_hint_y=None,
                height=40
            )
            grid_layout.add_widget(text_input)
            # text_input.bind(on_text=self.on_text_changed)  # Bind the method to each TextInput
            self.text_inputs.append(text_input)

        # Set the height of the GridLayout
        grid_layout.bind(minimum_height=grid_layout.setter('height'))

        # Add the GridLayout to the ScrollView
        scroll_view.add_widget(grid_layout)
        layout.add_widget(names_label)

        # Add the ScrollView to the BoxLayout
        layout.add_widget(scroll_view)

        # Add the "Start Game" button below the ScrollView
        start_game_button = Button(
            text='Start Game',
            size_hint_y=None,
            height=60,
            on_release=self.start_game
        )
        layout.add_widget(start_game_button)

        # Add the BoxLayout to the NamesWindow
        self.add_widget(layout)

    def start_game(self, *args):
        # Access the text values from TextInput widgets
        self.player_names = [text_input.text for text_input in self.text_inputs]

        # Print the player names
        for name in self.player_names:
            print("name: ", name)
        app = App.get_running_app()
        app.root.current = "game"

    def on_text_changed(self, instance, value):
        # Update the variable whenever the text in TextInput changes
        pass

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


    def on_enter(self):
        main_window = self.manager.get_screen('main')
        self.num_players = main_window.num_players
        self.num_spies = main_window.num_spies
        names_window = self.manager.get_screen('names')
        self.player_names=names_window.player_names
        self.random_spies=names_window.random_spies
        # Seed the random number generator with a unique value
        random.seed()
        self.random_word = random.choice(words_array)
        self.update_layout()

        # main_window = self.manager.get_screen('main')
        # self.num_players = main_window.num_players
        # self.num_spies = main_window.num_spies
        # names_window = self.manager.get_screen('names')
        # self.player_names=names_window.player_names
        # for name in self.player_names:
        #     print("name2: ", name)
    # print("second " + str(num_players))
    def update_layout(self):
        self.clear_widgets()

        self.value_label = Label(text='', font_name='Arial', font_size=40)
        show_spy = Button(text="Show Spy", on_release=self.show_spy)


        if self.current_player_index < len(self.player_names):
            current_player_name = self.player_names[self.current_player_index]

            layout = BoxLayout(orientation='vertical')
            player_label = Label(text=current_player_name, font_size=40)
            if(self.current_player_index == len(self.player_names) - 1 ):
                next_button = Button(text='Start Time', on_release=self.next_player)
            else:
                next_button = Button(text='Next Player', on_release=self.next_player)

            layout.add_widget(player_label)
            layout.add_widget(self.value_label)
            layout.add_widget(show_spy)
            layout.add_widget(next_button)

            self.add_widget(layout)
        else:
            # All players displayed, navigate to the next screen or perform other actions
            app = App.get_running_app()
            app.root.current = "time"

    def next_player(self, *args):

        self.current_player_index += 1
        self.update_layout()

    def show_spy(self, instance):
        # Update the Label text when the button is clicked
        if self.current_player_index in self.random_spies:
            self.value_label.text = "לגרמ"
        else:
            self.value_label.text = self.random_word

    def reset_data(self):
        self.current_player_index = 0
        self.random_word = ''
class TimeWindow(Screen):
    def on_enter(self):
        self.clear_widgets()

        main_window = self.manager.get_screen('main')
        self.num_players = main_window.num_players
        self.num_spies = main_window.num_spies
        self.game_time = main_window.game_time * 60
        # self.game_time = 10

        # Initialize remaining time
        self.remaining_time = self.game_time
        # self.remaining_time = 10


        # Create a Label to display the remaining time
        self.time_label = Label(text=str(self.format_time(self.remaining_time)), font_size=40)

        # Create a Button to go to the next screen
        next_screen_button = Button(text="End game and show spies", on_release=self.next_screen)

        # Add widgets to the layout
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.time_label)
        layout.add_widget(next_screen_button)

        # Schedule the update_time function to be called every second
        Clock.schedule_interval(self.update_time, 1)

        # Set the layout as the TimeWindow content
        self.add_widget(layout)

    def update_time(self, dt):
        # Update the remaining time and update the label text
        if self.remaining_time == 7:
            sound = SoundLoader.load('end_sound.mp3')
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
        names_window = self.manager.get_screen('names')
        self.player_names = names_window.player_names
        self.random_spies = names_window.random_spies
        self.spies = []

        layout = BoxLayout(orientation='vertical')
        self.spy_header = Label(text="The spies:", font_size=60)
        layout.add_widget(self.spy_header)

        i=0
        for n in self.player_names:
            if i in self.random_spies:
                self.spy_name = Label(text=n, font_size=40)
                layout.add_widget(self.spy_name)
                print("n spy: ", n)
            i = i + 1

        self.end_button = Button(text='New Game', on_release=self.new_game)
        layout.add_widget(self.end_button)

        self.add_widget(layout)
    def reset_data(self):
        self.spy_name=''
        self.spies = []
        self.spy_header=''

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
kv = Builder.load_file("SpyApp.kv")


class SpyApp(App):
    def build(self):
        return kv

if __name__ == '__main__':
    SpyApp().run()

# for i in range(1, self.num_players + 1):
#     self.players.append('Player ' + str(i) + ' Name')
# layout = BoxLayout(orientation='vertical', spacing=8)
# scroll_view = ScrollView()
# grid_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
#
# grid_layout.bind(minimum_height = layout.setter('height'))
# for i in range(1, self.num_players + 1):
#     text_input = TextInput(
#         hint_text='Player ' + str(i) + ' Name',
#         multiline=False,
#         size_hint_y=None,
#         height=40
#     )
#     grid_layout.add_widget(text_input)
#
#
# scroll_view.add_widget(grid_layout)
# layout.add_widget(scroll_view)
# self.add_widget(layout)
# layout = BoxLayout(orientation='vertical', spacing=5)
#
# # Create a ScrollView
# scroll_view = ScrollView()

# # Create a GridLayout inside ScrollView for TextInputs
# grid_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
# grid_layout.bind(minimum_height=grid_layout.setter('height'))
#
# # Adjust height and spacing
# text_input_height = '30dp'
# text_input_spacing = 5
#
# # Add TextInputs to GridLayout (adjust this loop as needed)
# for i in range(1, self.num_players + 1):
#     text_input = TextInput(
#         hint_text='Player ' + str(i) + ' Name',
#         multiline=False,
#         size_hint_y=None,
#         height=text_input_height
#     )
#     grid_layout.add_widget(text_input)
#
# # Add the GridLayout to the ScrollView
# scroll_view.add_widget(grid_layout)
#
# # Add the ScrollView to the BoxLayout
# layout.add_widget(scroll_view)
#
# # Add the BoxLayout to the NamesWindow
# self.add_widget(layout)
