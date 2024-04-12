# this file has functions to transcribe, translate to eng, TTS functions which use user's openai api.

import openai
import streamlit as st
import pyaudio, wave
# from dotenv import loadenv, findenv

############################################################################
#       ALL FUNCTION DECLARATION
############################################################################

#---------------------------------------------------------------------------
#        Speech to Text
#---------------------------------------------------------------------------
def set_api_key():
    openai.api_key = st.session_state.user_api_key

#---------------------------------------------------------------------------
#        Speech to Text
#---------------------------------------------------------------------------
# hitting audio.transcriptions.create to transcribe audio and returning response
def transcribe_audio(audio, prompt='', language='ur'):
    '''This function takes binary audio object (compulsary), optional prompt as uncommon words like prompt = 'sentiment, fake' and optional language as ISO-1 language code like 'en', 'ur'. \nReturns transcription text is got successful and empty string if unsucessful.'''
    transcription = ''
    if st.session_state.user_api_key != '':
        try:
            response = openai.audio.transcriptions.create(
                model = 'whisper-1',
                file = audio,
                prompt = prompt,
                language = language
            )
            try:
                transcription = response.text
                return transcription
            except Exception as err:
                print('Failed extracting transcriptions. Error: ', err)
                return  response
        except Exception as err:
            return transcription
    else:
        st.error('Please enter a valid api key')
        return transcription

#---------------------------------------------------------------------------
#        Text to Speech
#---------------------------------------------------------------------------
# takes text and model name. If model not provided then uses tts-1 (model optimized for speed) to convert the text to speech and then saves the file. Gives relevant errors if occured any.
def convert_to_speech(text, model='tts-1', voice = 'alloy', filename = 'output-audio.mp3'):
    '''Takes 'text' as the input text needed to be converted to speech, 'model' as model name i.e. tts-1 or tts-1-hd, 'voice' as voice to be used i.e. alloy, echo, fable, onyx, nova, shimmer and 'filename' as file name for the output audio file with extension e.g. output-audio.mp3. Returns 1 if success and empty string if failed.'''
    result = ''

    if st.session_state.user_api_key != '':
        if (filename.endswith('.mp3')):
            # hitting audio.speech api to convert to speech and save
            try:
                print('Converting to speech...')
                response = openai.audio.speech.create(
                    model = model,        # the one optimized for speed
                    input = text,
                    voice = voice
                )
                print('Converted.')
                # saving the speech file (mp3)
                try:
                    response.stream_to_file(filename)
                    print('File saved as:', filename)
                    return response

                except Exception as err:
                    print(f'Failed saving speech as {filename}. Saved as output-audio.mp3 in the parent dir. Error:', err)
                    response.stream_to_file('output-audio.mp3')
                    print(response)
                    return 1

            except Exception as err:
                print('Failed converting to speech. Error:', err)
                return result
        
        else:
            print("File name doesn't ends with .mp3")
            return response
    
    else:
        # st.error('Please enter a valid api key.')
        return result

#---------------------------------------------------------------------------
#        Text Translations
#---------------------------------------------------------------------------
def translate_audio(audio, prompt = ''):
    '''This function takes in a binary audio file object, uses whisper-1 openai's model and translated the provided audio into English text and returns it. You can provide uncommon words with in the prompt parameter in the format of a string like 'weird, prompting'. Returns empty string if failed. '''
    result = ''
    if st.session_state.user_api_key != '':
        try:
            # hitting the api
            print('Translating the file...')
            response = openai.audio.translations.create(
                model = 'whisper-1',
                file = audio,
                prompt = prompt        
            )
            print('File translated.')

            try:
                translation = response.text
                return translation
            except:
                print("Failed extracting translation.")
                return response

        except Exception as err:
            print('Failed translating the file. Error:', err)
            return result
    else:
        st.error('Please enter a valid api key.')
        return result


# function to record audio using microphone
def record_using_mic(duration=5, filename='recorded-audio.wav'):
    audio = pyaudio.PyAudio()
    
    try:
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )

        frames = []
        try:
            # Calculate the number of iterations based on the desired duration
            num_iterations = int(44100 / 1024 * duration+1)     # added 1 as the audio getting recorded was a second less
            
            for i in range(num_iterations):
                data = stream.read(1024)
                frames.append(data)
        
        except KeyboardInterrupt:
            pass

        stream.stop_stream()
        stream.close()
        audio.terminate()

        sound_file = wave.open(filename, 'wb')
        sound_file.setnchannels(1)
        sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        sound_file.setframerate(44100)
        sound_file.writeframes(b''.join(frames))
        sound_file.close()

        return 0
    
    except Exception as err:
        return err
    
# function to enable/disable record_audio_stt button if audio_duration_input's value is changed
def desired_duration_changed():
    if st.session_state.desired_duration != 0:
        st.session_state.mic_stt_disabled = False
    else:
        st.session_state.mic_stt_disabled = True
        st.session_state.process_rec_stt_disabled = True


############################################################################
#       STREAMLIT APP
############################################################################
st.set_page_config(page_title='Speak Ease', page_icon=':microphone', layout = 'wide')
st.title(':microphone: Speak Ease')
st.caption('Convert your text to speech and translate it with ease.')
#######################################################
                # ADD USER API USAGE FUNCTIONALITY
#######################################################
st.text_input('Enter you openai api key', key = 'user_api_key')
st.divider()

# if the user entered his key in the key textbox, then setting it.
if st.session_state.user_api_key != '':
    set_api_key()

# creating three columns: one for speech to text, second for text to speech, third for audio translation to audio
stt_tab, tts_tab, audio_to_eng_tab = st.tabs([':memo: Speech To Text', ':headphones: Text To Speech', 'Convert audio to english.'])

with stt_tab:
    # st.subheader('Speech To Text')
    choose_file_col, record_audio_col = st.columns(2, gap = 'large')
    
    # if user choosed an audio file then transcribing it (on button click) and writting the transcription
    with choose_file_col:
        # adding buttons for uploading file and transcribing it
        uploaded_audio_for_stt = st.file_uploader('upload a file', label_visibility='hidden', accept_multiple_files = False, type = ['mp3', 'wav', 'm4a', 'mp4'], key = 'uploaded_audio_for_stt')

        # checking if the file is uploaded
        if uploaded_audio_for_stt is not None:

            process_stt_btn = st.button(label = 'Process Audio', type = 'primary')
            # if the process button is clicked then transcribing the file
            if process_stt_btn:
                # using progress bar to show the process. Printing error message if transcription got failed
                with st.spinner('Processing audio...'):
                    try:
                        audio_transcription = transcribe_audio(uploaded_audio_for_stt)
                        if audio_transcription != '':
                            st.write(f":blue[Transcription:]\
                                    \n{audio_transcription}")
                            
                        else:
                            st.write(f':red[Transcribing failed. Please try later. Error: ], {audio_transcription}')

                    except Exception as err:
                        audio_transcription = ''
                        st.error('Sorry. I an unable to transcribe the audio right now. Please try again')


    # if the uses chooses to record the file on the spot | doing effective use of session_state
    with record_audio_col:

        # variables for controlling button disability behaviour
        if 'mic_stt_disabled' not in st.session_state:
            st.session_state.mic_stt_disabled = True
        if 'recording_response' not in st.session_state:    # if the app is just launched, setting recording_response = 1
            st.session_state.recording_response = 1

        # delcaring the input fields
        st.number_input(label = 'Enter audio duration in seconds', min_value = 0, max_value = 120, key = 'desired_duration', on_change = desired_duration_changed)
        st.button('Record Audio', type = 'primary', key = 'mic_stt', disabled = st.session_state.mic_stt_disabled)
        st.button('Process Audio', type = 'primary', key = 'process_rec_stt')

        
        # if user wants to record the audio
        if ((st.session_state.mic_stt == True) and (st.session_state.desired_duration != 0)):        # checking if the value of the button is true | is clicked
            # adding recorded_file name in session storage to use it later for audio processing
            if 'recorded_filename' not in st.session_state:
                st.session_state.recorded_filename = 'recorded-audio.wav'

            with st.spinner(text = 'Recording now...'):
                try:
                    st.session_state.recording_response = record_using_mic(duration = st.session_state.desired_duration, filename = st.session_state.recorded_filename)

                    st.audio(data = open(st.session_state.recorded_filename, 'rb'), format = 'wav')

                except Exception as err:
                    st.error(f'I am having trouble recording the file right now. Please try later. Error: \
                             \n{err}')
        

        # if user wants to transcribe the recorded audio
        # checking if the proces_rec_stt button is clicked and the audio is recorded or not
        if ((st.session_state.process_rec_stt) and (st.session_state.recording_response == 0)):
            with st.spinner('Processing audio...'):
                try:
                    transcription = transcribe_audio(audio = open(st.session_state.recorded_filename, 'rb'))

                    # if transcription got successful then writting it and resetting the recording_response = 1 and rerunning script to disable the process audio button again
                    if transcription != '':     # shaukat made chages here
                        st.write(f'Transcription: \
                                 \n:blue[{transcription}]')
                        # resetting the recording_response variable and disabling the process_rec_stt button
                        st.session_state.recording_response = 1

                    else:
                        st.error('Sorry. The transcription is None. Please record first.')

                except:
                    st.error('Sorry. I am facing trouble converted audio to text right now. Please try later.')
    
        else :
            st.write(':red[Please record audio first.]')

    
# takes text from the text area and converts it to speech and makes it available to the user for downloading.
with tts_tab:
    text_area = st.text_area(label = 'Paste your text here and hit the button.', key = 'text_area')
    process_text_btn = st.button(label = 'Convert to Audio', type = 'primary', key = 'process_text_btn')
    text_to_convert = ''

    if st.session_state.text_area:
        text_to_convert = text_area
        # st.write(text_to_convert)     # the text area is getting 

    # if we have text is the textbox and the button is pressed then converting the text to speech saving the file and then reopening in binary mode, then reading it and displaying using the st.audio().
    if process_text_btn:
        if text_to_convert != '':
            with st.spinner('Converting to audio...'):
                try:
                    prepared_audio_name = 'converted-audio.mp3'
                    response = convert_to_speech(text = text_to_convert, filename = prepared_audio_name)

                     # if conversion got failed.
                    if response == '':
                        st.error('Please enter a valid api key.')

                    else:
                        try:
                            # Reading the file to present it to you...
                            converted_audio = open(prepared_audio_name, 'rb')
                            converted_audio.read()

                             # Displaying the file...
                            st.audio(converted_audio, format='mp3')
                            st.success('You can play the file now.')

                             # displaying download button to download the file. The page reloads itself after downloading and the audio vanishes
                            st.download_button(label = 'Download Audio', data = converted_audio, file_name = prepared_audio_name, mime = 'application/octet-steam', type = 'secondary')

                        except Exception as err:
                            st.write(f"Got unexpected error. Error: {err}")
                        
                except:
                    st.write('I am having trouble right now. Please try later.')
        else:
            st.error(f"Please enter some text first.")

# if the user uploads an audio file, then translating it and then asking him if we want to convert the text to speech and then he can download the translated speech.
with audio_to_eng_tab:
    file_for_translation = st.file_uploader(label = 'Choose audio file.', type = ['mp3', 'wav', 'm4a', 'aac'], key = 'file_for_translation')

    if file_for_translation is not None:   # if any file is selected
        translate_file_btn = st.button(label = ':headphones: Translate file')
        
        # if the translate_file_btn is pressed, then translating the file and then converting it to speech. After that making it available for download
        if translate_file_btn:
            with st.spinner(text = 'Translating file...'):
                
                try:
                    # Translating file
                    translation = translate_audio(audio = file_for_translation)
                    translated_speech_filename = 'translated-audio.mp3'

                    try:
                        # Converting to speech
                        speech = convert_to_speech(text = translation, filename = translated_speech_filename)
                        
                        # if we got the speech
                        if speech != '':
                            translated_file = open(translated_speech_filename, 'rb')
                            st.audio(data = translated_file, format = 'mp3')
                            st.download_button(label = 'Download file', data = translated_file, file_name = translated_speech_filename, mime = 'application/octet-stream')
                        
                        else:
                            st.error('Failed.')

                    except:
                        st.error('Error converting translation to audio')

                except:
                    st.error('Error translating file.')