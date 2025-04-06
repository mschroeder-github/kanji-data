from gtts import gTTS

def text_to_speech(text, mp3_filename, lang):
    tts = gTTS(text, lang=lang)
    tts.save(mp3_filename)




