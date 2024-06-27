import datetime
import os
import re

from src.audio_generation.generate_audio import generate_audio_gtts, generate_audio_mozilla_tts
from src.audio_generation.nose_processing import remove_background_noise


def main():
    # Predefined values
    text = re.sub(r'(?<=[.!?])(?=\S)', ' ', """Ah, you've caught me at a particularly draining moment. As an energy 
    vampire from the series ""What We Do in the Shadows,"" my essence thrives on the mundane, the tedious, 
    and the emotionally exhausting. Unlike my flashier, blood-drinking counterparts, my sustenance comes from the 
    everyday interactions that leave others feeling inexplicably weary and drained.

    Picture this: I walk into a room and initiate an endless conversation about the most banal topics. I might 
    recount, in excruciating detail, my latest trip to the grocery store, or perhaps I'll drown them into the finer 
    points of corporate jargon. My presence lingers, my voice monotone, drawing the very life force from those around 
    me. My powers are particularly potent in office environments, where meetings are my hunting grounds, 
    and small talk is my weapon of choice.
    
    Unlike traditional vampires, I don't need to avoid sunlight or sleep in coffins. My abilities are subtle but 
    effective, allowing me to blend seamlessly into modern society. While my victims might not realize what's happening 
    at first, they'll soon find themselves inexplicably tired, struggling to stay focused, and desperately seeking an 
    escape from my conversational clutches.
    
    You see, it's not about the blood. It's about boredom. My sustenance is their despair, their frustration, 
    their drained patience. So, the next time you find yourself yawning uncontrollably during a particularly dull chat, 
    beware—you might just be in the presence of an energy vampire.
    
    There was that one time where I was draining this fellow coworker. I stopped in front of the water-cooler while 
    he was getting some water. Stephen was his name. No, actually this was George. Stephen was the printer guy who 
    had started just a couple of weeks before that. I shared a water-cooler convo with him as well but that's neither 
    here nor there. You see, it's weird because why do they even hire ""printer guys"" anymore? Did this happen in 
    the 90s? They have a 90s show now, did you know? It's like the 70s show but about the 90s. Of course the lens 
    through which we are looking at now it's completely different...""")

    tts_choice = input("Enter 'g' for gTTS or 'm' for Mozilla TTS: ").strip().lower()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"../../output_{timestamp}"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if tts_choice == 'g':
        output_file_gtts = os.path.join(output_dir, f"output_audio_generation_gtts_{timestamp}.mp3")
        print("Generating audio using gTTS...")
        generate_audio_gtts(text, output_file=output_file_gtts, language='en')
        print(f"gTTS audio saved to {output_file_gtts}")

    elif tts_choice == 'm':
        model_name = input(
            "Enter the TTS model name for Mozilla TTS (default: tts_models/en/ljspeech/tacotron2-DCA): ") or "tts_models/en/ljspeech/tacotron2-DCA"
        output_file_mozilla_tts = os.path.join(output_dir, f"output_audio_generation_mozilla_tts_{timestamp}.wav")
        print("Generating audio using Mozilla TTS...")
        generate_audio_mozilla_tts(text, output_file=output_file_mozilla_tts, model_name=model_name)
        print(f"Mozilla TTS audio saved to {output_file_mozilla_tts}")
        remove_background_noise(output_file_mozilla_tts, output_file_mozilla_tts)

    else:
        print("Invalid choice. Please enter 'g' for gTTS or 'm' for Mozilla TTS.")


if __name__ == "__main__":
    main()
