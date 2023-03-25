from datetime import datetime
from logging.config import listen
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha

#  Speech engine Init
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)  # 0 = male, 1 = female
activationWord = "computer"

# config browser
# set path to chrome
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

# Wolfram Alpha client set up
app_id = "RW83UU-VQ92PHEGJU"
wolfram_client = wolframalpha.Client(app_id)


def speak(text, rate=120):
    engine.setProperty("rate", rate)
    engine.say(text)
    engine.runAndWait()


def parse_command():
    listener = sr.Recognizer()
    print("Listening...")

    with sr.Microphone() as source:
        listener.pause_threshold = 2
        input_speech = listener.listen(source)
    try:
        print("Recognizing...")
        query = listener.recognize_google(input_speech, language="en-gb")
        print(query)
    except Exception as exception:
        print("I did not quite got that, can you repeat please...")
        speak("I did not quite got that, can you repeat please...")
        print(exception)
        return "None"
    return query


def search_wikipedia(query=""):
    search_results = wikipedia.search(query)
    if not search_results:
        print("No Wikipedia Articles")
        return "No result received"
    try:
        wiki_page = wikipedia.page(search_results[0])
    except wikipedia.DisambiguationError as error:
        wiki_page = wikipedia.page(error.options[0])
    print(wiki_page.title)
    wiki_summary = str(wiki_page.summary)
    return wiki_summary


def list_or_dict(var):
    if isinstance(var, list):
        return var[0]['plaintext']
    else:
        return  var['plaintext']


def search_wolframalpha(query=""):
    response = wolfram_client.query(query)

    # @success: Wolfram Alpha was able to resolve the query
    # @numpods: Number of results returned
    # pod: List of results. can contain sub pods
    if response["@success"] == 'false':
        return "Could not compute"
    else:
        result = ""
        # question
        pod0 = response['pod'][0]
        pod1 = response['pod'][1]

        # may contain the answer of has the highest confidence value
        # if it's primary, or has the title of result
        if('result' in pod1['@title'].lower()) or (pod1.get('@primary', 'false') == 'true') or ('definition' in pod1['@title'].lower()):
            # get result
            result = list_or_dict(pod1['subpod'])
            # remove brackets
            return result.split('(')[0]
        else:
            question = list_or_dict(pod0['subpod'])
            return question.split('(')[0]
            speak("Computation failed. Quering Universal databank.")
            return search_wikipedia(question)


if __name__ == '__main__':
    speak("All system activated.")

    while True:
        # Parse as a list
        query = parse_command().lower().split()

        if query[0] == activationWord:
            query.pop(0)

            # List Commands
            if query[0] == "say":
                if "hello" in query:
                    speak("Greeting, Sir.")
                else:
                    query.pop(0)  # Remove say
                    speech = " ".join(query)
                    speak(speech)

            # Navigation
            if query[0] == 'go' and query[1] == 'to':
                speak('Opening...')
                query = " ".join(query[2:])
                webbrowser.get("chrome").open_new(query)

            # wikipedia
            if query[0] == "wikipedia":
                query = " ".join(query[1:])
                speak("Querying the universal databank")
                speak(search_wikipedia(query))

            # wolframalpha
            if query[0] == "compute" or query[0] == "computer":
                query = " ".join(query[1:])
                speak("Computing")
                try:
                    result = search_wolframalpha(query)
                    speak(result)
                except:
                    speak("unable to compute")

            # note-taking
            if query[0] == 'log':
                speak("Ready to take your notes")
                new_note = parse_command().lower()
                now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                with open('note_%s.txt' % now, 'w') as new_file:
                    new_file.write(new_note)
                speak("Note written")

            if query[0] == 'exit':
                speak("Goodbye, Sir")
                break
